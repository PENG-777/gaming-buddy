"""订单投诉管理（/biz/complaint 前缀, 管理端列表/处理/删除 + 用户端订单详情发起投诉）"""
# FastAPI: 路由/查询参数
from fastapi import APIRouter, Query

from core.common import split_ids  # 项目内: 删除接口 "1,2,3" 解析
from core.deps import CompanionScopeDep, DbDep, LoginUserDep, PageDep  # 项目内: 通用依赖(分页/登录校验/请求级 Session/陪玩师数据范围)
from core.response import ajax_error, ajax_success, page_data, to_ajax  # 项目内: 统一响应
from schemas.body import ComplaintBody  # 项目内: 订单投诉请求体
from services import complaint_service  # 项目内: 订单投诉业务层

# 投诉类型白名单(与用户端 COMPLAINT_TYPES 一致); 处理结果白名单(管理端处理弹窗下拉)
COMPLAINT_TYPES = ("服务态度差", "迟到未提供服务", "技术水平与描述不符", "诱导私下交易", "言语不当", "其他问题")
HANDLE_RESULTS = ("警告陪玩师", "全额退款", "驳回投诉", "其他")

router = APIRouter(prefix="/biz/complaint", tags=["complaint"])  # 模块路由器


@router.get("/selectComplaintList")
def select_complaint_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # 通用依赖: 分页参数/登录校验/Session
                          companion_scope: CompanionScopeDep,  # 陪玩师数据范围(陪玩师仅看针对自己的投诉)
                          orderNo: str | None = Query(None),  # 订单号模糊筛选(可选)
                          userName: str | None = Query(None),  # 投诉用户名模糊筛选(可选)
                          nickName: str | None = Query(None),  # 被投诉陪玩师昵称模糊筛选(可选)
                          complaintType: str | None = Query(None),  # 类型筛选(可选, 白名单六项)
                          status: int | None = Query(None)):  # 状态筛选(可选: 0待处理 1已处理)
    """管理端: 分页查询投诉列表(join 订单/下单用户/陪玩师; 陪玩师仅看针对自己的)

    参数: page 分页参数 / login_user 登录用户 / db 请求级 Session / companion_scope 陪玩师数据范围 /
          orderNo 订单号模糊(可选) / userName 用户名模糊(可选) / nickName 昵称模糊(可选) /
          complaintType 类型筛选(可选) / status 状态筛选(可选)
    """
    total, rows = complaint_service.select_complaint_page(
        db, page.pageNum, page.pageSize, orderNo, userName, nickName, complaintType, status,
        companion_id=companion_scope,  # 非 None 时仅查该陪玩师被投诉的记录
    )
    return page_data(rows, total)  # {total, rows, code, msg}


@router.put("/updateComplaint")
def update_complaint(body: ComplaintBody, login_user: LoginUserDep, db: DbDep,
                     companion_scope: CompanionScopeDep):
    """管理端: 处理投诉(置为已处理并记录结果/说明/时间; 全额退款联动取消订单并原路退回; 陪玩师只读无权处理)

    参数: body 投诉请求体(complaintId 定位/handleResult 结果/reply 说明) / login_user 登录用户 /
          db 请求级 Session / companion_scope 陪玩师数据范围(非 None 拒绝)
    """
    if companion_scope is not None:  # 陪玩师角色拦截(被投诉方不可处理)
        return ajax_error("陪玩师账号无权执行该操作")
    if body.complaintId is None:  # 缺少主键无法定位记录
        return ajax_error("参数错误: 缺少投诉ID")
    if not body.handleResult or body.handleResult not in HANDLE_RESULTS:  # 处理结果必选且在白名单内
        return ajax_error("请选择处理结果")
    if body.reply is not None and len(body.reply) > 500:  # 说明长度与表列宽一致
        return ajax_error("处理说明不能超过 500 字")
    err = complaint_service.handle_complaint(db, body)  # 事务内完成投诉/订单/钱包写入
    return ajax_success() if err is None else ajax_error(err)  # err 语义: None 成功 / 文案 失败


@router.delete("/deleteComplaintByComplaintIds/{complaintIds}")
def delete_complaint_by_complaint_ids(complaintIds: str, login_user: LoginUserDep, db: DbDep,
                                      companion_scope: CompanionScopeDep):
    """管理端: 批量删除投诉(路径参数逗号分隔; 陪玩师只读无权删除)

    参数: complaintIds 路径参数, 投诉ID串如 "1,2,3" / login_user 登录用户 / db 请求级 Session /
          companion_scope 陪玩师数据范围(非 None 拒绝)
    """
    if companion_scope is not None:  # 陪玩师角色拦截
        return ajax_error("陪玩师账号无权执行该操作")
    complaint_ids = split_ids(complaintIds)  # "1,2,3" -> [1, 2, 3]
    return to_ajax(complaint_service.delete_complaint_by_ids(db, complaint_ids))  # 按受影响行数返回


# ==================== 用户端 ====================

@router.post("/insertComplaint")
def insert_complaint(body: ComplaintBody, login_user: LoginUserDep, db: DbDep):
    """用户端: 发起投诉(订单详情页, 每单限一次, user_id 取自登录用户)

    参数: body 投诉请求体(orderNo/complaintType/content) / login_user 登录用户 / db 请求级 Session
    """
    if not body.orderNo:  # 订单号必填(按它定位订单)
        return ajax_error("参数错误: 缺少订单号")
    if not body.complaintType:  # 类型必填
        return ajax_error("请选择投诉类型")
    if body.complaintType not in COMPLAINT_TYPES:  # 类型必须在白名单内
        return ajax_error("投诉类型不合法")
    if not body.content or not body.content.strip():  # 内容必填
        return ajax_error("投诉内容不能为空")
    if len(body.content.strip()) > 200:  # 内容长度与表列宽一致
        return ajax_error("投诉内容不能超过 200 字")
    body.content = body.content.strip()  # 去除首尾空白后入库
    err, rows = complaint_service.insert_complaint(db, body, login_user.userId)  # 返回 (错误或 None, 受影响行数)
    return to_ajax(rows) if err is None else ajax_error(err)  # 按受影响行数返回
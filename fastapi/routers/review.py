"""订单评价管理（/biz/review 前缀, 管理端评价列表/回复/删除; 评价数据内嵌于订单表）"""
# FastAPI: 路由/查询参数
from fastapi import APIRouter, Query

from core.common import parse_dt, split_ids  # 项目内: 日期解析 / 删除接口 "1,2,3" 解析
from core.deps import CompanionScopeDep, DbDep, LoginUserDep, PageDep  # 项目内: 通用依赖(分页/登录校验/请求级 Session/陪玩师数据范围)
from core.response import ajax_error, ajax_success, ajax_success_data, page_data, to_ajax  # 项目内: 统一响应
from schemas.body import ReviewReplyBody  # 项目内: 评价回复请求体
from services import review_service  # 项目内: 评价业务层

router = APIRouter(prefix="/biz/review", tags=["review"])  # 模块路由器


@router.get("/selectReviewList")
def select_review_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # 通用依赖: 分页参数/登录校验/Session
                       companion_scope: CompanionScopeDep,  # 陪玩师数据范围(陪玩师仅看自己的评价)
                       orderNo: str | None = Query(None),  # 订单号模糊筛选(可选)
                       userName: str | None = Query(None),  # 评价用户名模糊筛选(可选)
                       nickName: str | None = Query(None),  # 陪玩师昵称模糊筛选(可选)
                       rating: int | None = Query(None, ge=1, le=5),  # 星级筛选(可选: 1-5)
                       beginTime: str | None = Query(None),  # 评价时间范围起(可选, 'yyyy-MM-dd HH:mm:ss')
                       endTime: str | None = Query(None)):  # 评价时间范围止(可选, 建议传 'yyyy-MM-dd 23:59:59' 含当天)
    """管理端: 分页查询评价列表(已评价订单, join user/companion; 陪玩师仅看自己的)

    参数: page 分页参数 / login_user 登录用户 / db 请求级 Session / companion_scope 陪玩师数据范围 /
          orderNo 订单号模糊(可选) / userName 用户名模糊(可选) / nickName 昵称模糊(可选) /
          rating 星级(可选) / beginTime/endTime 评价时间范围(可选)
    """
    total, rows = review_service.select_review_page(  # 日期字符串解析失败返回 None(条件自动失效)
        db, page.pageNum, page.pageSize, orderNo, userName, nickName, rating,
        parse_dt(beginTime), parse_dt(endTime), companion_id=companion_scope,
    )
    return page_data(rows, total)  # {total, rows, code, msg}


@router.get("/companionReviews/{companionId}")
def companion_reviews(companionId: int, login_user: LoginUserDep, db: DbDep):
    """用户端: 某陪玩师的全部真实评价(新在前, 供详情页评价列表/评分分布/标签统计)

    参数: companionId 路径参数, 陪玩师ID / login_user 登录用户 / db 请求级 Session
    """
    return ajax_success_data(review_service.select_companion_reviews(db, companionId))  # 评价列表(新在前)


@router.put("/updateReviewReply")
def update_review_reply(body: ReviewReplyBody, login_user: LoginUserDep, db: DbDep,
                        companion_scope: CompanionScopeDep):
    """管理端: 回复评价(已评价订单才可回复, 重复回复覆盖更新; 陪玩师只读无权回复)

    参数: body 回复请求体(orderId 定位/reply 回复内容) / login_user 登录用户 / db 请求级 Session /
          companion_scope 陪玩师数据范围(非 None 拒绝)
    """
    if companion_scope is not None:  # 陪玩师角色拦截(被评价方不可回复)
        return ajax_error("陪玩师账号无权执行该操作")
    if body.orderId is None:  # 管理端回复按订单ID定位
        return ajax_error("参数错误: 缺少订单ID")
    if not body.reply or not body.reply.strip():  # 回复内容必填
        return ajax_error("回复内容不能为空")
    body.reply = body.reply.strip()  # 去除首尾空白后入库
    err = review_service.reply_review(db, body)  # None 成功, 否则返回错误文案
    return ajax_success() if err is None else ajax_error(err)  # err 语义: None 成功 / 文案 失败


@router.delete("/deleteReviewByOrderIds/{orderIds}")
def delete_review_by_order_ids(orderIds: str, login_user: LoginUserDep, db: DbDep,
                               companion_scope: CompanionScopeDep):
    """管理端: 批量删除评价(路径参数逗号分隔; 清空评价字段, 订单保留; 陪玩师只读无权删除)

    参数: orderIds 路径参数, 订单ID串如 "1,2,3"(评价内嵌订单表, 按订单清评价) / login_user 登录用户 /
          db 请求级 Session / companion_scope 陪玩师数据范围(非 None 拒绝)
    """
    if companion_scope is not None:  # 陪玩师角色拦截
        return ajax_error("陪玩师账号无权执行该操作")
    return to_ajax(review_service.delete_review_by_ids(db, split_ids(orderIds)))  # 按受影响行数返回
"""打赏礼物管理（/biz/gift 前缀, 管理端增删改查 + 用户端启用礼物列表）"""
# FastAPI: 路由/查询参数
from fastapi import APIRouter, Query

from core.common import split_ids  # 项目内: 删除接口 "1,2,3" 解析
from core.deps import DbDep, LoginUserDep, PageDep  # 项目内: 通用依赖(分页/登录校验/请求级 Session)
from core.response import ajax_error, ajax_success, ajax_success_data, page_data, to_ajax  # 项目内: 统一响应
from schemas.body import GiftBody  # 项目内: 打赏礼物请求体
from services import gift_service  # 项目内: 打赏礼物业务层

router = APIRouter(prefix="/biz/gift", tags=["gift"])  # 模块路由器


@router.get("/selectGiftList")
def select_gift_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # 通用依赖: 分页参数/登录校验/Session
                     giftName: str | None = Query(None),  # 礼物名称模糊筛选(可选)
                     status: int | None = Query(None)):  # 状态筛选(可选: 0启用 1停用)
    """分页查询礼物列表(管理端)

    参数: page 分页参数 / login_user 登录用户 / db 请求级 Session / giftName 名称模糊(可选) / status 状态(可选)
    """
    total, rows = gift_service.select_gift_page(db, page.pageNum, page.pageSize, giftName, status)  # 业务层分页查询
    return page_data(rows, total)  # {total, rows, code, msg}


@router.get("/selectGiftByGiftId/{giftId}")
def select_gift_by_gift_id(giftId: int, login_user: LoginUserDep, db: DbDep):
    """按礼物ID查询礼物详情(管理端修改回显)

    参数: giftId 路径参数, 礼物ID / login_user 登录用户 / db 请求级 Session
    """
    gift = gift_service.get_gift_by_id(db, giftId)  # 按主键查询
    return ajax_success_data(gift) if gift is not None else ajax_success()  # 无数据时不输出 data 键


@router.post("/insertGift")
def insert_gift(body: GiftBody, login_user: LoginUserDep, db: DbDep):
    """新增礼物(管理端)

    参数: body 礼物请求体(名称/图片/价格/状态/排序) / login_user 登录用户 / db 请求级 Session
    """
    if not body.giftName:  # 礼物名称必填
        return ajax_error("礼物名称不能为空")
    if gift_service.name_exists(db, body.giftName):  # 名称查重
        return ajax_error("礼物名称已存在")
    return to_ajax(gift_service.insert_gift(db, body))  # 按受影响行数返回


@router.put("/updateGift")
def update_gift(body: GiftBody, login_user: LoginUserDep, db: DbDep):
    """修改礼物(管理端)

    参数: body 礼物请求体(giftId 必填定位记录, 仅非 null 字段更新) / login_user 登录用户 / db 请求级 Session
    """
    if body.giftId is None:  # 缺少主键无法定位记录
        return ajax_error("参数错误: 缺少礼物ID")
    if gift_service.name_exists(db, body.giftName, exclude_id=body.giftId):  # 传了名称才查重
        return ajax_error("礼物名称已存在")
    return to_ajax(gift_service.update_gift_by_id(db, body))  # 按受影响行数返回


@router.delete("/deleteGiftByIds/{giftIds}")
def delete_gift_by_ids(giftIds: str, login_user: LoginUserDep, db: DbDep):
    """批量删除礼物(管理端, 路径参数逗号分隔; 历史打赏记录存快照不受影响)

    参数: giftIds 路径参数, 礼物ID串如 "1,2,3" / login_user 登录用户 / db 请求级 Session
    """
    return to_ajax(gift_service.delete_gift_by_ids(db, split_ids(giftIds)))  # "1,2,3" -> 批量删除


# ==================== 用户端 ====================

@router.get("/selectEnabledGiftList")
def select_enabled_gift_list(login_user: LoginUserDep, db: DbDep):
    """启用礼物列表(用户端打赏弹窗, 含图片/价格, 按显示顺序)

    参数: login_user 登录用户 / db 请求级 Session
    """
    return ajax_success_data(gift_service.select_enabled_gifts(db))  # 启用礼物列表
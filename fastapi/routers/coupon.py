"""
优惠券管理 (/biz/coupon 前缀)
"""
from fastapi import APIRouter, Query

from core.common import split_ids  # 项目内: 删除接口 "1,2,3" 解析
from core.deps import DbDep, LoginUserDep, PageDep  # 项目内: 通用依赖(分页/登录校验/请求级 Session)
from core.response import ajax_error, ajax_success, ajax_success_data, page_data, to_ajax  # 项目内: 统一响应
from schemas.body import CouponBody
from services import coupon_service

router = APIRouter(prefix="/biz/coupon", tags=["coupon"])  # 模块路由器


@router.get("/selectCouponList")
def select_coupon_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # 通用依赖: 分页参数/登录校验/Session
                       couponName: str | None = Query(None),  # 优惠券名称模糊筛选(可选)
                       status: int | None = Query(None)):  # 状态筛选(可选)
    """分页查询优惠券列表"""
    total, rows = coupon_service.select_coupon_page(db, page.pageNum, page.pageSize, couponName, status)  # 业务层分页查询
    return page_data(rows, total)  # {total, rows, code, msg}


@router.get("/selectCouponByCouponId/{couponId}")
def select_coupon_by_coupon_id(couponId: int, login_user: LoginUserDep, db: DbDep):
    """
    按优惠券ID查询详情
    """
    coupon = coupon_service.get_coupon_by_id(db, couponId)  # 按主键查询
    return ajax_success_data(coupon) if coupon is not None else ajax_success()  # 无数据时不输出 data 键


@router.post("/insertCoupon")
def insert_coupon(body: CouponBody, login_user: LoginUserDep, db: DbDep):
    """
    新增优惠券
    """
    if not body.couponName:  # 如果优惠券名称为空
        return ajax_error("优惠券名称不能为空")
    if body.amount is None:
        return ajax_error("面额不能为空")
    if coupon_service.name_exists(db, body.couponName):  # 如果优惠券名已存在
        return ajax_error("优惠券名称已存在")
    return to_ajax(coupon_service.insert_coupon(db, body))  # 按受影响行数返回


@router.put("/updateCoupon")
def update_coupon(body: CouponBody, login_user: LoginUserDep, db: DbDep):
    """
    修改优惠券
    """
    if body.couponId is None:  # 如果该优惠券ID在数据库中不存在
        return ajax_error("优惠券ID不存在")
    if coupon_service.name_exists(db, body.couponName, exclude_id=body.couponId):  # 传了优惠券名称才查重
        return ajax_error("优惠券名称已存在")
    return to_ajax(coupon_service.update_coupon_by_id(db, body))  # 按受影响行数返回


@router.delete("/deleteCouponByCouponIds/{couponIds}")
def delete_coupon_by_coupon_ids(couponIds: str, login_user: LoginUserDep, db: DbDep):
    """
    批量删除优惠券
    """
    return to_ajax(coupon_service.delete_coupon_by_ids(db, split_ids(couponIds)))


@router.get("/selectUserCouponList")
def select_user_coupon_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # 通用依赖: 分页参数/登录校验/Session
                            userName: str | None = Query(None),  # 用户名模糊筛选(可选)
                            couponName: str | None = Query(None),  # 优惠券名称模糊筛选(可选)
                            status: int | None = Query(None)):  # 状态筛选(可选)
    """分页查询优惠券列表"""
    total, rows = coupon_service.select_user_coupon_page(db, page.pageNum, page.pageSize, userName, couponName,
                                                         status)  # 业务层分页查询
    return page_data(rows, total)  # {total, rows, code, msg}


# =============================== 用户端 ===============================

@router.get("/selectAvailableCouponList")
def select_available_coupon_list(login_user: LoginUserDep, db: DbDep):
    """
    领券中心使用: 查询可领取的优惠券(启用状态)
    """
    return ajax_success_data(coupon_service.select_available_coupons(db, login_user.userId))  # 可领取的优惠券列表


@router.post("/receiveCoupon/{couponId}")
def receive_coupon(couponId: int, login_user: LoginUserDep, db: DbDep):
    """
    领取优惠券
    """
    err = coupon_service.receive_coupon(db, login_user.userId, couponId)
    return ajax_success() if err is None else ajax_error(err)


@router.get("/selectMyCouponList")
def select_my_coupon_list(login_user: LoginUserDep, db: DbDep):
    """
    我的优惠券: 当前用户领取的优惠券列表
    """
    return ajax_success_data(coupon_service.select_my_coupons(db, login_user.userId))  # 用户个人的优惠券列表


@router.put("/useCoupon/{userCouponId}")
def use_coupon(userCouponId: int, login_user: LoginUserDep, db: DbDep):
    """
    核销优惠券(订单支付时调用): 本人 + 未使用 + 未过期的优惠券才可以核销
    """
    return to_ajax(coupon_service.use_coupon(db, login_user.userId, userCouponId))  # 按受影响行数返回


@router.put("/returnCoupon/{userCouponId}")
def return_coupon(userCouponId: int, login_user: LoginUserDep, db: DbDep):
    """
    返还优惠券(订单取消的时候退款时调用): 已使用的优惠券变回未使用的优惠券并且清空使用时间
    """
    return to_ajax(coupon_service.return_coupon(db, login_user.userId, userCouponId))  # 按受影响行数返回

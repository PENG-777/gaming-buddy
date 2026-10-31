"""陪玩订单管理（/biz/order 前缀, 管理端订单列表/开始服务/代取消/确认退款/删除 + 用户端下单全流程）"""
# 标准库: 日期算术(批量时段查询)
from datetime import date, timedelta

# FastAPI: 路由/查询参数
from fastapi import APIRouter, Query

from core.common import parse_dt, split_ids  # 项目内: 日期解析 / 删除接口 "1,2,3" 解析
from core.deps import CompanionScopeDep, DbDep, LoginUserDep, PageDep  # 项目内: 通用依赖(分页/登录校验/请求级 Session/陪玩师数据范围)
from core.response import ajax_error, ajax_success, ajax_success_data, page_data, to_ajax  # 项目内: 统一响应
from schemas.body import OrderCancelBody, OrderCreateBody, OrderPayBody, OrderReviewBody  # 项目内: 订单请求体
from services import order_service  # 项目内: 订单业务层

router = APIRouter(prefix="/biz/order", tags=["order"])  # 模块路由器


# ==================== 管理端 ====================

@router.get("/selectOrderList")
def select_order_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # 通用依赖: 分页参数/登录校验/Session
                      companion_scope: CompanionScopeDep,  # 陪玩师数据范围(陪玩师仅看自己的订单)
                      orderNo: str | None = Query(None),  # 订单号模糊筛选(可选)
                      userName: str | None = Query(None),  # 下单用户名模糊筛选(可选)
                      nickName: str | None = Query(None),  # 陪玩师昵称模糊筛选(可选)
                      status: str | None = Query(None),  # 状态筛选(可选: pending/booked/ongoing/completed/refunding/cancelled)
                      beginTime: str | None = Query(None),  # 下单时间范围起(可选, 'yyyy-MM-dd HH:mm:ss')
                      endTime: str | None = Query(None)):  # 下单时间范围止(可选, 建议传 'yyyy-MM-dd 23:59:59' 含当天)
    """管理端: 分页查询订单列表(join user/companion; 陪玩师仅看自己的)"""
    total, rows = order_service.select_order_page(  # 日期字符串解析失败返回 None(条件自动失效)
        db, page.pageNum, page.pageSize, orderNo, userName, nickName, status,
        parse_dt(beginTime), parse_dt(endTime), companion_id=companion_scope,
    )
    return page_data(rows, total)  # {total, rows, code, msg}


@router.put("/startOrder/{orderId}")
def start_order(orderId: int, login_user: LoginUserDep, db: DbDep,
                companion_scope: CompanionScopeDep):
    """开始服务(booked -> ongoing; 陪玩师仅能开始自己的订单, 管理员不限)

    参数: orderId 路径参数, 订单ID / login_user 登录用户 / db 请求级 Session / companion_scope 陪玩师数据范围(非 None 时限定仅自己的订单)
    """
    err = order_service.start_order(db, orderId, companion_id=companion_scope)  # None 成功, 否则返回错误文案
    return ajax_success() if err is None else ajax_error(err)  # err 语义: None 成功 / 文案 失败


@router.put("/cancelOrder")
def cancel_order(body: OrderCancelBody, login_user: LoginUserDep, db: DbDep,
                 companion_scope: CompanionScopeDep):
    """管理端: 代取消订单(pending 直接取消, booked 取消并退款; 陪玩师无权操作)

    参数: body 请求体(orderId 定位订单, cancelReason 可选取消原因) / login_user 登录用户 / db 请求级 Session / companion_scope 陪玩师数据范围
    """
    if companion_scope is not None:  # 陪玩师角色拦截
        return ajax_error("陪玩师账号无权执行该操作")
    if body.orderId is None:  # 管理端代取消按订单ID定位
        return ajax_error("参数错误: 缺少订单ID")
    err = order_service.cancel_order_admin(db, body.orderId, body.cancelReason)  # None 成功, 否则返回错误文案
    return ajax_success() if err is None else ajax_error(err)  # err 语义: None 成功 / 文案 失败


@router.put("/confirmRefund/{orderId}")
def confirm_refund(orderId: int, login_user: LoginUserDep, db: DbDep,
                   companion_scope: CompanionScopeDep):
    """管理端: 确认退款(refunding -> cancelled, 余额单退回+返还优惠券; 陪玩师无权操作)

    参数: orderId 路径参数, 订单ID / login_user 登录用户 / db 请求级 Session / companion_scope 陪玩师数据范围
    """
    if companion_scope is not None:  # 陪玩师角色拦截
        return ajax_error("陪玩师账号无权执行该操作")
    err = order_service.confirm_refund(db, orderId)  # None 成功, 否则返回错误文案
    return ajax_success() if err is None else ajax_error(err)  # err 语义: None 成功 / 文案 失败


@router.delete("/deleteOrderByOrderIds/{orderIds}")
def delete_order_by_order_ids(orderIds: str, login_user: LoginUserDep, db: DbDep,
                              companion_scope: CompanionScopeDep):
    """管理端: 批量删除订单(路径参数逗号分隔; 陪玩师无权操作)

    参数: orderIds 路径参数, 订单ID串如 "1,2,3" / login_user 登录用户 / db 请求级 Session / companion_scope 陪玩师数据范围
    """
    if companion_scope is not None:  # 陪玩师角色拦截
        return ajax_error("陪玩师账号无权执行该操作")
    return to_ajax(order_service.delete_order_by_ids(db, split_ids(orderIds)))  # "1,2,3" -> [1,2,3] 后批量删


# ==================== 用户端: 下单 / 支付 / 状态流转 ====================

@router.post("/create")
def create_order(body: OrderCreateBody, login_user: LoginUserDep, db: DbDep):
    """用户端: 创建订单(待支付), 价格/优惠以后端定价与校验为准

    参数: body 下单请求体(陪玩师/服务/日期/时段/时长/备注/优惠券) / login_user 登录用户 / db 请求级 Session
    """
    err, order_no = order_service.create_order(db, login_user.userId, body)  # 返回 (错误文案或 None, 订单号)
    return ajax_success(orderNo=order_no) if err is None else ajax_error(err)  # 成功携带订单号供跳转支付


@router.put("/pay")
def pay_order(body: OrderPayBody, login_user: LoginUserDep, db: DbDep):
    """用户端: 支付订单(余额支付事务扣款, 微信/支付宝模拟支付成功)

    参数: body 支付请求体(orderNo 订单号, payMethod 支付方式) / login_user 登录用户 / db 请求级 Session
    """
    if not body.orderNo or not body.payMethod:  # 订单号与支付方式必填
        return ajax_error("参数错误: 缺少订单号或支付方式")
    err, balance_after = order_service.pay_order(db, login_user.userId, body.orderNo, body.payMethod)  # 返回 (错误或 None, 支付后余额)
    return ajax_success(balance=balance_after) if err is None else ajax_error(err)  # 成功携带最新余额


@router.put("/cancel")
def cancel_order(body: OrderCancelBody, login_user: LoginUserDep, db: DbDep):
    """用户端: 取消订单(待支付直接取消, 已支付进入退款审核)

    参数: body 取消请求体(orderNo 订单号, cancelReason 可选原因) / login_user 登录用户 / db 请求级 Session
    """
    if not body.orderNo:  # 用户端取消按订单号定位
        return ajax_error("参数错误: 缺少订单号")
    err = order_service.cancel_order(db, login_user.userId, body.orderNo, body.cancelReason)  # 仅限本人订单
    return ajax_success() if err is None else ajax_error(err)  # err 语义: None 成功 / 文案 失败


@router.put("/finish/{orderNo}")
def finish_order(orderNo: str, login_user: LoginUserDep, db: DbDep):
    """用户端: 确认完成(ongoing -> completed)

    参数: orderNo 路径参数, 订单号 / login_user 登录用户 / db 请求级 Session
    """
    err = order_service.finish_order(db, login_user.userId, orderNo)  # 仅限本人订单
    return ajax_success() if err is None else ajax_error(err)  # err 语义: None 成功 / 文案 失败


@router.put("/review")
def review_order(body: OrderReviewBody, login_user: LoginUserDep, db: DbDep):
    """用户端: 评价订单(completed 且未评价, 每单仅一次)

    参数: body 评价请求体(orderNo/星级/标签/内容) / login_user 登录用户 / db 请求级 Session
    """
    err = order_service.review_order(db, login_user.userId, body)  # 仅限本人订单
    return ajax_success() if err is None else ajax_error(err)  # err 语义: None 成功 / 文案 失败


# ==================== 用户端: 查询 ====================

@router.get("/my")
def select_my_orders(page: PageDep, login_user: LoginUserDep, db: DbDep,  # 通用依赖: 分页参数/登录校验/Session
                     status: str | None = Query(None)):  # 状态筛选(可选, Tab 切换)
    """用户端: 分页查询我的订单

    参数: page 分页参数 / login_user 登录用户 / db 请求级 Session / status 状态筛选(可选)
    """
    total, rows = order_service.select_my_orders(db, login_user.userId, status, page.pageNum, page.pageSize)
    return page_data(rows, total)  # {total, rows, code, msg}


@router.get("/my/counters")
def my_order_counters(login_user: LoginUserDep, db: DbDep):
    """用户端: 我的订单各状态计数(供 Tab 角标/个人中心)

    参数: login_user 登录用户 / db 请求级 Session
    """
    return ajax_success_data(order_service.count_my_orders(db, login_user.userId))  # {状态码: 数量}


@router.get("/my/reviews")
def my_reviews(login_user: LoginUserDep, db: DbDep):
    """用户端: 我发出的评价(已评价订单列表)

    参数: login_user 登录用户 / db 请求级 Session
    """
    return ajax_success_data(order_service.select_my_reviews(db, login_user.userId))  # 评价字典列表


@router.get("/my/{orderNo}")
def get_my_order(orderNo: str, login_user: LoginUserDep, db: DbDep):
    """用户端: 按订单号查询我的订单详情(仅本人可见)

    参数: orderNo 路径参数, 订单号 / login_user 登录用户 / db 请求级 Session
    """
    order = order_service.get_my_order(db, login_user.userId, orderNo)  # 非本人/不存在均返回 None
    return ajax_success_data(order) if order is not None else ajax_error("订单不存在")  # 详情字典


@router.get("/slots")
def occupied_slots(login_user: LoginUserDep, db: DbDep,
                   companionId: int = Query(...),  # 陪玩师ID(必填)
                   date: str = Query(...)):  # 服务日期(必填, 'yyyy-MM-dd')
    """用户端: 某陪玩师某天的已占用开始时段(pending/booked/ongoing 订单)

    参数: login_user 登录用户 / db 请求级 Session / companionId 陪玩师ID / service_date 服务日期
    """
    service_date = order_service._parse_date(date)  # 解析失败返回 None
    if service_date is None:
        return ajax_error("日期格式错误")
    return ajax_success_data(order_service.occupied_hours(db, companionId, service_date))  # 已占用小时列表如 [10, 14]


@router.get("/slotsBatch")
def occupied_slots_batch(login_user: LoginUserDep, db: DbDep,
                         companionId: int = Query(...),  # 陪玩师ID(必填)
                         days: int = Query(7, ge=1, le=31)):  # 天数(可选, 含今天, 默认 7 天)
    """用户端: 某陪玩师未来 days 天每天已占用时段字典 {'yyyy-MM-dd': [时, ...]}(详情页时间表)

    参数: login_user 登录用户 / db 请求级 Session / companionId 陪玩师ID / days 天数(含今天)
    """
    begin = date.today()  # 从今天起
    end = begin + timedelta(days=days - 1)  # 到第 days 天(含首尾)
    return ajax_success_data(order_service.occupied_hours_range(db, companionId, begin, end))  # 日期 -> 已占小时列表
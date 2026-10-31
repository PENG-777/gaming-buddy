"""
陪玩订单业务层

companion_order(陪玩订单) 模块:
- 管理端: 分页列表(join user/companion)、开始服务、代取消、确认退款、批量删除
- 用户端: 下单/支付/取消/确认完成/评价事务 + 我的订单/详情/状态计数/我的评价/时段占用查询

订单状态机: pending 待支付 -> booked 待开始(由管理端开始服务) -> ongoing 进行中 -> completed 已完成(可评价一次)
             pending/booked 可取消; 用户取消已支付订单 -> refunding(退款中, 由管理端确认退款)
             终态: completed / cancelled
支付与退款: 余额支付扣款/退款入账 + wallet_transaction 流水 + user_coupon 核销/返还
             均在订单事务内完成(参照 reward_service.send_reward, 不复用 wallet_service.do_change)
"""
import random  # 标准库: 随机数(订单号尾号)
from datetime import date, datetime  # 标准库: 日期/日期时间类型

from sqlalchemy import func, select, update  # 第三方: SQLAlchemy 列表达式
from sqlalchemy.orm import Session  # 第三方: 会话类型标注

from core.common import (  # 项目内: 泛型工具
    between_if, delete_by_pks, eq_if, like_if, paginate, parse_dt, row_to_dict, where_if,
)
from models.entities import (  # 项目内: 订单相关 ORM 实体
    Companion, CompanionOrder, CompanionService, Complaint, Coupon, ServiceItem, User, UserCoupon, WalletTransaction,
)
from schemas.body import OrderCreateBody, OrderReviewBody  # 项目内: 下单/评价请求体

# 订单活跃状态(占用时段/不可删除)
ACTIVE_STATUS = ("pending", "booked", "ongoing")
# 全部状态(状态计数/下拉)
ALL_STATUS = ("pending", "booked", "ongoing", "completed", "refunding", "cancelled")

# 管理端/用户端通用查询列(join user 取下单用户名, join companion 取陪玩师昵称/头像, 转换键一一对应)
_ORDER_COLS = (
    CompanionOrder.order_id, CompanionOrder.order_no, CompanionOrder.user_id, User.user_name,
    CompanionOrder.companion_id, Companion.nick_name, Companion.avatar,
    CompanionOrder.service_id, CompanionOrder.service_name, CompanionOrder.price, CompanionOrder.hours,
    CompanionOrder.service_date, CompanionOrder.start_hour, CompanionOrder.note,
    CompanionOrder.user_coupon_id, CompanionOrder.coupon_name, CompanionOrder.coupon_amount,
    CompanionOrder.gross_amount, CompanionOrder.amount, CompanionOrder.pay_method, CompanionOrder.status,
    CompanionOrder.pay_time, CompanionOrder.start_time, CompanionOrder.end_time, CompanionOrder.cancel_reason,
    CompanionOrder.review_rating, CompanionOrder.review_tags, CompanionOrder.review_content,
    CompanionOrder.review_time, CompanionOrder.review_reply, CompanionOrder.review_reply_time,
    CompanionOrder.create_time,
)


def _order_row_to_dict(row) -> dict:
    """数据库行 -> camelCase 字典(service_date 补格式化为 'yyyy-MM-dd' 字符串)

    参数: row select 列表达式查询行; row_to_dict 只处理 datetime, date 类型在此补格式化
    """
    d = row_to_dict(row)  # datetime 已由 row_to_dict 统一格式化
    if d.get("serviceDate") is not None:  # date 类型 row_to_dict 不处理, 这里补格式化
        d["serviceDate"] = str(d["serviceDate"])  # date -> 'yyyy-MM-dd' 字符串
    return d


def _base_query():
    """订单基础查询(join user/companion)

    无参数; 返回带用户名/陪玩师昵称头像的订单基础语句(调用方再拼 where/order)。
    """
    stmt = select(*_ORDER_COLS).select_from(CompanionOrder)  # 显式指定主表
    stmt = stmt.join(User, CompanionOrder.user_id == User.user_id)  # 内连接用户(取用户名)
    stmt = stmt.join(Companion, CompanionOrder.companion_id == Companion.companion_id)  # 内连接陪玩师(取昵称/头像)
    return stmt


# ==================== 管理端查询/删除 ====================

def select_order_page(db: Session, page_num: int, page_size: int,
                      order_no: str | None = None, user_name: str | None = None,
                      nick_name: str | None = None, status: str | None = None,
                      begin_time: datetime | None = None, end_time: datetime | None = None,
                      companion_id: int | None = None) -> tuple[int, list[dict]]:
    """管理端: 分页查询订单列表(join user/companion; companion_id 非空时仅看该陪玩师)

    参数: db 请求级 Session / page_num 页码 / page_size 每页条数 / order_no 订单号模糊(可选) /
          user_name 用户名模糊(可选) / nick_name 昵称模糊(可选) / status 状态(可选) /
          begin_time/end_time 下单时间范围(可选) / companion_id 陪玩师数据范围(可选)
    """
    stmt = _base_query()
    stmt = where_if(  # 拼接动态条件(值非空才生成)
        stmt,
        like_if(CompanionOrder.order_no, order_no),
        like_if(User.user_name, user_name),
        like_if(Companion.nick_name, nick_name),
        eq_if(CompanionOrder.status, status),
        between_if(CompanionOrder.create_time, begin_time, end_time),
        eq_if(CompanionOrder.companion_id, companion_id),  # 陪玩师数据范围(仅看自己)
    )
    stmt = stmt.order_by(CompanionOrder.order_id.desc())  # 按订单ID倒序(最新订单在前)
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [_order_row_to_dict(r) for r in rows]


def delete_order_by_ids(db: Session, order_ids: list[int]) -> int:
    """管理端: 批量删除订单

    参数: db 请求级 Session / order_ids 订单ID列表; 返回受影响行数(活跃订单由路由层拦截, 这里不重复校验)
    """
    return delete_by_pks(db, CompanionOrder, CompanionOrder.order_id, order_ids)  # 泛型按主键批量删除


# ==================== 用户端查询 ====================

def select_my_orders(db: Session, user_id: int, status: str | None,
                     page_num: int, page_size: int) -> tuple[int, list[dict]]:
    """用户端: 分页查询我的订单(status 为空查全部)

    参数: db 请求级 Session / user_id 用户ID(仅本人订单) / status 状态筛选(可选) /
          page_num 页码 / page_size 每页条数
    """
    stmt = _base_query().where(CompanionOrder.user_id == user_id)  # 仅本人订单
    stmt = where_if(stmt, eq_if(CompanionOrder.status, status))  # 状态筛选(Tab)
    stmt = stmt.order_by(CompanionOrder.order_id.desc())  # 新单在前
    total, rows = paginate(db, stmt, page_num, page_size)
    return total, [_order_row_to_dict(r) for r in rows]


def get_my_order(db: Session, user_id: int, order_no: str) -> dict | None:
    """用户端: 按订单号查询我的订单详情(仅本人可见, 附带该订单的投诉信息)

    参数: db 请求级 Session / user_id 用户ID(归属校验) / order_no 订单号; 非本人/不存在返回 None
    """
    row = db.execute(
        _base_query().where(CompanionOrder.user_id == user_id, CompanionOrder.order_no == order_no)
    ).first()  # 归属 + 订单号双条件
    if row is None:
        return None  # 不存在或不属于本人
    order = _order_row_to_dict(row)  # 订单主体字典
    complaint = db.execute(  # 附带投诉信息(每单限一条, 字段加前缀避免与订单字段冲突)
        select(
            Complaint.complaint_id, Complaint.complaint_type, Complaint.status,
            Complaint.handle_result, Complaint.reply, Complaint.handle_time, Complaint.create_time,
        ).where(Complaint.order_id == order["orderId"])
    ).first()
    if complaint is not None:
        c = row_to_dict(complaint)  # datetime 已统一格式化
        order.update({  # 投诉字段并入订单详情(加 complaint/handle 前缀区分)
            "complaintId": c["complaintId"],
            "complaintType": c["complaintType"],
            "complaintStatus": c["status"],
            "handleResult": c["handleResult"],
            "complaintReply": c["reply"],
            "handleTime": c["handleTime"],
            "complaintTime": c["createTime"],
        })
    return order  # 详情字典(含可选投诉段)


def count_my_orders(db: Session, user_id: int) -> dict:
    """用户端: 我的订单各状态计数(无订单的状态计 0, 附 all 总数)

    参数: db 请求级 Session / user_id 用户ID; 返回 {状态码: 数量, "all": 总数}
    """
    rows = db.execute(  # 按状态分组计数
        select(CompanionOrder.status, func.count())
        .where(CompanionOrder.user_id == user_id)
        .group_by(CompanionOrder.status)
    ).all()
    counters = {s: 0 for s in ALL_STATUS}  # 先置 0, 保证前端取任意状态都有值
    total = 0  # 全状态合计
    for status, cnt in rows:
        counters[status] = cnt  # 回填实际计数
        total += cnt
    counters["all"] = total  # 附总数键
    return counters


def select_my_reviews(db: Session, user_id: int) -> list[dict]:
    """用户端: 我发出的评价(已评价订单 -> 评价视图, 新评价在前)

    参数: db 请求级 Session / user_id 用户ID(仅本人评价)
    """
    stmt = (
        select(
            CompanionOrder.order_id, CompanionOrder.order_no,
            CompanionOrder.companion_id, Companion.nick_name, CompanionOrder.service_name,
            CompanionOrder.review_rating, CompanionOrder.review_tags,
            CompanionOrder.review_content, CompanionOrder.review_time, CompanionOrder.review_reply,
        )  # 评价视图所需列(订单评价字段 + 陪玩师昵称)
        .select_from(CompanionOrder)
        .join(Companion, CompanionOrder.companion_id == Companion.companion_id)  # 关联陪玩师取昵称
        .where(CompanionOrder.user_id == user_id, CompanionOrder.review_rating.is_not(None))  # 仅本人已评价订单
        .order_by(CompanionOrder.review_time.desc())  # 新评价在前
    )
    rows = db.execute(stmt).all()
    return [
        {  # 评价视图字段对齐原 mock 结构(rating/tags/content/time)
            "id": r.order_id, "orderId": r.order_no, "companionId": r.companion_id,
            "companionName": r.nick_name, "serviceName": r.service_name,
            "rating": r.review_rating, "tags": (r.review_tags or "").split(",") if r.review_tags else [],  # 逗号分隔标签转数组
            "content": r.review_content or "", "time": row_to_dict(r).get("reviewTime"),  # 复用行转换取格式化时间
            "reply": r.review_reply or "",
        }
        for r in rows
    ]


def occupied_hours(db: Session, companion_id: int, service_date: date) -> list[int]:
    """某陪玩师某天的已占用开始时段(pending/booked/ongoing 订单)

    参数: db 请求级 Session / companion_id 陪玩师ID / service_date 服务日期; 返回升序小时列表如 [10, 14]
    """
    rows = db.execute(
        select(CompanionOrder.start_hour).where(
            CompanionOrder.companion_id == companion_id,
            CompanionOrder.service_date == service_date,  # 指定日期
            CompanionOrder.status.in_(ACTIVE_STATUS),  # 仅活跃订单占用时段
        )
    ).scalars().all()
    return sorted(rows)  # 升序排列(前端逐格标灰)


def occupied_hours_range(db: Session, companion_id: int, begin_date: date, end_date: date) -> dict[str, list[int]]:
    """某陪玩师日期范围内每天已占用开始时段(pending/booked/ongoing 订单), 供详情页时间表

    参数: db 请求级 Session / companion_id 陪玩师ID / begin_date 起始日期(含) / end_date 结束日期(含);
          返回 {'yyyy-MM-dd': [时, ...]}
    """
    rows = db.execute(
        select(CompanionOrder.service_date, CompanionOrder.start_hour).where(
            CompanionOrder.companion_id == companion_id,
            CompanionOrder.service_date.between(begin_date, end_date),  # 闭区间范围
            CompanionOrder.status.in_(ACTIVE_STATUS),  # 仅活跃订单占用时段
        )
    ).all()
    result: dict[str, list[int]] = {}  # 日期 -> 时段列表
    for r in rows:  # 按日期分组收集时段
        result.setdefault(str(r.service_date), []).append(r.start_hour)
    return {d: sorted(hs) for d, hs in result.items()}  # 每天时段升序


# ==================== 用户端下单/支付事务 ====================

def gen_order_no() -> str:
    """生成订单号: GB + yyyyMMddHHmmss + 3 位随机(唯一性由 uk_order_no 兜底)

    无参数; 形如 GB20260101120000123。
    """
    return f"GB{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100, 999)}"  # 时间戳+随机尾号, 撞号由唯一索引兜底


def create_order(db: Session, user_id: int, body: OrderCreateBody) -> tuple[str | None, str | None]:
    """用户端下单核心事务: 校验陪玩师/服务/时段/优惠券 -> 写订单(pending), 一次性提交

    价格以 companion_service 定价为准(防篡改); 服务名/单价/券名存快照。
    参数: db 请求级 Session / user_id 下单用户 / body 下单请求体。
    返回 (None, order_no) 成功; (错误信息, None) 失败。
    """
    if not body.companionId or not body.serviceId or not body.date or not body.startHour or not body.hours:
        return "参数错误: 请完整选择服务/日期/时段/时长", None  # 必填项缺失
    service_date = _parse_date(body.date)  # 'yyyy-MM-dd' -> date
    if service_date is None:
        return "服务日期格式错误", None
    if service_date < date.today():  # 不允许约过去的日期
        return "服务日期不能早于今天", None
    if body.startHour + body.hours > 24:  # 服务结束时间超出当天
        return "服务结束时间超出当天, 请减少时长", None
    companion = db.execute(  # 陪玩师存在且启用才可下单
        select(Companion.companion_id).where(
            Companion.companion_id == body.companionId, Companion.status == 0
        )
    ).first()
    if companion is None:
        return "陪玩师不存在或已停用", None
    svc = db.execute(  # 服务以 companion_service 定价为准(join service_item 取名称快照)
        select(CompanionService.price, ServiceItem.service_name)
        .join(ServiceItem, CompanionService.service_id == ServiceItem.service_id)
        .where(CompanionService.companion_id == body.companionId,
               CompanionService.service_id == body.serviceId)
    ).first()
    if svc is None:
        return "该陪玩师未开通此服务", None
    occupied = db.scalar(  # 同陪玩师同日同时段已有活跃订单则拒绝(防超卖)
        select(CompanionOrder.order_id).where(
            CompanionOrder.companion_id == body.companionId,
            CompanionOrder.service_date == service_date,
            CompanionOrder.start_hour == body.startHour,
            CompanionOrder.status.in_(ACTIVE_STATUS),
        )
    )
    if occupied is not None:
        return "该时段已被预约, 请更换时段", None
    gross = svc.price * body.hours  # 订单原价(后端定价计算)
    user_coupon_id, coupon_name, coupon_amount = None, None, 0  # 券相关快照(默认不用券)
    if body.userCouponId is not None:  # 用券下单: 校验归属/未使用/未过期/满门槛
        coupon = db.execute(
            select(UserCoupon.expire_time, UserCoupon.status, Coupon.coupon_name, Coupon.threshold, Coupon.amount)
            .join(Coupon, UserCoupon.coupon_id == Coupon.coupon_id)  # 关联券表取名称/门槛/面额
            .where(UserCoupon.id == body.userCouponId, UserCoupon.user_id == user_id)  # 归属校验
        ).first()
        if coupon is None:
            return "优惠券不存在", None  # 非本人券或不存在的记录
        if coupon.status == 1:
            return "优惠券已使用", None
        if coupon.expire_time is None or coupon.expire_time.date() < date.today():
            return "优惠券已过期", None  # 无过期时间视为已过期
        if gross < coupon.threshold:
            return f"订单金额未满足该券满 {coupon.threshold} 元门槛", None  # 满减门槛校验
        user_coupon_id, coupon_name = body.userCouponId, coupon.coupon_name  # 记录用券快照
        coupon_amount = min(coupon.amount, gross)  # 抵扣额不超过原价
    order_no = gen_order_no()  # 生成唯一订单号
    db.add(CompanionOrder(  # 写入订单(快照字段以后端查询为准)
        order_no=order_no, user_id=user_id, companion_id=body.companionId, service_id=body.serviceId,
        service_name=svc.service_name, price=svc.price, hours=body.hours,
        service_date=service_date, start_hour=body.startHour, note=body.note or None,
        user_coupon_id=user_coupon_id, coupon_name=coupon_name, coupon_amount=coupon_amount,
        gross_amount=gross, amount=max(0, gross - coupon_amount),  # 实付 = 原价 - 抵扣(下限 0)
        status="pending", create_time=datetime.now(),  # 新单一律待支付
    ))
    db.commit()  # 下单为单表写入, 一次性提交
    return None, order_no  # 成功返回订单号


def pay_order(db: Session, user_id: int, order_no: str, pay_method: str) -> tuple[str | None, int | None]:
    """用户端支付核心事务: 校验订单/支付方式 -> 余额扣款+流水 -> 核销优惠券 -> 置 booked, 一次性提交

    参数: db 请求级 Session / user_id 支付用户 / order_no 订单号 / pay_method 支付方式(balance/wechat/alipay)。
    返回 (None, 变动后余额) 成功; (错误信息, None) 失败。wechat/alipay 为模拟支付(直接成功)。
    """
    if pay_method not in ("balance", "wechat", "alipay"):
        return "不支持的支付方式", None  # 支付方式白名单
    order = db.scalar(  # 待支付的本人订单才可支付
        select(CompanionOrder).where(
            CompanionOrder.order_no == order_no, CompanionOrder.user_id == user_id
        )
    )
    if order is None:
        return "订单不存在", None  # 非本人或不存在
    if order.status != "pending":
        return "订单状态已变化, 请刷新", None  # 仅待支付可付
    balance_after = None  # 模拟支付时保持 None(未动余额)
    if pay_method == "balance":  # 余额支付: 事务内校验余额并扣款
        balance = db.scalar(select(User.balance).where(User.user_id == user_id))
        if balance is None:
            return "用户不存在", None
        if balance < order.amount:
            return "余额不足, 请先充值", None
        balance_after = balance - order.amount  # 扣款后余额
        db.execute(update(User).where(User.user_id == user_id).values(balance=balance_after))  # 扣减余额
        db.add(WalletTransaction(  # 消费流水(与钱包模块对账)
            user_id=user_id, type="consume", amount=-order.amount,  # 支出为负数
            balance_after=balance_after, note=f"支付订单 {order.order_no}", create_time=datetime.now(),
        ))
    if order.user_coupon_id is not None:  # 核销优惠券(归属+未使用+未过期条件更新, 0 行说明券已失效)
        result = db.execute(
            update(UserCoupon)
            .where(UserCoupon.id == order.user_coupon_id, UserCoupon.user_id == user_id,
                   UserCoupon.status == 0, UserCoupon.expire_time >= func.now())  # 条件更新防并发重复核销
            .values(status=1, use_time=func.now())
        )
        if result.rowcount == 0:
            db.rollback()  # 回滚已执行的余额扣款, 保证事务原子性
            return "优惠券状态已变化, 请重新下单", None
    order.pay_method = pay_method  # 置为待开始 + 记录支付方式/时间
    order.pay_time = datetime.now()
    order.status = "booked"  # 支付成功 -> 待开始
    db.commit()  # 多表写操作: 同一事务内完成后一次性提交
    return None, balance_after  # 成功返回扣款后余额


# ==================== 用户端状态流转 ====================

def cancel_order(db: Session, user_id: int, order_no: str, reason: str | None) -> str | None:
    """用户端取消订单: pending -> cancelled / booked -> refunding(待管理端确认退款), 写取消原因

    参数: db 请求级 Session / user_id 用户ID(归属校验) / order_no 订单号 / reason 取消原因(可选);
    返回 None 成功 / 错误文案 失败
    """
    order = db.scalar(
        select(CompanionOrder).where(CompanionOrder.order_no == order_no, CompanionOrder.user_id == user_id)
    )
    if order is None:
        return "订单不存在"
    if order.status == "pending":  # 未支付直接取消
        order.status = "cancelled"
    elif order.status == "booked":  # 已支付进入退款审核
        order.status = "refunding"  # 退款由管理端确认后才入账
    else:
        return "当前状态不可取消"  # ongoing/completed 等不可取消
    order.cancel_reason = (reason or "").strip() or None  # 记录取消原因(可空)
    db.commit()  # 单表状态更新
    return None


def finish_order(db: Session, user_id: int, order_no: str) -> str | None:
    """用户端确认完成: ongoing -> completed

    参数: db 请求级 Session / user_id 用户ID(归属校验) / order_no 订单号; 返回 None 成功 / 错误文案 失败
    """
    order = db.scalar(
        select(CompanionOrder).where(CompanionOrder.order_no == order_no, CompanionOrder.user_id == user_id)
    )
    if order is None:
        return "订单不存在"
    if order.status != "ongoing":
        return "当前状态不可完成"  # 仅进行中可确认完成
    order.status = "completed"  # 置终态
    order.end_time = datetime.now()  # 记录服务完成时间
    db.commit()  # 单表状态更新
    return None


def review_order(db: Session, user_id: int, body: OrderReviewBody) -> str | None:
    """用户端评价: completed 且未评价才可评价(每单仅一次)

    参数: db 请求级 Session / user_id 用户ID(归属校验) / body 评价请求体(订单号/星级/标签/内容);
    返回 None 成功 / 错误文案 失败
    """
    if not body.orderNo or not body.rating:
        return "参数错误: 缺少订单号或星级"  # 必填项校验
    order = db.scalar(
        select(CompanionOrder).where(CompanionOrder.order_no == body.orderNo, CompanionOrder.user_id == user_id)
    )
    if order is None:
        return "订单不存在"
    if order.status != "completed":
        return "当前状态不可评价"  # 仅已完成可评价
    if order.review_rating is not None:
        return "该订单已评价过"  # 每单仅一次
    order.review_rating = body.rating  # 星级 1-5
    order.review_tags = body.tags or None  # 标签(可空)
    order.review_content = (body.content or "").strip() or None  # 内容(去空白, 可空)
    order.review_time = datetime.now()  # 评价时间
    db.commit()  # 单表写入
    return None


# ==================== 管理端开始服务/取消/退款 ====================

def start_order(db: Session, order_id: int, companion_id: int | None = None) -> str | None:
    """开始服务: booked -> ongoing(companion_id 非空时校验订单归属, 陪玩师仅能开始自己的订单)

    参数: db 请求级 Session / order_id 订单ID / companion_id 陪玩师数据范围(管理员传 None 不限);
    返回 None 成功 / 错误文案 失败
    """
    order = db.scalar(select(CompanionOrder).where(CompanionOrder.order_id == order_id))
    if order is None:
        return "订单不存在"
    if companion_id is not None and order.companion_id != companion_id:  # 陪玩师数据范围校验
        return "该订单不属于您, 无法开始服务"
    if order.status != "booked":
        return "当前状态不可开始"  # 仅待开始可开始服务
    order.status = "ongoing"  # 置进行中
    order.start_time = datetime.now()  # 记录实际开始时间
    db.commit()  # 单表状态更新
    return None


def refund_paid_order(db: Session, order: CompanionOrder):
    """已支付订单退款共通: 余额支付退回余额+写退款流水; 使用过的优惠券返还(未使用条件幂等)

    公开供投诉全额退款复用; 不含 commit, 调用方须在同一事务内一次性提交。

    参数: db 会话 / order 已支付订单实体(pay_method/user_coupon_id 决定退款动作)
    """
    if order.pay_method == "balance":  # 余额单原路退回钱包
        balance = db.scalar(select(User.balance).where(User.user_id == order.user_id)) or 0
        balance_after = balance + order.amount  # 退后余额 = 当前 + 实付
        db.execute(update(User).where(User.user_id == order.user_id).values(balance=balance_after))  # 回补余额
        db.add(WalletTransaction(  # 退款流水(与钱包模块对账)
            user_id=order.user_id, type="refund", amount=order.amount,  # 退入为正数
            balance_after=balance_after, note=f"订单退款 {order.order_no}", create_time=datetime.now(),
        ))
    if order.user_coupon_id is not None:  # 已核销的优惠券返还(status=1 才返还, 幂等)
        db.execute(
            update(UserCoupon)
            .where(UserCoupon.id == order.user_coupon_id, UserCoupon.status == 1)  # 条件更新防重复返还
            .values(status=0, use_time=None)  # 重置为未使用并清使用时间
        )


def cancel_order_admin(db: Session, order_id: int, reason: str | None) -> str | None:
    """管理端代取消订单: pending -> cancelled / booked -> cancelled(已支付余额单退回+返还券), 同一事务提交

    参数: db 请求级 Session / order_id 订单ID / reason 取消原因(缺省为"管理员取消");
    返回 None 成功 / 错误文案 失败
    """
    order = db.scalar(select(CompanionOrder).where(CompanionOrder.order_id == order_id))
    if order is None:
        return "订单不存在"
    if order.status == "pending":
        order.status = "cancelled"  # 未支付直接取消
    elif order.status == "booked":  # 已支付订单代取消即完成退款
        order.status = "cancelled"  # 管理员代取消不走退款审核, 直接待退
        refund_paid_order(db, order)  # 余额回补 + 券返还(同事务)
    else:
        return "当前状态不可取消"  # ongoing/completed/refunding 不可代取消
    order.cancel_reason = (reason or "").strip() or "管理员取消"  # 缺省原因
    db.commit()  # 退款涉及多表, 一次性提交
    return None


def confirm_refund(db: Session, order_id: int) -> str | None:
    """管理端确认退款: refunding -> cancelled, 余额单退回+写退款流水+返还优惠券, 同一事务提交

    参数: db 请求级 Session / order_id 订单ID; 返回 None 成功 / 错误文案 失败
    """
    order = db.scalar(select(CompanionOrder).where(CompanionOrder.order_id == order_id))
    if order is None:
        return "订单不存在"
    if order.status != "refunding":
        return "该订单不在退款中"  # 仅退款中状态可确认
    order.status = "cancelled"  # 置终态
    refund_paid_order(db, order)  # 余额回补 + 券返还(同事务)
    db.commit()  # 退款涉及多表, 一次性提交
    return None


# ==================== 内部工具 ====================

def _parse_date(value: str | None) -> date | None:
    """'yyyy-MM-dd' 字符串 -> date, 解析失败返回 None

    参数: value 日期字符串(可空)
    """
    dt = parse_dt(value)  # parse_dt 支持纯日期格式
    return dt.date() if dt else None  # 转成 date 类型(仅日期部分)
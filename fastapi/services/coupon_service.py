"""
优惠券业务层
"""
from datetime import datetime, timedelta  # 日期时间类型的标准库
from sqlalchemy import select, func, update, and_
from sqlalchemy.orm import Session  # 第三方: 会话类型标注
from core.common import (  # 项目内: 泛型工具
    body_fields, delete_by_pks, eq_if, like_if, paginate, row_to_dict, where_if, insert_row, update_by_pk, between_if,
)
from models.entities import Coupon, User, UserCoupon
from schemas.body import CouponBody

# 已领取数量子查询
_RECEIVED_COUNT = (
    select(func.count())
    .where(UserCoupon.coupon_id == Coupon.coupon_id)
    .scalar_subquery()
    .label("received_count")
)

# 优惠券查询列
_COUPON_COLS = (
    Coupon.coupon_id, Coupon.coupon_name, Coupon.amount, Coupon.threshold, Coupon.valid_days,
    Coupon.per_limit, Coupon.total_count, Coupon.description, Coupon.status, Coupon.create_time,
    _RECEIVED_COUNT
)

# 用户优惠券查询列
_USER_COUPON_COLS = (
    UserCoupon.coupon_id, User.user_name, User.avatar, Coupon.coupon_name, Coupon.amount, Coupon.threshold,
    UserCoupon.status, UserCoupon.receive_time, UserCoupon.expire_time, UserCoupon.use_time
)


def coupon_row_to_dict(row) -> dict:
    """数据库行 -> camelCase 字典"""
    return row_to_dict(row)


def _base_query(coupon_name: str | None, status: int | None):
    """构造优惠券基础查询(动态条件, 供列表/分页复用)"""
    stmt = select(*_COUPON_COLS)  # 查询优惠券列
    stmt = where_if(stmt, like_if(Coupon.coupon_name, coupon_name), eq_if(Coupon.status, status))  # 拼接动态条件(值非空才生成)
    return stmt.order_by(Coupon.coupon_id.desc())  # 按主键ID倒序排序


def select_coupon_page(db: Session, page_num: int, page_size: int,
                       coupon_name: str | None = None, status: int | None = None) -> tuple[int, list[dict]]:
    """
    分页查询优惠券列表
    """
    stmt = _base_query(coupon_name, status)  # 复用基础查询
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [coupon_row_to_dict(r) for r in rows]  # 总数 + 当前页字典列表


def get_coupon_by_id(db: Session, coupon_id: int) -> dict | None:
    """
    按优惠券ID查询详情
    """
    row = db.execute(select(*_COUPON_COLS).where(Coupon.coupon_id == coupon_id)).first()  # 按主键查第一条
    return coupon_row_to_dict(row) if row else None  # 无记录返回 None


def name_exists(db: Session, coupon_name: str | None, exclude_id: int | None = None) -> bool:
    """
    优惠券名称是否已存在
    """
    if not coupon_name:
        return False
    stmt = select(Coupon.coupon_id).where(Coupon.coupon_name == coupon_name)  # 根据优惠券名称查询优惠券ID
    if exclude_id is not None:  # 更新场景要排除自身
        stmt = stmt.where(Coupon.coupon_id != exclude_id)
    return db.scalar(stmt) is not None  # 查到就代表存在


def insert_coupon(db: Session, body: CouponBody) -> int:
    """
    新增优惠券
    """
    return insert_row(db, Coupon, body_fields(body, skip=("couponId",)))


def update_coupon_by_id(db: Session, body: CouponBody) -> int:
    """
    根据优惠券ID更新优惠券信息
    """
    if body.couponId is None:  # 缺少主键无法更新
        return 0
    return update_by_pk(db, Coupon, Coupon.coupon_id, body.couponId, body_fields(body, skip=("couponId",)))


def delete_coupon_by_ids(db: Session, coupon_ids: list[int]) -> int:
    """
    批量删除优惠券
    """
    return delete_by_pks(db, Coupon, Coupon.coupon_id, coupon_ids)


def count_user_coupon_by_coupon_ids(db: Session, coupon_ids: list[int]) -> int:
    """
    统计这批优惠券的用户领取记录数
    """
    stmt = select(func.count()).select_from(UserCoupon).where(UserCoupon.coupon_id.in_(coupon_ids))  # 根据优惠券ID计数
    return db.scalar(stmt) or 0  # 如果没有记录就返回0


def _user_coupon_status_cond(status: int | None):
    """
    用户优惠券状态筛选条件
    """
    if status == 0:  # 未使用
        return and_(UserCoupon.status == 0, UserCoupon.expire_time >= func.now())
    if status == 1:  # 已使用
        return UserCoupon.status == 1
    if status == 2:  # 已过期
        return and_(UserCoupon.status == 0, UserCoupon.expire_time < func.now())
    return None  # 不筛选


def select_user_coupon_page(db: Session, page_num: int, page_size: int,
                            user_name: str | None = None, coupon_name: str | None = None,
                            status: int | None = None) -> tuple[int, list[dict]]:
    """
    分页查询用户领取记录列表
    """
    stmt = select(*_USER_COUPON_COLS).select_from(UserCoupon)  # 显式指定主表
    stmt = stmt.join(User, UserCoupon.user_id == User.user_id)  # 内链接用户表
    stmt = stmt.join(Coupon, UserCoupon.coupon_id == Coupon.coupon_id)  # 内连接优惠券表
    stmt = where_if(
        stmt,
        like_if(User.user_name, user_name),
        like_if(Coupon.coupon_name, coupon_name),
        _user_coupon_status_cond(status),
    )
    stmt = stmt.order_by(UserCoupon.id.desc())  # 按记录ID倒序排序
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [coupon_row_to_dict(r) for r in rows]  # 总数 + 当前页字典列表


# =============================== 用户端 ===============================

def select_available_coupons(db: Session, user_id: int) -> list[dict]:
    """
    领券中心: 全部启用状态的优惠券 + 当前用户已领取的次数 + 全站已领取的次数
    """
    claimed_count = (
        select(func.count())
        .where(UserCoupon.user_id == user_id, UserCoupon.coupon_id == Coupon.coupon_id)
        .scalar_subquery()
        .label("claimed_count")
    )
    stmt = (
        select(Coupon.coupon_id, Coupon.coupon_name, Coupon.amount, Coupon.threshold, Coupon.valid_days,
               Coupon.per_limit, Coupon.total_count, Coupon.description, _RECEIVED_COUNT, claimed_count)
        .where(Coupon.status == 0)
        .order_by(Coupon.coupon_id)
    )
    return [row_to_dict(r) for r in db.execute(stmt).all()]


def receive_coupon(db: Session, user_id: int, coupon_id: int) -> str | None:
    """
    领取优惠券: 校验存在/启用 每人限领 发放总量, 如果通过就写入领取记录, 返回None成功, 否则就返回错误信息
    """
    coupon = db.scalar(select(Coupon).where(Coupon.coupon_id == coupon_id, Coupon.status == 0))  # 优惠券存在并且已启用
    if coupon is None:
        return "优惠券不存在或已停用"
    my_count = db.scalar(  # 本人已经领取的该优惠券次数
        select(func.count()).select_from(UserCoupon)
        .where(UserCoupon.user_id == user_id, UserCoupon.coupon_id == coupon_id)
    ) or 0
    if my_count >= coupon.per_limit:  # 超出了每人限领的次数
        return f"该优惠券每人限领 {coupon.per_limit} 次"
    if coupon.total_count > 0:  # 有限量时校验全站已经领取的次数
        received = db.scalar(
            select(func.count()).select_from(UserCoupon).where(UserCoupon.coupon_id == coupon_id)
        ) or 0
        if received >= coupon.total_count:
            return "该优惠券已被领完"
    now = datetime.now()  # 领取时间
    db.add(UserCoupon(  # 写入领取记录, 过期时间 = 领取时间 + 有效天数
        user_id=user_id, coupon_id=coupon_id, status=0,
        receive_time=now, expire_time=now + timedelta(days=coupon.valid_days),
    ))
    db.commit()
    return None


def select_my_coupons(db: Session, user_id: int) -> list[dict]:
    """
    我的优惠券: 当前用户领取的优惠券列表
    """
    stmt = (
        select(UserCoupon.id, UserCoupon.coupon_id, Coupon.coupon_name, Coupon.amount, Coupon.threshold,
               UserCoupon.status, UserCoupon.receive_time, UserCoupon.expire_time, UserCoupon.use_time)
        .join(Coupon, UserCoupon.coupon_id == Coupon.coupon_id)  # 内连接优惠券
        .where(UserCoupon.user_id == user_id)
        .order_by(UserCoupon.id.desc())  # 最新领取的在前
    )
    return [row_to_dict(r) for r in db.execute(stmt).all()]


def use_coupon(db: Session, user_id: int, user_coupon_id: int) -> int:
    """
    核销优惠券(订单支付时调用): 本人 + 未使用 + 未过期的优惠券才可以核销
    """
    result = db.execute(
        update(UserCoupon)
        .where(UserCoupon.id == user_coupon_id, UserCoupon.user_id == user_id,  # 归属校验
               UserCoupon.status == 0, UserCoupon.expire_time >= func.now())  # 未使用且未过期(条件更新防并发)
        .values(status=1, use_time=func.now())  # 置已使用并记使用时间
    )
    db.commit()
    return result.rowcount  # 受影响行数(0 = 核销失败)


def return_coupon(db: Session, user_id: int, user_coupon_id: int) -> int:
    """
    返还优惠券(订单取消的时候退款时调用): 已使用的优惠券变回未使用的优惠券并且清空使用时间
    """
    result = db.execute(
        update(UserCoupon)
        .where(UserCoupon.id == user_coupon_id, UserCoupon.user_id == user_id, UserCoupon.status == 1)  # 仅已使用的券返还(幂等)
        .values(status=0, use_time=None)  # 重置未使用并清使用时间
    )
    db.commit()
    return result.rowcount  # 受影响行数

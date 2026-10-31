"""
订单评价管理业务层

评价内嵌于 companion_order(review_* 字段), 无独立评价表:
- 管理端: 分页查询已评价订单(join user/companion)、回复评价(重复回复覆盖更新)、
  删除评价(清空评价字段含回复, 订单记录保留, 用户可重新评价)
- 用户端: 某陪玩师全部真实评价(join user 取用户名/头像, 详情页评价列表/分布/标签统计)
"""
from datetime import datetime  # 标准库: 回复时间写入

from sqlalchemy import select, update  # 第三方: SQLAlchemy 列表达式
from sqlalchemy.orm import Session  # 第三方: 会话类型标注

from core.common import (  # 项目内: 泛型工具
    between_if, eq_if, fmt_dt, like_if, paginate, row_to_dict, where_if,
)
from models.entities import Companion, CompanionOrder, User  # 项目内: 订单/用户/陪玩师实体
from schemas.body import ReviewReplyBody  # 项目内: 评价回复请求体

# 评价视图查询列(订单定位/服务/金额/状态 + 下单用户与陪玩师信息 + 评价与回复字段)
_REVIEW_COLS = (
    CompanionOrder.order_id, CompanionOrder.order_no, CompanionOrder.status,
    CompanionOrder.service_name, CompanionOrder.price, CompanionOrder.hours,
    CompanionOrder.amount, CompanionOrder.create_time,
    CompanionOrder.user_id, User.user_name, User.avatar,
    CompanionOrder.companion_id, Companion.nick_name,
    CompanionOrder.review_rating, CompanionOrder.review_tags,
    CompanionOrder.review_content, CompanionOrder.review_time,
    CompanionOrder.review_reply, CompanionOrder.review_reply_time,
)

# 删除评价时清空的全部评价字段(含平台回复)
_REVIEW_FIELDS = (
    "review_rating", "review_tags", "review_content", "review_time",
    "review_reply", "review_reply_time",
)


def select_review_page(db: Session, page_num: int, page_size: int,
                       order_no: str | None = None, user_name: str | None = None,
                       nick_name: str | None = None, rating: int | None = None,
                       begin_time: datetime | None = None, end_time: datetime | None = None,
                       companion_id: int | None = None) -> tuple[int, list[dict]]:
    """管理端: 分页查询评价列表(review_rating 非空的订单, 新评价在前; companion_id 非空时仅看该陪玩师)

    参数: db 请求级 Session / page_num 页码 / page_size 每页条数 / order_no 订单号模糊(可选) /
          user_name 用户名模糊(可选) / nick_name 昵称模糊(可选) / rating 星级(可选) /
          begin_time/end_time 评价时间范围(可选) / companion_id 陪玩师数据范围(可选)
    """
    stmt = select(*_REVIEW_COLS).select_from(CompanionOrder)  # 显式指定主表
    stmt = stmt.join(User, CompanionOrder.user_id == User.user_id)  # 内连接用户(取用户名/头像)
    stmt = stmt.join(Companion, CompanionOrder.companion_id == Companion.companion_id)  # 内连接陪玩师(取昵称)
    stmt = stmt.where(CompanionOrder.review_rating.is_not(None))  # 仅已评价订单
    stmt = where_if(  # 拼接动态条件(值非空才生成)
        stmt,
        like_if(CompanionOrder.order_no, order_no),
        like_if(User.user_name, user_name),
        like_if(Companion.nick_name, nick_name),
        eq_if(CompanionOrder.review_rating, rating),
        between_if(CompanionOrder.review_time, begin_time, end_time),
        eq_if(CompanionOrder.companion_id, companion_id),  # 陪玩师数据范围(仅看自己被评的)
    )
    stmt = stmt.order_by(CompanionOrder.review_time.desc())  # 按评价时间倒序(新评价在前)
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [row_to_dict(r) for r in rows]


def select_companion_reviews(db: Session, companion_id: int) -> list[dict]:
    """用户端: 某陪玩师全部真实评价(join user 取用户名/头像, 新评价在前)

    参数: db 请求级 Session / companion_id 陪玩师ID
    """
    rows = db.execute(
        select(
            CompanionOrder.order_id, User.user_name, User.avatar,  # 订单定位 + 评价人信息
            CompanionOrder.service_name, CompanionOrder.review_rating, CompanionOrder.review_tags,
            CompanionOrder.review_content, CompanionOrder.review_time, CompanionOrder.review_reply,
        )
        .select_from(CompanionOrder)
        .join(User, CompanionOrder.user_id == User.user_id)  # 内连接用户(取用户名/头像)
        .where(CompanionOrder.companion_id == companion_id, CompanionOrder.review_rating.is_not(None))  # 该陪玩师已评价订单
        .order_by(CompanionOrder.review_time.desc())  # 新评价在前
    ).all()
    return [  # 字段名对齐前端详情页展示结构(user/game/rating/tags/content/time/reply)
        {
            "id": r.order_id, "user": r.user_name or "匿名用户", "avatar": r.avatar or "",
            "game": r.service_name or "", "rating": r.review_rating,
            "tags": (r.review_tags or "").split(",") if r.review_tags else [],
            "content": r.review_content or "",
            "time": fmt_dt(r.review_time) or "", "reply": r.review_reply or "",
        }
        for r in rows
    ]


def reply_review(db: Session, body: ReviewReplyBody) -> str | None:
    """管理端回复评价: 仅已评价订单可回复, 重复回复覆盖更新

    参数: db 请求级 Session / body 回复请求体(orderId 定位/reply 回复内容); 返回 None 成功 / 错误文案 失败
    """
    order = db.scalar(select(CompanionOrder).where(CompanionOrder.order_id == body.orderId))
    if order is None:
        return "订单不存在"
    if order.review_rating is None:
        return "该订单未评价, 无法回复"  # 未评价订单无回复对象
    order.review_reply = body.reply  # 覆盖式写入回复
    order.review_reply_time = datetime.now()  # 回复时间随最新回复刷新
    db.commit()  # 单表写操作
    return None


def delete_review_by_ids(db: Session, order_ids: list[int]) -> int:
    """管理端批量删除评价: 清空评价字段(含回复), 订单记录保留, 用户可重新评价

    参数: db 请求级 Session / order_ids 订单ID列表; 返回受影响行数(仅已评价订单会计入)
    """
    result = db.execute(
        update(CompanionOrder)
        .where(CompanionOrder.order_id.in_(order_ids), CompanionOrder.review_rating.is_not(None))  # 仅已评价订单生效
        .values(**{f: None for f in _REVIEW_FIELDS})  # 评价字段全部置空
    )
    db.commit()
    return result.rowcount  # 受影响行数
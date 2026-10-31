"""
订单投诉业务层

complaint(订单投诉) 模块:
- 管理端: 分页列表(join companion_order/user/companion 取订单号/服务/双方信息)、处理投诉(置为已处理并记录结果/说明/时间, 结果为全额退款时联动取消订单并原路退回)、批量删除
- 用户端: 发起投诉(订单详情页, 每单限一次, 仅已支付后的订单状态)
- 投诉处理联动全额退款(取消订单/余额退回/优惠券返还), 其他结果仅标记不联动订单状态
"""
from datetime import datetime  # 标准库: 日期时间类型

from sqlalchemy import select  # 第三方: SQLAlchemy 列表达式
from sqlalchemy.orm import Session  # 第三方: 会话类型标注

from core.common import (  # 项目内: 泛型工具
    delete_by_pks, eq_if, insert_row, like_if, paginate, row_to_dict, where_if,
)
from models.entities import Complaint, Companion, CompanionOrder, User  # 项目内: 订单投诉相关 ORM 实体
from schemas.body import ComplaintBody  # 项目内: 订单投诉请求体模型
from services import order_service  # 项目内: 订单业务层(全额退款联动复用其退款共通)

# 允许投诉的订单状态(已支付后: 待开始/进行中/已完成/退款中)
COMPLAINABLE_STATUS = ("booked", "ongoing", "completed", "refunding")

# 投诉查询列(join 订单/下单用户/陪玩师; 订单状态与投诉状态同名列, 订单状态 label 区分)
_COMPLAINT_COLS = (
    Complaint.complaint_id, Complaint.order_id, CompanionOrder.order_no,
    Complaint.user_id, User.user_name, User.avatar, Companion.nick_name,
    CompanionOrder.service_name, CompanionOrder.amount, CompanionOrder.status.label("order_status"),
    Complaint.complaint_type, Complaint.content, Complaint.status,
    Complaint.handle_result, Complaint.reply, Complaint.handle_time, Complaint.create_time,
)


def select_complaint_page(db: Session, page_num: int, page_size: int,
                          order_no: str | None = None, user_name: str | None = None,
                          nick_name: str | None = None, complaint_type: str | None = None,
                          status: int | None = None,
                          companion_id: int | None = None) -> tuple[int, list[dict]]:
    """管理端: 分页查询投诉列表(join 订单/下单用户/陪玩师; companion_id 非空时仅看该陪玩师被投诉的)

    参数: db 请求级 Session / page_num 页码 / page_size 每页条数 / order_no 订单号模糊(可选) /
          user_name 用户名模糊(可选) / nick_name 昵称模糊(可选) / complaint_type 类型(可选) /
          status 处理状态(可选) / companion_id 陪玩师数据范围(可选)
    """
    stmt = select(*_COMPLAINT_COLS).select_from(Complaint)  # 显式指定主表
    stmt = stmt.join(CompanionOrder, Complaint.order_id == CompanionOrder.order_id)  # 内连接订单(取订单信息)
    stmt = stmt.join(User, Complaint.user_id == User.user_id)  # 内连接投诉用户(取用户名/头像)
    stmt = stmt.join(Companion, CompanionOrder.companion_id == Companion.companion_id)  # 内连接陪玩师(取昵称)
    stmt = where_if(  # 拼接动态条件(值非空才生成)
        stmt,
        like_if(CompanionOrder.order_no, order_no),
        like_if(User.user_name, user_name),
        like_if(Companion.nick_name, nick_name),
        eq_if(Complaint.complaint_type, complaint_type),
        eq_if(Complaint.status, status),
        eq_if(CompanionOrder.companion_id, companion_id),  # 陪玩师数据范围(仅看自己被投诉的)
    )
    stmt = stmt.order_by(Complaint.complaint_id.desc())  # 按投诉ID倒序(最新投诉的在前)
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [row_to_dict(r) for r in rows]  # 总数 + 当前页字典列表


def handle_complaint(db: Session, body: ComplaintBody) -> str | None:
    """处理投诉核心事务: 置为已处理并记录结果/说明/时间; 结果为全额退款时联动取消订单并原路退回

    同一事务内完成投诉/订单/钱包多表写入后一次性提交。
    参数: db 请求级 Session / body 处理请求体(complaintId 定位/handleResult 结果/reply 说明)。
    返回 None 成功; 错误信息失败(未提交任何写入)。
    """
    complaint = db.scalar(  # 先定位投诉(已处理的拒绝再次处理, 防重复退款)
        select(Complaint).where(Complaint.complaint_id == body.complaintId)
    )
    if complaint is None:
        return "投诉不存在"
    if complaint.status == 1:
        return "该投诉已处理, 请勿重复处理"
    complaint.status = 1  # 写投诉处理字段
    complaint.handle_result = body.handleResult
    complaint.reply = body.reply if body.reply is not None else ""  # 说明缺省为空串
    complaint.handle_time = datetime.now()
    if body.handleResult == "全额退款":  # 联动订单: 取消 + 原路退回(余额退钱包+退款流水, 优惠券返还)
        order = db.scalar(
            select(CompanionOrder).where(CompanionOrder.order_id == complaint.order_id)
        )
        if order is None:
            db.rollback()  # 回滚投诉标记, 保证事务原子性
            return "关联订单不存在"
        if order.status != "cancelled":  # 已取消订单款项已退, 仅记录结果不重复退
            order.status = "cancelled"  # 置取消终态
            order.cancel_reason = "投诉成立, 全额退款"  # 固定取消原因
            order_service.refund_paid_order(db, order)  # 复用订单退款共通(同事务)
    db.commit()  # 多表写操作: 同一事务内完成后一次性提交
    return None


def delete_complaint_by_ids(db: Session, complaint_ids: list[int]) -> int:
    """批量删除投诉

    参数: db 请求级 Session / complaint_ids 投诉ID列表; 返回受影响行数
    """
    return delete_by_pks(db, Complaint, Complaint.complaint_id, complaint_ids)  # 泛型按主键批量删除


# ==================== 用户端 ====================

def insert_complaint(db: Session, body: ComplaintBody, user_id: int) -> tuple[str | None, int]:
    """用户端发起投诉: 校验订单归属/状态/未投诉过 -> 写入(每单限一次), 返回 (错误信息, 受影响行数)

    参数: db 请求级 Session / body 投诉请求体(orderNo/complaintType/content) / user_id 投诉用户(取登录用户)
    """
    order = db.execute(  # 按订单号定位本人订单
        select(CompanionOrder.order_id, CompanionOrder.status).where(
            CompanionOrder.order_no == body.orderNo, CompanionOrder.user_id == user_id
        )
    ).first()
    if order is None:
        return "订单不存在", 0
    if order.status not in COMPLAINABLE_STATUS:
        return "当前订单状态不可投诉", 0
    existed = db.scalar(  # 每单限投诉一次(uk_order_id 唯一索引兜底)
        select(Complaint.complaint_id).where(Complaint.order_id == order.order_id)
    )
    if existed is not None:
        return "该订单已投诉过, 请耐心等待平台处理", 0
    fields = {  # 只取订单/类型/内容, 其余(状态/时间)走数据库默认值
        "order_id": order.order_id,
        "user_id": user_id,
        "complaint_type": body.complaintType,
        "content": body.content,
        "status": 0,
    }
    return None, insert_row(db, Complaint, fields)  # 泛型单表插入(直接提交)
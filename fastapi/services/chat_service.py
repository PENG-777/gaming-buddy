"""
官方客服业务层

service_conversation(官方客服会话) + service_message(官方客服消息) 模块:
- 用户端: 初始化/获取我的会话(首次创建插入欢迎语)、历史消息(顺带清未读)、未读数
- 管理端: 分页会话列表(join user 取用户信息)、按会话查历史消息
- 双端共通: 保存消息(WS 收发两端调用, 插消息+更新会话快照/未读数, 同一事务一次提交)
"""
from datetime import datetime  # 标准库: 消息/会话时间写入

from sqlalchemy import select  # 第三方: 列表达式查询
from sqlalchemy.orm import Session  # 第三方: 会话类型标注

from core.common import entity_to_dict, fmt_dt, like_if, paginate, row_to_dict, where_if  # 项目内: 泛型工具
from models.entities import ServiceConversation, ServiceMessage, User  # 项目内: 客服会话/消息/用户实体

# 首次创建会话时的欢迎语(人工客服语气, 不用"小助手"式 AI 措辞)
WELCOME = "您好, 这里是官方客服中心, 请描述您遇到的问题(订单/支付/账号等), 客服看到后会尽快回复您~"

# 管理端会话列表查询列(join user 取用户名/头像)
_CONV_COLS = (
    ServiceConversation.conversation_id, ServiceConversation.user_id,
    User.user_name, User.avatar,
    ServiceConversation.last_message, ServiceConversation.user_unread,
    ServiceConversation.last_time, ServiceConversation.create_time,
)

# 消息查询列
_MSG_COLS = (
    ServiceMessage.message_id, ServiceMessage.conversation_id,
    ServiceMessage.sender_type, ServiceMessage.content, ServiceMessage.create_time,
)


def _now() -> datetime:
    """当前时间(消息/会话快照统一取应用时间, 保证返回值必含时间)

    无参数; 去微秒与表列精度一致。
    """
    return datetime.now().replace(microsecond=0)  # 去微秒(与 datetime 列秒级精度对齐)


def _msg_dict(message_id: int, conversation_id: int, sender_type: int, content: str, create_time: datetime) -> dict:
    """消息字段 -> camelCase 字典(入库返回共用, 时间统一格式化)

    参数: message_id 消息ID / conversation_id 会话ID / sender_type 发送方(0用户 1客服) /
          content 正文 / create_time 发送时间
    """
    return {
        "messageId": message_id,
        "conversationId": conversation_id,
        "senderType": sender_type,
        "content": content,
        "createTime": fmt_dt(create_time),  # datetime -> 统一格式字符串
    }


def get_or_create_conversation(db: Session, user_id: int) -> dict:
    """获取我的客服会话, 不存在则创建并插入欢迎语(一人一会话, uk 兜底)

    参数: db 请求级 Session / user_id 用户ID
    """
    conv = db.scalar(
        select(ServiceConversation).where(ServiceConversation.user_id == user_id)
    )
    if conv is not None:
        return entity_to_dict(conv)  # ORM 实体转 dict(select(Entity) 整体查询结果)
    now = _now()
    conv = ServiceConversation(  # 建会话
        user_id=user_id, last_message=WELCOME, user_unread=1, last_time=now, create_time=now,
    )  # 未读数 1: 欢迎语即一条客服消息
    db.add(conv)  # 加入会话
    db.flush()  # 取自增 conversation_id
    db.add(ServiceMessage(  # 插入欢迎语消息(sender_type=1 客服)
        conversation_id=conv.conversation_id, sender_type=1, content=WELCOME, create_time=now,
    ))
    db.commit()  # 会话+欢迎语两条写入: 同一事务一次性提交
    return entity_to_dict(conv)  # ORM 实体转 dict


def get_my_conversation(db: Session, user_id: int) -> tuple[dict, list[dict]]:
    """我的会话 + 全部历史消息(不动未读数, 打开会话时另调 clear_unread); 会话不存在时自动创建

    参数: db 请求级 Session / user_id 用户ID; 返回 (会话字典, 消息字典列表)
    """
    conv = get_or_create_conversation(db, user_id)  # 无会话则建(含欢迎语)
    rows = db.execute(
        select(*_MSG_COLS)
        .where(ServiceMessage.conversation_id == conv["conversationId"])
        .order_by(ServiceMessage.message_id.asc())  # 按发送顺序升序
    ).all()
    return conv, [row_to_dict(r) for r in rows]  # 会话 + 消息列表


def clear_unread(db: Session, user_id: int) -> int:
    """清零我的客服未读数(打开客服会话时调用); 返回受影响行数

    参数: db 请求级 Session / user_id 用户ID
    """
    rows = db.query(ServiceConversation).filter(
        ServiceConversation.user_id == user_id, ServiceConversation.user_unread != 0  # 仅未读非 0 的行才更新
    ).update({"user_unread": 0})  # 批量置 0
    db.commit()  # 单表更新直接提交
    return rows  # 受影响行数(0 表示本就无未读)


def get_unread(db: Session, user_id: int) -> int:
    """我的客服未读数(无会话视为 0)

    参数: db 请求级 Session / user_id 用户ID
    """
    unread = db.scalar(
        select(ServiceConversation.user_unread).where(ServiceConversation.user_id == user_id)
    )
    return unread or 0  # 无会话(None)或 NULL 均返回 0


def page_conversations(db: Session, page_num: int, page_size: int, kw: str | None = None) -> tuple[int, list[dict]]:
    """管理端: 分页查询会话列表(join user 取用户名/头像, 按最后消息时间倒序)

    参数: db 请求级 Session / page_num 页码 / page_size 每页条数 / kw 用户名模糊筛选(可选)
    """
    stmt = select(*_CONV_COLS).select_from(ServiceConversation)  # 会话列 + join 用户信息
    stmt = stmt.join(User, ServiceConversation.user_id == User.user_id)  # 关联用户表
    stmt = where_if(stmt, like_if(User.user_name, kw))  # 用户名模糊条件(值非空才拼)
    stmt = stmt.order_by(ServiceConversation.last_time.desc())  # 最新活跃的在前(NULL 会话排最后)
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [row_to_dict(r) for r in rows]  # 总数 + 当前页字典列表


def get_conversation_brief(db: Session, conversation_id: int) -> dict | None:
    """按会话ID查会话概要(join user 取用户名/头像, 与列表行同结构); 不存在返回 None

    WS 落库后组推送 payload 用(管理端实时刷新列表需要完整的会话行)。

    参数: db 请求级 Session / conversation_id 会话ID
    """
    row = db.execute(
        select(*_CONV_COLS)
        .select_from(ServiceConversation)
        .join(User, ServiceConversation.user_id == User.user_id)  # 关联用户表取用户名/头像
        .where(ServiceConversation.conversation_id == conversation_id)
    ).first()  # 主键查询最多一条
    return row_to_dict(row) if row else None  # 无记录返回 None


def list_conv_messages(db: Session, conversation_id: int) -> list[dict]:
    """管理端: 按会话查全部历史消息(message_id 升序)

    参数: db 请求级 Session / conversation_id 会话ID
    """
    rows = db.execute(
        select(*_MSG_COLS)
        .where(ServiceMessage.conversation_id == conversation_id)
        .order_by(ServiceMessage.message_id.asc())  # 按发送顺序升序
    ).all()
    return [row_to_dict(r) for r in rows]  # 消息字典列表


def save_message(db: Session, conversation_id: int, sender_type: int, content: str) -> dict | None:
    """保存一条消息并更新会话快照(插消息+改会话同一事务一次提交); 会话不存在返回 None

    客服回复(sender_type=1)时用户未读数 +1; 用户发言不影响自己未读数。

    参数: db 请求级 Session / conversation_id 会话ID / sender_type 发送方(0用户 1客服) /
          content 正文; 会话不存在返回 None, 成功返回消息字典
    """
    conv = db.scalar(
        select(ServiceConversation).where(ServiceConversation.conversation_id == conversation_id)
    )
    if conv is None:
        return None  # 会话不存在(可能已被删除)
    now = _now()
    msg = ServiceMessage(
        conversation_id=conversation_id, sender_type=sender_type, content=content, create_time=now,
    )  # 新消息实体
    db.add(msg)  # 加入会话
    db.flush()  # 取自增 message_id
    conv.last_message = content[:500]  # 快照与列宽一致, 超长截断
    conv.last_time = now  # 刷新最后消息时间(列表排序依据)
    if sender_type == 1:
        conv.user_unread = (conv.user_unread or 0) + 1  # 客服回复: 用户未读 +1
    db.commit()  # 消息+会话两条写入: 同一事务一次性提交
    return _msg_dict(msg.message_id, conversation_id, sender_type, content, now)  # 消息字典(WS 推送共用)
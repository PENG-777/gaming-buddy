"""
用户私聊业务层(用户 <-> 陪玩师)

private_conversation(用户私聊会话) + private_message(用户私聊消息) 模块:
- 用户端: 我的会话列表、按陪玩师开聊(get_or_create + 历史 + 清用户未读)
- 管理端工作台: 会话分页(管理员看全部/陪玩师只看自己的, join 双方取昵称头像)、按会话查历史(陪玩师打开清自己未读, 管理员只读不清)
- 双端共通: 保存消息(WS 收发两端调用, 插消息+更新会话快照/对向未读数, 同一事务一次提交)
"""
from datetime import datetime  # 标准库: 消息/会话时间写入

from sqlalchemy import select  # 第三方: 列表达式查询
from sqlalchemy.orm import Session  # 第三方: 会话类型标注

from core.common import entity_to_dict, fmt_dt, paginate, row_to_dict  # 项目内: 泛型工具
from models.entities import Companion, PrivateConversation, PrivateMessage, User  # 项目内: 私聊相关实体
from schemas.vo import LoginUser  # 项目内: 登录用户快照
from services.menu_service import ADMIN_ROLE_ID  # 项目内: 管理员角色 ID 常量

# 会话查询列(join user + companion 取双方昵称/头像, 同名列用 label 区分;
# 统一携带双方信息, 用户端/陪玩师工作台/管理员监管按需取字段渲染)
_CONV_COLS = (
    PrivateConversation.conversation_id, PrivateConversation.user_id, PrivateConversation.companion_id,
    User.user_name.label("user_name"), User.avatar.label("user_avatar"),
    Companion.nick_name.label("companion_name"), Companion.avatar.label("companion_avatar"),
    PrivateConversation.last_message, PrivateConversation.user_unread, PrivateConversation.companion_unread,
    PrivateConversation.last_time, PrivateConversation.create_time,
)

# 消息查询列
_MSG_COLS = (
    PrivateMessage.message_id, PrivateMessage.conversation_id,
    PrivateMessage.sender_type, PrivateMessage.content, PrivateMessage.create_time,
)


def _now() -> datetime:
    """当前时间(消息/会话快照统一取应用时间, 保证返回值必含时间)

    无参数; 去微秒与表列精度一致。
    """
    return datetime.now().replace(microsecond=0)  # 去微秒(与 datetime 列秒级精度对齐)


def _msg_dict(message_id: int, conversation_id: int, sender_type: int, content: str, create_time: datetime) -> dict:
    """消息字段 -> camelCase 字典(入库返回共用, 时间统一格式化)

    参数: message_id 消息ID / conversation_id 会话ID / sender_type 发送方(0用户 1陪玩师) /
          content 正文 / create_time 发送时间
    """
    return {
        "messageId": message_id,
        "conversationId": conversation_id,
        "senderType": sender_type,
        "content": content,
        "createTime": fmt_dt(create_time),  # datetime -> 统一格式字符串
    }


def is_admin(login_user: LoginUser) -> bool:
    """管理员判定(token 快照 roleId, 与官方客服管理端 WS 同口径)

    参数: login_user 登录用户快照(取 user.roleId)
    """
    return login_user.user is not None and login_user.user.roleId == ADMIN_ROLE_ID  # 快照缺角色信息视为非管理员


def get_companion_by_user_id(db: Session, user_id: int) -> Companion | None:
    """按登录用户ID查陪玩师身份(WS 鉴权 + 工作台数据过滤用)

    参数: db 会话 / user_id 登录用户ID; 非陪玩师账号返回 None
    """
    return db.scalar(select(Companion).where(Companion.user_id == user_id))  # 整行查询(需 companion_id 供归属校验)


def get_companion_user_id(db: Session, companion_id: int) -> int | None:
    """按陪玩师ID查其登录账号 user_id(用户私聊 WS 推送路由用)

    参数: db 会话 / companion_id 陪玩师ID; 未绑定登录账号返回 None
    """
    return db.scalar(select(Companion.user_id).where(Companion.companion_id == companion_id))  # 单列查询


def get_or_create_conversation(db: Session, user_id: int, companion_id: int) -> dict | None:
    """获取(或创建)用户与陪玩师的私聊会话, 首次创建为空会话(无欢迎语); 陪玩师不存在返回 None

    参数: db 请求级 Session / user_id 用户ID / companion_id 陪玩师ID
    """
    companion = db.scalar(select(Companion).where(Companion.companion_id == companion_id))
    if companion is None:
        return None  # 陪玩师不存在(可能已删除)
    conv = db.scalar(
        select(PrivateConversation).where(
            PrivateConversation.user_id == user_id, PrivateConversation.companion_id == companion_id
        )
    )
    if conv is not None:
        return entity_to_dict(conv)  # ORM 实体转 dict(select(Entity) 整体查询结果)
    conv = PrivateConversation(  # 建空会话(消息发出时才更新快照/未读)
        user_id=user_id, companion_id=companion_id, last_time=_now(), create_time=_now(),
    )
    db.add(conv)  # 加入会话
    db.commit()  # 单条单表写操作直接提交
    return entity_to_dict(conv)  # 返回含主键的会话字典


def _list_messages(db: Session, conversation_id: int) -> list[dict]:
    """按会话查全部历史消息(message_id 升序)

    参数: db 会话 / conversation_id 会话ID
    """
    rows = db.execute(
        select(*_MSG_COLS)
        .where(PrivateMessage.conversation_id == conversation_id)
        .order_by(PrivateMessage.message_id.asc())  # 按发送顺序升序
    ).all()
    return [row_to_dict(r) for r in rows]  # 消息字典列表


def _brief_stmt():
    """会话查询语句(双表 join, 分页/单条共用)

    无参数; 返回带双方昵称/头像的会话基础查询(调用方再拼 where/order)。
    """
    return (
        select(*_CONV_COLS)
        .select_from(PrivateConversation)
        .join(User, PrivateConversation.user_id == User.user_id)  # 关联用户表(用户侧信息)
        .join(Companion, PrivateConversation.companion_id == Companion.companion_id)  # 关联陪玩师表(陪玩师侧信息)
    )


def list_my_conversations(db: Session, user_id: int) -> list[dict]:
    """用户端: 我的私聊会话列表(按最后消息时间倒序, 不清任何未读)

    参数: db 请求级 Session / user_id 用户ID
    """
    stmt = _brief_stmt().where(PrivateConversation.user_id == user_id)  # 仅查本人发起的会话
    stmt = stmt.order_by(PrivateConversation.last_time.desc())  # 最近活跃在前
    return [row_to_dict(r) for r in db.execute(stmt).all()]  # 会话字典列表


def open_for_user(db: Session, user_id: int, companion_id: int) -> tuple[dict, list[dict]] | None:
    """用户端: 按陪玩师开聊(get_or_create + 全部历史 + 清我的未读); 陪玩师不存在返回 None

    参数: db 请求级 Session / user_id 用户ID / companion_id 陪玩师ID; 返回 (会话概要, 消息列表)
    """
    conv = get_or_create_conversation(db, user_id, companion_id)  # 无会话则建空会话
    if conv is None:
        return None  # 陪玩师不存在
    rows = db.query(PrivateConversation).filter(  # 清用户未读(仅自己的会话, 归属天然校验)
        PrivateConversation.conversation_id == conv["conversationId"],
        PrivateConversation.user_unread != 0,  # 仅未读非 0 才更新
    ).update({"user_unread": 0})
    if rows:
        db.commit()  # 有变更才提交
    messages = _list_messages(db, conv["conversationId"])  # 全部历史消息
    brief = get_conversation_brief(db, conv["conversationId"])  # 清零后的最新会话行
    return brief or conv, messages  # 优先返回带双方信息的概要


def page_workbench_conversations(db: Session, login_user: LoginUser, page_num: int, page_size: int, kw: str | None = None) -> tuple[int, list[dict]]:
    """工作台: 分页查询会话列表(按最后消息时间倒序, join 双方取昵称/头像)

    数据范围按身份过滤: 管理员看全部(监管), 陪玩师只看自己的; 普通用户无数据。

    参数: db 请求级 Session / login_user 登录用户(角色决定数据范围) / page_num 页码 /
          page_size 每页条数 / kw 用户名/昵称模糊筛选(可选)
    """
    stmt = _brief_stmt()
    if is_admin(login_user):  # 管理员: 全部会话, 关键词同时匹配用户名/陪玩师昵称
        if kw:
            stmt = stmt.where(
                User.user_name.like(f"%{kw}%") | Companion.nick_name.like(f"%{kw}%")
            )  # or 条件: 任一侧命中即保留
    else:  # 非管理员: 按陪玩师身份过滤(非陪玩师查不到会话, 返回空)
        companion = get_companion_by_user_id(db, login_user.userId)
        if companion is None:
            return 0, []  # 普通用户无工作台数据
        stmt = stmt.where(PrivateConversation.companion_id == companion.companion_id)  # 仅本人会话
        if kw:
            stmt = stmt.where(User.user_name.like(f"%{kw}%"))  # 陪玩师侧只按用户名搜
    stmt = stmt.order_by(PrivateConversation.last_time.desc())  # 最近活跃在前
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页
    return total, [row_to_dict(r) for r in rows]  # 总数 + 当前页字典列表


def list_messages_for_workbench(db: Session, conversation_id: int, login_user: LoginUser) -> list[dict] | None:
    """工作台: 按会话查全部历史消息; 无权限或会话不存在返回 None

    管理员可看任意会话(只读, 不清未读); 陪玩师只能看自己的会话(打开时清陪玩师未读)。

    参数: db 请求级 Session / conversation_id 会话ID / login_user 登录用户(角色决定权限)
    """
    if is_admin(login_user):
        return _list_messages(db, conversation_id)  # 管理员直读, 不动未读
    companion = get_companion_by_user_id(db, login_user.userId)
    if companion is None:
        return None  # 非陪玩师无权查看
    owned = db.scalar(  # 归属校验: 会话必须属于该陪玩师
        select(PrivateConversation.conversation_id).where(
            PrivateConversation.conversation_id == conversation_id,
            PrivateConversation.companion_id == companion.companion_id,
        )
    )
    if owned is None:
        return None  # 会话不存在或不属于该陪玩师
    rows = db.query(PrivateConversation).filter(  # 清陪玩师未读(管理员查看不动此字段)
        PrivateConversation.conversation_id == conversation_id,
        PrivateConversation.companion_unread != 0,  # 仅未读非 0 才更新
    ).update({"companion_unread": 0})
    if rows:
        db.commit()  # 有变更才提交
    return _list_messages(db, conversation_id)  # 历史消息列表


def get_conversation_brief(db: Session, conversation_id: int) -> dict | None:
    """按会话ID查会话概要(双方信息, 与列表行同结构); 不存在返回 None

    WS 落库后组推送 payload 用(三端实时刷新列表需要完整的会话行)。

    参数: db 请求级 Session / conversation_id 会话ID
    """
    row = db.execute(
        _brief_stmt().where(PrivateConversation.conversation_id == conversation_id)
    ).first()  # 主键查询最多一条
    return row_to_dict(row) if row else None  # 无记录返回 None


def save_message(db: Session, conversation_id: int, sender_type: int, content: str) -> dict | None:
    """保存一条消息并更新会话快照(插消息+改会话同一事务一次提交); 会话不存在返回 None

    用户发言(sender_type=0)时陪玩师未读数 +1; 陪玩师回复(sender_type=1)时用户未读数 +1。

    参数: db 请求级 Session / conversation_id 会话ID / sender_type 发送方(0用户 1陪玩师) /
          content 正文; 会话不存在返回 None, 成功返回消息字典
    """
    conv = db.scalar(
        select(PrivateConversation).where(PrivateConversation.conversation_id == conversation_id)
    )
    if conv is None:
        return None  # 会话不存在(可能已被删除)
    now = _now()
    msg = PrivateMessage(
        conversation_id=conversation_id, sender_type=sender_type, content=content, create_time=now,
    )  # 新消息实体
    db.add(msg)  # 加入会话
    db.flush()  # 取自增 message_id
    conv.last_message = content[:500]  # 快照与列宽一致, 超长截断
    conv.last_time = now  # 刷新最后消息时间(列表排序依据)
    if sender_type == 0:
        conv.companion_unread = (conv.companion_unread or 0) + 1  # 用户发言: 陪玩师未读 +1
    else:
        conv.user_unread = (conv.user_unread or 0) + 1  # 陪玩师回复: 用户未读 +1
    db.commit()  # 消息+会话两条写入: 同一事务一次性提交
    return _msg_dict(msg.message_id, conversation_id, sender_type, content, now)  # 消息字典(WS 推送共用)
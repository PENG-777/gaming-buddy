"""官方客服（REST 历史/未读 + WebSocket 实时收发）

路由不设统一前缀: REST 为 /chat/**, WebSocket 为顶级 /ws/chat(用户端)与 /ws/adminChat(管理端)。
WS 鉴权走 query 参数 token(浏览器 WebSocket 无法携带 Authorization 头), 失败关闭码:
4401 未登录/登录过期、4403 非客服端(管理员/客服)。
"""
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect  # FastAPI: 路由/查询参数/WebSocket 与断开异常

from core.database import SessionLocal  # 项目内: Session 工厂(WS 内短会话)
from core.deps import DbDep, LoginUserDep, PageDep  # 项目内: 通用依赖
from core.response import ajax_success, ajax_success_data, page_data  # 项目内: 统一响应
from core.ws import authenticate_ws, manager  # 项目内: WS 鉴权与连接管理
from services import chat_service  # 项目内: 官方客服业务层
from services.menu_service import ADMIN_ROLE_ID, SERVICE_ROLE_ID  # 项目内: 管理员/客服角色 ID 常量

router = APIRouter(tags=["chat"])  # 模块路由器(不设前缀, 见模块注释)

# 单条消息长度上限(与表列宽一致, 超长截断)
MAX_CONTENT_LEN = 1000


# ==================== 用户端 REST ====================

@router.get("/chat/myConversation")
def my_conversation(login_user: LoginUserDep, db: DbDep):
    """用户端: 初始化/获取我的客服会话 + 全部历史消息(不动未读数, 打开会话另调 /chat/read)

    参数: login_user 登录用户 / db 请求级 Session
    """
    conv, messages = chat_service.get_my_conversation(db, login_user.userId)  # 无会话则自动创建
    return ajax_success_data({"conversation": conv, "messages": messages})  # 会话概要 + 消息列表


@router.put("/chat/read")
def mark_read(login_user: LoginUserDep, db: DbDep):
    """用户端: 清零我的客服未读数(打开客服会话时调用)

    参数: login_user 登录用户 / db 请求级 Session
    """
    chat_service.clear_unread(db, login_user.userId)  # user_unread 置 0
    return ajax_success()


@router.get("/chat/unread")
def chat_unread(login_user: LoginUserDep, db: DbDep):
    """用户端: 我的客服未读数(WS 断线期间的补偿轮询)

    参数: login_user 登录用户 / db 请求级 Session
    """
    return ajax_success_data(chat_service.get_unread(db, login_user.userId))  # 未读整数(int)


# ==================== 管理端 REST ====================

@router.get("/chat/page")
def chat_page(page: PageDep, login_user: LoginUserDep, db: DbDep,
              kw: str | None = Query(None)):  # 用户名模糊筛选(可选)
    """管理端: 分页查询客服会话列表(join user, 按最后消息时间倒序)

    参数: page 分页参数 / login_user 登录用户 / db 请求级 Session / kw 用户名模糊筛选(可选)
    """
    total, rows = chat_service.page_conversations(db, page.pageNum, page.pageSize, kw)
    return page_data(rows, total)  # {total, rows, code, msg}


@router.get("/chat/{conversationId}/messages")
def conv_messages(conversationId: int, login_user: LoginUserDep, db: DbDep):
    """管理端: 按会话查全部历史消息(message_id 升序)

    参数: conversationId 路径参数, 会话ID / login_user 登录用户 / db 请求级 Session
    """
    return ajax_success_data(chat_service.list_conv_messages(db, conversationId))  # 消息字典列表


# ==================== WebSocket ====================

def _clip(content) -> str:
    """消息内容清洗: 去首尾空白, 超长截断(与表列宽一致)

    参数: content 客户端发来的原始消息体(容错 None)
    """
    text = str(content or "").strip()  # 容错 None 转空串并去首尾空白
    return text[:MAX_CONTENT_LEN]  # 截断到列宽上限


@router.websocket("/ws/chat")
async def ws_chat(ws: WebSocket, token: str | None = Query(None)):
    """用户端 WS: 接收用户消息落库并实时推给所有在线管理员; 上线回推当前未读数"""
    login_user = authenticate_ws(token)  # 与 HTTP 登录依赖同链路校验
    if login_user is None or login_user.userId is None:  # 鉴权失败或快照缺用户ID
        await ws.close(code=4401)  # 未登录/登录过期
        return
    user_id = login_user.userId  # 当前用户 ID(连接注册键)
    await ws.accept()  # 完成 WS 握手
    await manager.connect_user(user_id, ws)  # 注册连接(重复连接踢旧)
    try:
        with SessionLocal() as db:  # 上线即知未读(不在此清零, 清零走 REST 打开会话)
            unread = chat_service.get_unread(db, user_id)
        await ws.send_json({"type": "init", "unread": unread})  # 上线回执: 携带当前未读数
    except Exception:
        pass  # 未读推送失败不断连接(前端有 REST 未读接口兜底)
    try:
        while True:  # 消息主循环: 阻塞等待客户端下一条消息
            data = await ws.receive_json()  # 客户端 JSON 消息
            msg_type = data.get("type")  # 消息类型分发(ping/chat)
            if msg_type == "ping":  # 心跳
                await ws.send_json({"type": "pong"})
            elif msg_type == "chat":  # 用户发送消息
                content = _clip(data.get("content"))  # 清洗/截断消息内容
                if not content:  # 空消息拒收
                    await ws.send_json({"type": "error", "msg": "消息内容不能为空"})
                    continue
                with SessionLocal() as db:  # 每条消息一个短 Session
                    conv = chat_service.get_or_create_conversation(db, user_id)  # 无会话则创建
                    msg = chat_service.save_message(db, conv["conversationId"], 0, content)  # 落库(sender_type=0 用户)
                    brief = chat_service.get_conversation_brief(db, conv["conversationId"])  # 会话概要(供列表更新)
                # 只推管理端(用户端本地即时显示, 免去去重逻辑)
                await manager.push_to_admins({"type": "message", "conversation": brief, "message": msg})
    except WebSocketDisconnect:  # 正常断开
        pass
    finally:
        manager.disconnect_user(user_id, ws)  # 连接清理(仅当注册的仍是本连接)


@router.websocket("/ws/adminChat")
async def ws_admin_chat(ws: WebSocket, token: str | None = Query(None)):
    """管理端 WS: 接收客服回复落库, 实时推给对应用户与所有在线管理员(多工作台同步)"""
    login_user = authenticate_ws(token)  # 与 HTTP 登录依赖同链路校验
    if login_user is None or login_user.userId is None:  # 鉴权失败或快照缺用户ID
        await ws.close(code=4401)  # 未登录/登录过期
        return
    # token 快照不携带 roleName(见 routers/auth.py), 客服端判定用角色 ID 常量(管理员/客服)
    if login_user.user is None or login_user.user.roleId not in (ADMIN_ROLE_ID, SERVICE_ROLE_ID):
        await ws.close(code=4403)  # 非客服端(管理员/客服)
        return
    admin_id = login_user.userId  # 管理员/客服用户 ID(连接注册键)
    await ws.accept()  # 完成 WS 握手
    await manager.connect_admin(admin_id, ws)  # 注册到管理端连接池(重复连接踢旧)
    try:
        await ws.send_json({"type": "init"})  # 上线回执(前端据此刷新在线状态)
    except Exception:
        pass  # 回执失败不断连接
    try:
        while True:  # 消息主循环: 阻塞等待客户端下一条消息
            data = await ws.receive_json()  # 客户端 JSON 消息
            msg_type = data.get("type")  # 消息类型分发(ping/reply)
            if msg_type == "ping":  # 心跳
                await ws.send_json({"type": "pong"})
            elif msg_type == "reply":  # 客服回复
                conversation_id = data.get("conversationId")  # 目标会话ID
                content = _clip(data.get("content"))  # 清洗/截断回复内容
                if not isinstance(conversation_id, int):  # 会话ID缺失/类型非法
                    await ws.send_json({"type": "error", "msg": "参数错误: 缺少会话ID"})
                    continue
                if not content:  # 空回复拒收
                    await ws.send_json({"type": "error", "msg": "回复内容不能为空"})
                    continue
                with SessionLocal() as db:  # 每条消息一个短 Session
                    msg = chat_service.save_message(db, conversation_id, 1, content)  # 落库(sender_type=1 客服; 会话不存在返回 None)
                    brief = chat_service.get_conversation_brief(db, conversation_id)  # 会话概要(含未读数/最后消息)
                if msg is None or brief is None:  # 会话不存在(已被删除等)
                    await ws.send_json({"type": "error", "msg": "会话不存在"})
                    continue
                await ws.send_json({"type": "ok"})  # 回执(发送方据此清空输入框)
                # 推给对应用户(不在线静默忽略, 上线后 REST 历史兜底)
                await manager.push_to_user(brief["userId"], {"type": "message", "conversation": brief, "message": msg})
                # 推给所有在线管理员(多工作台同步, 含发送方自身)
                await manager.push_to_admins({"type": "message", "conversation": brief, "message": msg})
    except WebSocketDisconnect:  # 正常断开
        pass
    finally:
        manager.disconnect_admin(admin_id, ws)  # 连接清理(仅当注册的仍是本连接)
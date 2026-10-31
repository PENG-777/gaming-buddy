"""用户私聊（REST 历史 + WebSocket 实时收发）

用户端用户 <-> 陪玩师(companion 角色)的一对一私聊:
- 用户在用户端消息页发起/收发; 陪玩师登录管理端"私聊消息"工作台回复自己的会话;
  管理员(admin)在同一工作台只读监管全部会话(不可回复、不清未读)。

路由不设统一前缀: REST 为 /privateChat/**, WebSocket 为顶级 /ws/privateChat(用户端)
与 /ws/companionChat(陪玩师工作台/管理员监管)。
WS 鉴权走 query 参数 token(浏览器 WebSocket 无法携带 Authorization 头), 失败关闭码:
4401 未登录/登录过期、4403 无权访问(工作台仅管理员与陪玩师)。
"""
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect  # FastAPI: 路由/查询参数/WebSocket 与断开异常

from core.database import SessionLocal  # 项目内: Session 工厂(WS 内短会话)
from core.deps import DbDep, LoginUserDep, PageDep  # 项目内: 通用依赖
from core.response import ajax_error, ajax_success_data, page_data  # 项目内: 统一响应
from core.ws import authenticate_ws, manager  # 项目内: WS 鉴权与连接管理
from services import private_chat_service as svc  # 项目内: 用户私聊业务层

router = APIRouter(tags=["privateChat"])  # 模块路由器(不设前缀, 见模块注释)

# 单条消息长度上限(与表列宽一致, 超长截断)
MAX_CONTENT_LEN = 1000


# ==================== 用户端 REST ====================

@router.get("/privateChat/myConversations")
def my_conversations(login_user: LoginUserDep, db: DbDep):
    """用户端: 我的私聊会话列表(含双方昵称/头像与未读数, 不清任何未读)

    参数: login_user 登录用户 / db 请求级 Session
    """
    return ajax_success_data(svc.list_my_conversations(db, login_user.userId))  # 会话字典列表


@router.get("/privateChat/companion/{companionId}/open")
def open_conversation(companionId: int, login_user: LoginUserDep, db: DbDep):
    """用户端: 按陪玩师开聊(get_or_create + 全部历史 + 清我的未读; "聊一聊"直达用)

    参数: companionId 路径参数, 陪玩师ID / login_user 登录用户 / db 请求级 Session
    """
    result = svc.open_for_user(db, login_user.userId, companionId)  # 陪玩师无效时返回 None
    if result is None:
        return ajax_error("陪玩师不存在或已下架")
    conversation, messages = result  # 拆包会话与历史消息
    return ajax_success_data({"conversation": conversation, "messages": messages})


# ==================== 工作台 REST(陪玩师回复 / 管理员监管) ====================

@router.get("/privateChat/workbench/page")
def workbench_page(page: PageDep, login_user: LoginUserDep, db: DbDep,
                   kw: str | None = Query(None)):  # 用户名/陪玩师昵称模糊筛选(可选)
    """工作台: 分页查询会话列表(管理员看全部, 陪玩师只看自己的, 按最后消息时间倒序)

    参数: page 分页参数 / login_user 登录用户(角色决定数据范围) / db 请求级 Session / kw 用户名/昵称模糊筛选(可选)
    """
    total, rows = svc.page_workbench_conversations(db, login_user, page.pageNum, page.pageSize, kw)
    return page_data(rows, total)  # {total, rows, code, msg}


@router.get("/privateChat/{conversationId}/workbenchMessages")
def workbench_messages(conversationId: int, login_user: LoginUserDep, db: DbDep):
    """工作台: 按会话查全部历史消息(陪玩师打开清自己未读, 管理员只读不清)

    参数: conversationId 路径参数, 会话ID / login_user 登录用户(角色决定权限) / db 请求级 Session
    """
    messages = svc.list_messages_for_workbench(db, conversationId, login_user)  # 无权/不存在返回 None
    if messages is None:
        return ajax_error("会话不存在或无权查看")
    return ajax_success_data(messages)  # 消息字典列表


# ==================== WebSocket ====================

def _clip(content) -> str:
    """消息内容清洗: 去首尾空白, 超长截断(与表列宽一致)

    参数: content 客户端发来的原始消息体(容错 None)
    """
    text = str(content or "").strip()  # 容错 None 转空串并去首尾空白
    return text[:MAX_CONTENT_LEN]  # 截断到列宽上限


@router.websocket("/ws/privateChat")
async def ws_private_chat(ws: WebSocket, token: str | None = Query(None)):
    """用户端私聊 WS: 接收用户消息落库, 实时推给陪玩师工作台与在线监管管理员"""
    login_user = authenticate_ws(token)  # 与 HTTP 登录依赖同链路校验
    if login_user is None or login_user.userId is None:  # 鉴权失败或快照缺用户ID
        await ws.close(code=4401)  # 未登录/登录过期
        return
    user_id = login_user.userId  # 当前用户 ID(连接注册键)
    await ws.accept()  # 完成 WS 握手
    await manager.connect_private_user(user_id, ws)  # 注册连接(重复连接踢旧)
    try:
        await ws.send_json({"type": "init"})  # 上线回执(前端据此刷新在线状态)
    except Exception:
        pass  # 回执失败不断连接
    try:
        while True:  # 消息主循环: 阻塞等待客户端下一条消息
            data = await ws.receive_json()  # 客户端 JSON 消息
            msg_type = data.get("type")  # 消息类型分发(ping/chat)
            if msg_type == "ping":  # 心跳
                await ws.send_json({"type": "pong"})
            elif msg_type == "chat":  # 用户向陪玩师发私聊
                companion_id = data.get("companionId")  # 目标陪玩师ID
                content = _clip(data.get("content"))  # 清洗/截断消息内容
                if not isinstance(companion_id, int):  # 陪玩师ID缺失/类型非法
                    await ws.send_json({"type": "error", "msg": "参数错误: 缺少陪玩师ID"})
                    continue
                if not content:  # 空消息拒收
                    await ws.send_json({"type": "error", "msg": "消息内容不能为空"})
                    continue
                with SessionLocal() as db:  # 每条消息一个短 Session
                    conv = svc.get_or_create_conversation(db, user_id, companion_id)  # 无会话则创建
                    if conv is None:  # 陪玩师不存在/已下架
                        await ws.send_json({"type": "error", "msg": "陪玩师不存在或已下架"})
                        continue
                    msg = svc.save_message(db, conv["conversationId"], 0, content)  # 落库(sender_type=0 用户)
                    brief = svc.get_conversation_brief(db, conv["conversationId"])  # 会话概要(供列表更新)
                    companion_user_id = svc.get_companion_user_id(db, companion_id)  # 陪玩师登录账号(推送路由用)
                await ws.send_json({"type": "ok", "conversationId": conv["conversationId"]})  # 回执(发送方本地即时显示)
                # 只推对端与监管(用户端本地即时显示, 免去去重逻辑)
                payload = {"type": "message", "conversation": brief, "message": msg}  # 统一推送负载
                if companion_user_id is not None:  # 陪玩师工作台定点推
                    await manager.push_to_companion(companion_user_id, payload)
                await manager.push_to_private_admins(payload)  # 在线监管管理员广播
    except WebSocketDisconnect:  # 正常断开
        pass
    finally:
        manager.disconnect_private_user(user_id, ws)  # 连接清理(仅当注册的仍是本连接)


@router.websocket("/ws/companionChat")
async def ws_companion_chat(ws: WebSocket, token: str | None = Query(None)):
    """工作台 WS: 陪玩师回复落库实时推给用户; 管理员仅接收推送监管(不可回复)"""
    login_user = authenticate_ws(token)  # 与 HTTP 登录依赖同链路校验
    if login_user is None or login_user.userId is None:  # 鉴权失败或快照缺用户ID
        await ws.close(code=4401)  # 未登录/登录过期
        return
    user_id = login_user.userId  # 当前用户 ID(连接注册键)
    # 管理员进监管池; 陪玩师进工作台池(拿 companion_id 供 reply 归属校验); 其余拒绝
    with SessionLocal() as db:  # 短会话查角色与档案
        is_admin = svc.is_admin(login_user)  # 是否管理员角色
        companion = None if is_admin else svc.get_companion_by_user_id(db, user_id)  # 陪玩师档案(非管理员才查)
    if not is_admin and companion is None:  # 既非管理员也无陪玩师档案
        await ws.close(code=4403)  # 非管理员且非陪玩师
        return
    await ws.accept()  # 完成 WS 握手
    if is_admin:  # 按身份注册到不同连接池
        await manager.connect_private_admin(user_id, ws)  # 管理员监管池(广播接收)
    else:
        await manager.connect_companion(user_id, ws)  # 陪玩师工作台池(定点推送)
    try:
        await ws.send_json({"type": "init", "role": "admin" if is_admin else "companion"})  # 上线回执(附身份)
    except Exception:
        pass  # 回执失败不断连接
    try:
        while True:  # 消息主循环: 阻塞等待客户端下一条消息
            data = await ws.receive_json()  # 客户端 JSON 消息
            msg_type = data.get("type")  # 消息类型分发(ping/reply)
            if msg_type == "ping":  # 心跳
                await ws.send_json({"type": "pong"})
            elif msg_type == "reply":  # 陪玩师回复
                if is_admin:  # 管理员只读监管, 禁止回复
                    await ws.send_json({"type": "error", "msg": "管理员仅可监管查看, 不能回复"})
                    continue
                conversation_id = data.get("conversationId")  # 目标会话ID
                content = _clip(data.get("content"))  # 清洗/截断回复内容
                if not isinstance(conversation_id, int):  # 会话ID缺失/类型非法
                    await ws.send_json({"type": "error", "msg": "参数错误: 缺少会话ID"})
                    continue
                if not content:  # 空回复拒收
                    await ws.send_json({"type": "error", "msg": "回复内容不能为空"})
                    continue
                with SessionLocal() as db:  # 每条消息一个短 Session
                    brief = svc.get_conversation_brief(db, conversation_id)  # 先取会话概要做归属校验
                    if brief is None or brief["companionId"] != companion.companion_id:  # 归属校验(防越权)
                        await ws.send_json({"type": "error", "msg": "会话不存在或无权回复"})
                        continue
                    msg = svc.save_message(db, conversation_id, 1, content)  # 落库(sender_type=1 陪玩师)
                    brief = svc.get_conversation_brief(db, conversation_id)  # 落库后的最新会话行
                await ws.send_json({"type": "ok", "message": msg})  # 回执携带入库消息(发送方本地入列, 以库为准)
                payload = {"type": "message", "conversation": brief, "message": msg}  # 统一推送负载
                # 推给对应用户(不在线静默忽略, 上线后 REST 历史兜底)
                await manager.push_to_private_user(brief["userId"], payload)
                # 广播给所有在线监管管理员(多监管页同步)
                await manager.push_to_private_admins(payload)
    except WebSocketDisconnect:  # 正常断开
        pass
    finally:
        if is_admin:  # 按身份从对应连接池清理
            manager.disconnect_private_admin(user_id, ws)
        else:
            manager.disconnect_companion(user_id, ws)
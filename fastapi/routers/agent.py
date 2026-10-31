"""AI 助手（多 Agent 对话 SSE + 会话管理 + Agent 配置管理, /agent 前缀）

对话接口 POST /agent/chat(用户端) 与 /agent/analysis/chat(仅管理员) 返回
text/event-stream, 事件协议(event + JSON data):
  status  Agent 移交/工具调用进度(前端渲染进度气泡)
  token   主管最终答复的增量文本(打字机效果, 子 Agent 中间输出不外发)
  done    结束(含会话ID/消息ID/自动标题, 供前端更新会话列表)
  error   异常(SSE 已 200, 业务错误走事件而非状态码)
每 SSE_PING_SECONDS 秒发送 ": ping" 注释行防代理空闲断连; 生成器内落库
使用 SessionLocal 短会话(流式响应跨越请求生命周期, 对齐 chat.py 模式)。
"""
import asyncio  # 标准库: 异步队列/超时(心跳与产出并发)
import json  # 标准库: SSE data 序列化

from fastapi import APIRouter
from fastapi.responses import StreamingResponse  # SSE 流式响应

from agent.analyst import build_analyst  # 项目内: 管理端 supervisor 图构建
from agent.registry import AGENT_REGISTRY  # 项目内: Agent 注册表(handoff 名称翻译)
from agent.user_assistant import build_user_assistant  # 项目内: 用户端 supervisor 图构建
from core.database import SessionLocal  # 项目内: Session 工厂(生成器内短会话)
from core.deps import DbDep, LoginUserDep  # 项目内: 通用依赖
from core.exceptions import ApiError  # 项目内: 业务异常
from core.response import ajax_success_data, to_ajax  # 项目内: 统一响应
from schemas.body import AgentChatBody, AgentConfigBody  # 项目内: 请求体
from services import agent_service  # 项目内: AI 助手业务层
from services.menu_service import ADMIN_ROLE_ID  # 项目内: 管理员角色 ID

router = APIRouter(prefix="/agent", tags=["agent"])

# SSE 心跳间隔(秒): 防 vite 代理/浏览器空闲断连
SSE_PING_SECONDS = 15

# 场景标识(与 agent_config.scene 一致)
SCENE_USER = "user"
SCENE_ANALYST = "analyst"

# 全部子 Agent 标识(用于区分 LLM 输出归属: 子 Agent 中间输出不外发)
_WORKER_KEYS = {spec.key for spec in AGENT_REGISTRY.values() if not spec.is_supervisor}


def _sse(event: str, data: dict) -> str:
    """拼一条 SSE 事件文本(event + JSON data + 空行结尾)

    参数: event 事件名(status/token/done/error) / data 事件负载(dict, datetime 自动转字符串)
    """
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"  # 中文不转义, 空行标志一条事件结束


def _chunk_text(chunk) -> str:
    """提取 AIMessageChunk 的文本(content 兼容 str 与多模态 list 两种形态)

    参数: chunk 流式增量消息(LangChain AIMessageChunk, 非文本形态安全降级为空串)
    """
    content = getattr(chunk, "content", "")  # 取 content 字段(缺失时为空串)
    if isinstance(content, str):  # 普通文本形态直接返回
        return content
    if isinstance(content, list):  # 多模态分段: 拼接其中 text 段
        return "".join(seg.get("text", "") for seg in content if isinstance(seg, dict))
    return ""  # 其他形态(如 None)返回空串


def _require_admin(login_user) -> None:
    """管理端专用接口校验(仅管理员, 越权直接业务异常)

    参数: login_user 登录用户快照(取 user.roleId 判定角色)
    """
    if login_user.user is None or login_user.user.roleId != ADMIN_ROLE_ID:  # 非管理员或快照缺角色信息
        raise ApiError("仅管理员可使用经营分析能力")  # HTTP 500 + 错误提示


# ==================== SSE 对话(用户端 + 管理端) ====================

async def _event_stream(graph, messages: list, conversation_id: int):
    """执行 Agent 图并产出 SSE 事件流(产出与心跳并发, 15s 无产出补 ping)

    用 astream_events(v2) 消费事件(官方通用流式接口, 对 supervisor 嵌套子图
    也能拿到 token 级 on_chat_model_stream):
    - token: 仅透出非子 Agent(checkpoint_ns 首段不是 worker 标识)的 LLM 输出;
      supervisor 移交决策阶段若产生过文案, 移交时发 reset 事件让前端清空
    - status: on_tool_start 事件(移交 handoff / 业务工具调用进度)
    """
    queue: asyncio.Queue = asyncio.Queue()  # 事件队列: 产出协程与消费生成器解耦(心跳不阻塞产出)

    async def produce():
        """后台消费 astream_events 并放入队列(异常与结束统一转事件)"""
        answer_text = ""  # 累计最终答复全文(移交前文案会被清空重计)
        last_worker = None  # 最后一次移交的子 Agent(assistant 消息归属统计)
        try:
            async for ev in graph.astream_events({"messages": messages}, version="v2"):  # 官方通用流式事件接口
                kind = ev["event"]  # 事件类型(模型流式/工具开始等)
                meta = ev.get("metadata") or {}  # 事件元数据(含子图命名空间)
                # checkpoint_ns 形如 'supervisor:uuid|agent:uuid' / 'order_agent:uuid|...':
                # 首段即产出该 token 的子图名(顶层为空串), 用于区分主管与子 Agent 输出
                owner = str(meta.get("checkpoint_ns", "")).split(":", 1)[0].split("|", 1)[0]
                if kind == "on_chat_model_stream":  # LLM token 级增量输出
                    if owner in _WORKER_KEYS:  # 子 Agent 中间输出不干扰正文
                        continue
                    piece = _chunk_text((ev.get("data") or {}).get("chunk"))  # 提取本次增量文本
                    if piece:  # 空片丢弃
                        answer_text += piece  # 累计到最终答复
                        await queue.put(("token", {"content": piece}))  # 发打字机事件
                elif kind == "on_tool_start":  # 工具调用开始(含移交)
                    name = ev.get("name") or ""  # 工具名(transfer_to_xxx 为移交)
                    if name.startswith("transfer_to_"):  # 主管移交子 Agent
                        target = name[len("transfer_to_"):]  # 目标子 Agent 标识
                        zh = AGENT_REGISTRY.get(target)  # 取中文名(未注册则为 None)
                        last_worker = target  # 记录归属
                        if answer_text:  # 移交前若已有文案(非最终答案), 通知前端清空
                            answer_text = ""
                            await queue.put(("token", {"content": "", "reset": True}))
                        await queue.put(("status", {  # 前端渲染进度气泡
                            "agent": "supervisor", "tool": name, "targetAgent": target,
                            "msg": f"已移交「{zh.name if zh else target}」处理",
                        }))
                    else:  # 业务工具调用进度
                        zh_agent = AGENT_REGISTRY.get(owner)  # 调用方 Agent 中文名
                        await queue.put(("status", {
                            "agent": owner or "supervisor", "tool": name,
                            "msg": f"「{zh_agent.name}」正在调用 {name} ..." if zh_agent else f"正在调用工具 {name} ...",
                        }))
            if not answer_text.strip():  # 全程无有效输出(如全部子 Agent 停用且未直答)
                await queue.put(("error", {"msg": "AI 助手暂时没有生成答复, 请稍后重试"}))
                return
            await queue.put(("final", {"content": answer_text, "agentName": last_worker}))  # 最终答复事件
        except Exception as e:  # 网络/配额/模型异常统一走 error 事件
            await queue.put(("error", {"msg": f"AI 服务异常: {e}"}))
        finally:
            await queue.put(None)  # 结束哨兵

    producer = asyncio.create_task(produce())  # 启动后台产出协程
    try:
        while True:  # 消费循环: 队列事件逐条转 SSE, 空闲补心跳
            try:
                item = await asyncio.wait_for(queue.get(), timeout=SSE_PING_SECONDS)  # 限时等下一条事件
            except asyncio.TimeoutError:
                yield ": ping\n\n"  # 空闲心跳(SSE 注释行, 前端忽略)
                continue
            if item is None:  # 收到哨兵, 流正常结束
                break
            kind, data = item  # 拆事件
            if kind == "final":  # 最终答复: 落库后发 done
                with SessionLocal() as db:  # 落库助手答复 + 读取自动标题(短会话)
                    msg = agent_service.append_message(db, conversation_id, "assistant",
                                                       data["content"], data.get("agentName"))
                    conv = agent_service.get_conversation(db, conversation_id)
                yield _sse("done", {"conversationId": conversation_id, "messageId": msg["messageId"],
                                    "title": (conv or {}).get("title", "新对话")})
            else:  # token / status / error
                yield _sse(kind, data)
    finally:
        if not producer.done():  # 客户端提前断开(生成器被取消)
            producer.cancel()  # 客户端断开时终止后台产出
        try:
            await producer  # 等待后台协程退出(吞掉取消异常)
        except (asyncio.CancelledError, Exception):
            pass


async def _chat_response(body: AgentChatBody, login_user, db, scene: str):
    """对话接口共通: 会话定位/归属校验 -> 落库用户消息 -> 构建注入上下文 -> SSE 流

    参数: body 对话请求体(conversationId 可空/content 必填) / login_user 登录用户 / db 请求级 Session /
          scene 场景标识(SCENE_USER 用户端 / SCENE_ANALYST 管理端)
    """
    content = (body.content or "").strip()  # 去首尾空白
    if not content:
        raise ApiError("消息内容不能为空")
    if body.conversationId:  # 已有会话: 校验归属与场景
        conv = agent_service.get_conversation(db, body.conversationId)
        if conv is None or conv["userId"] != login_user.userId:  # 不存在或非本人
            raise ApiError("会话不存在")
        if conv["scene"] != scene:  # 用户端会话不能用于分析端(反之亦然)
            raise ApiError("会话场景不匹配")
        conversation_id = conv["conversationId"]
    else:  # 新建会话
        conv = agent_service.create_conversation(db, login_user.userId, scene)
        conversation_id = conv["conversationId"]
    agent_service.append_message(db, conversation_id, "user", content)  # 先落库用户消息
    agent_service.touch_title(db, conversation_id, content)  # 首轮自动命名
    history = agent_service.history_messages(db, conversation_id)  # 注入窗口(含本轮输入)
    messages = [("human" if h["role"] == "user" else "assistant", h["content"]) for h in history]  # 转 LangChain 消息二元组

    # 构建图(纯内存组装): 用户端订单类工具闭包绑定当前用户, 管理端无需绑定
    # (返回的 answer_nodes 已不使用: token 归属改由 checkpoint_ns 区分)
    if scene == SCENE_ANALYST:
        graph, _ = build_analyst()  # 管理端经营分析图
    else:
        graph, _ = build_user_assistant(login_user.userId)  # 用户端开黑小助手图

    return StreamingResponse(  # 以 SSE 流返回(非 JSON)
        _event_stream(graph, messages, conversation_id),  # 事件流生成器
        media_type="text/event-stream",  # SSE 媒体类型
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},  # 禁代理缓冲
    )


@router.post("/chat")
async def agent_chat(body: AgentChatBody, login_user: LoginUserDep, db: DbDep):
    """用户端 AI 助手对话(SSE 流式, 多 Agent 编排)

    参数: body 对话请求体 / login_user 登录用户 / db 请求级 Session
    """
    return await _chat_response(body, login_user, db, SCENE_USER)  # 用户端场景共通流程


@router.post("/analysis/chat")
async def analysis_chat(body: AgentChatBody, login_user: LoginUserDep, db: DbDep):
    """管理端经营分析对话(SSE 流式, 仅管理员)

    参数: body 对话请求体 / login_user 登录用户 / db 请求级 Session
    """
    _require_admin(login_user)  # 仅管理员可用
    return await _chat_response(body, login_user, db, SCENE_ANALYST)  # 管理端场景共通流程


# ==================== 会话管理 REST ====================

@router.get("/conversations")
def conversations(scene: str, login_user: LoginUserDep, db: DbDep):
    """我的会话列表(按活跃时间倒序; analyst 场景仅管理员)

    参数: scene 查询参数, 场景标识(user/analyst) / login_user 登录用户 / db 请求级 Session
    """
    if scene not in (SCENE_USER, SCENE_ANALYST):  # 场景白名单校验
        raise ApiError("场景参数错误")
    if scene == SCENE_ANALYST:  # 分析场景仅管理员可见
        _require_admin(login_user)
    return ajax_success_data(agent_service.list_conversations(db, login_user.userId, scene))  # 会话字典列表


@router.get("/conversations/{conversation_id}/messages")
def conversation_messages(conversation_id: int, login_user: LoginUserDep, db: DbDep):
    """按会话查全部历史消息(校验归属)

    参数: conversation_id 路径参数, 会话ID / login_user 登录用户 / db 请求级 Session
    """
    conv = agent_service.get_conversation(db, conversation_id)
    if conv is None or conv["userId"] != login_user.userId:  # 不存在或非本人
        raise ApiError("会话不存在")
    if conv["scene"] == SCENE_ANALYST:  # 分析会话消息仅管理员可读
        _require_admin(login_user)
    return ajax_success_data(agent_service.list_messages(db, conversation_id))  # 消息字典列表


@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, login_user: LoginUserDep, db: DbDep):
    """删除会话及其全部消息(校验归属)

    参数: conversation_id 路径参数, 会话ID / login_user 登录用户 / db 请求级 Session
    """
    conv = agent_service.get_conversation(db, conversation_id)
    if conv is not None and conv["scene"] == SCENE_ANALYST:  # 分析会话仅管理员可删
        _require_admin(login_user)
    return to_ajax(agent_service.delete_conversation(db, login_user.userId, conversation_id))  # 归属不符时删 0 行报失败


# ==================== Agent 配置管理(仅管理员) ====================

@router.get("/config/list")
def config_list(login_user: LoginUserDep, db: DbDep):
    """全部 Agent 配置(含近 30 天调用次数)

    参数: login_user 登录用户(须管理员) / db 请求级 Session
    """
    _require_admin(login_user)
    return ajax_success_data(agent_service.list_agent_configs(db))  # 配置字典列表


@router.put("/config/{agent_id}")
def update_config(agent_id: int, body: AgentConfigBody, login_user: LoginUserDep, db: DbDep):
    """更新 Agent 配置(描述/提示词/温度/启停, 下次对话生效)

    参数: agent_id 路径参数, Agent 配置ID / body 更新请求体(仅非 null 字段生效) / login_user 登录用户(须管理员) / db 请求级 Session
    """
    _require_admin(login_user)
    return to_ajax(agent_service.update_agent_config(db, agent_id, body))  # 按受影响行数判定成败
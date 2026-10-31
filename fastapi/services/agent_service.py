"""
AI 助手业务层（会话/消息 CRUD + Agent 配置管理）

- 会话/消息: 面向 routers 的常规 CRUD(请求级 Session), 历史注入窗口取最近 20 条
- Agent 配置: 管理页列表(含近 30 天调用统计)/更新(仅提示词/温度/启停/描述)
- get_effective_configs: 供 agent 包构建图时读取运行时配置, 自开短会话
  (Agent 执行跨越请求生命周期), 读失败(如未建表)返回空字典回退代码默认值
"""
from datetime import datetime, timedelta  # 标准库: 时间写入与统计窗口

from sqlalchemy import delete, func, select, update  # 第三方: 列表达式/聚合/更新
from sqlalchemy.orm import Session  # 第三方: 会话类型标注

from core.common import entity_to_dict, update_by_pk  # 项目内: 实体转字典/按主键更新
from core.database import SessionLocal  # 项目内: Session 工厂(短会话)
from models.entities import AgentConfig, AgentConversation, AgentMessage  # 项目内: AI 助手 ORM 实体
from schemas.body import AgentConfigBody  # 项目内: Agent 配置请求体

# 对话历史注入窗口(发给 LLM 的最近消息条数, 含本轮问答)
HISTORY_WINDOW = 20


# ==================== 会话/消息 CRUD ====================

def create_conversation(db: Session, user_id: int, scene: str) -> dict:
    """新建会话并返回 camelCase 字典

    参数: db 请求级 Session / user_id 归属用户ID / scene 场景标识(user/analyst)
    """
    conv = AgentConversation(user_id=user_id, scene=scene, create_time=datetime.now(), update_time=datetime.now())  # 新会话实体(默认标题新对话)
    db.add(conv)  # 加入会话
    db.commit()  # 单表写入直接提交
    return entity_to_dict(conv)  # 提交后主键已回填


def get_conversation(db: Session, conversation_id: int) -> dict | None:
    """按主键查会话

    参数: db 请求级 Session / conversation_id 会话ID; 无结果返回 None
    """
    row = db.execute(select(AgentConversation).where(AgentConversation.conversation_id == conversation_id)).scalar_one_or_none()
    return entity_to_dict(row) if row else None  # 整体实体查询后转字典


def list_conversations(db: Session, user_id: int, scene: str) -> list[dict]:
    """我的会话列表(按最后活跃时间倒序)

    参数: db 请求级 Session / user_id 用户ID / scene 场景标识(仅查该场景)
    """
    rows = db.execute(
        select(AgentConversation).where(AgentConversation.user_id == user_id, AgentConversation.scene == scene)
        .order_by(AgentConversation.update_time.desc(), AgentConversation.conversation_id.desc())  # 活跃时间倒序, 同刻按ID稳定排序
    ).scalars().all()
    return [entity_to_dict(r) for r in rows]  # 实体列表转字典列表


def delete_conversation(db: Session, user_id: int, conversation_id: int) -> int:
    """删除会话及其全部消息(校验归属, 两表同事务提交)

    参数: db 请求级 Session / user_id 归属用户ID(校验会话属于本人) / conversation_id 会话ID;
          返回受影响行数(0 表示会话不存在或非本人)
    """
    conv = db.execute(
        select(AgentConversation.conversation_id).where(
            AgentConversation.conversation_id == conversation_id,
            AgentConversation.user_id == user_id,  # 归属校验(非本人视为不存在)
        )
    ).first()
    if conv is None:
        return 0  # 会话不存在或不属于该用户
    db.execute(delete(AgentMessage).where(AgentMessage.conversation_id == conversation_id))  # 先删消息
    db.execute(delete(AgentConversation).where(AgentConversation.conversation_id == conversation_id))  # 再删会话
    db.commit()  # 两表同一事务提交
    return 1


def list_messages(db: Session, conversation_id: int) -> list[dict]:
    """按会话查全部历史消息(message_id 升序)

    参数: db 请求级 Session / conversation_id 会话ID
    """
    rows = db.execute(
        select(AgentMessage).where(AgentMessage.conversation_id == conversation_id)
        .order_by(AgentMessage.message_id.asc())  # 按发送顺序升序(前端直接渲染)
    ).scalars().all()
    return [entity_to_dict(r) for r in rows]  # 实体列表转字典列表


def history_messages(db: Session, conversation_id: int, limit: int = HISTORY_WINDOW) -> list[dict]:
    """取最近 N 条历史(时间正序返回), 供 SSE 构建注入 LLM 的上下文(不含本轮新消息)

    参数: db 请求级 Session / conversation_id 会话ID / limit 注入窗口条数(默认 20)
    """
    rows = db.execute(
        select(AgentMessage).where(AgentMessage.conversation_id == conversation_id)
        .order_by(AgentMessage.message_id.desc()).limit(limit)  # 倒序取最近 N 条
    ).scalars().all()
    return [entity_to_dict(r) for r in reversed(rows)]  # 反转回正序(时间轴顺序)


def append_message(db: Session, conversation_id: int, role: str, content: str,
                   agent_name: str | None = None) -> dict:
    """追加一条消息并刷新会话活跃时间

    参数: db 请求级 Session / conversation_id 会话ID / role 角色(user/assistant) /
          content 消息正文 / agent_name 应答 Agent 名(仅 assistant 消息携带, 可空)
    """
    msg = AgentMessage(conversation_id=conversation_id, role=role, agent_name=agent_name,
                       content=content, create_time=datetime.now())  # 新消息实体
    db.add(msg)  # 加入会话
    db.execute(  # 手动刷新活跃时间(仅 INSERT 不会触发会话表的 ON UPDATE)
        update(AgentConversation).where(AgentConversation.conversation_id == conversation_id)
        .values(update_time=datetime.now())
    )
    db.commit()  # 消息 + 活跃时间同事务提交
    return entity_to_dict(msg)  # 返回含主键的消息字典


def touch_title(db: Session, conversation_id: int, first_input: str) -> None:
    """首轮对话自动命名: 取用户输入前 20 字符(超长截断, 无需返回)

    参数: db 请求级 Session / conversation_id 会话ID / first_input 用户首条输入
    """
    title = (first_input or "").strip().replace("\n", " ")[:20] or "新对话"  # 去空白/换行转空格/截断 20 字, 空输入保持默认
    db.execute(update(AgentConversation).where(
        AgentConversation.conversation_id == conversation_id,
        AgentConversation.title == "新对话",  # 仅默认标题时改名(用户未自定义)
    ).values(title=title))
    db.commit()  # 单表更新直接提交


# ==================== Agent 配置管理 ====================

def list_agent_configs(db: Session) -> list[dict]:
    """全部 Agent 配置(含近 30 天调用次数统计, 管理页展示)

    参数: db 请求级 Session
    """
    stats = agent_call_stats(db, days=30)  # agent_key -> 调用次数
    rows = db.execute(select(AgentConfig).order_by(AgentConfig.agent_id.asc())).scalars().all()  # 按 ID 升序取全部配置
    return [entity_to_dict(r, {"callCount": stats.get(r.agent_key, 0)}) for r in rows]  # 附加 callCount 占位字段


def agent_call_stats(db: Session, days: int = 30) -> dict[str, int]:
    """近 N 天各 Agent 应答次数(assistant 消息按 agent_name 聚合)

    参数: db 请求级 Session / days 统计窗口天数(默认 30)
    """
    begin = datetime.now() - timedelta(days=days)  # 窗口起始时刻
    rows = db.execute(
        select(AgentMessage.agent_name, func.count())
        .where(AgentMessage.role == "assistant", AgentMessage.agent_name.is_not(None),  # 仅携带归属的应答消息
               AgentMessage.create_time >= begin)  # 仅统计窗口内
        .group_by(AgentMessage.agent_name)  # 按 Agent 名分组计数
    ).all()
    return {name: cnt for name, cnt in rows}  # {agent_name: 次数}


def update_agent_config(db: Session, agent_id: int, body: AgentConfigBody) -> int:
    """更新 Agent 配置(仅允许改描述/提示词/温度/启停; 标识/名称/场景/工具清单不可改)

    参数: db 请求级 Session / agent_id 配置ID / body 更新请求体(仅非 null 字段生效); 返回受影响行数
    """
    fields = {}  # 待更新列(仅收集非空字段)
    if body.description is not None:
        fields["description"] = body.description  # 职责描述
    if body.prompt is not None and body.prompt.strip():
        fields["prompt"] = body.prompt  # 系统提示词(空白串不更新)
    if body.temperature is not None:
        fields["temperature"] = max(0.0, min(float(body.temperature), 1.0))  # 温度夹取 [0, 1]
    if body.enabled is not None:
        fields["enabled"] = 1 if body.enabled else 0  # 归一为 0/1(0 启用 1 停用)
    if not fields:
        return 0  # 无可更新字段
    return update_by_pk(db, AgentConfig, AgentConfig.agent_id, agent_id, fields)  # 泛型按主键更新


def get_effective_configs(scene: str) -> dict[str, dict]:
    """读取某场景 Agent 生效配置: agent_key -> {prompt, temperature, enabled}

    自开短会话(Agent 构建跨越请求生命周期); 表不存在等异常时返回空字典,
    由 agent 包回退 registry 代码默认值(未执行建表 SQL 也能工作)。
    """
    try:
        with SessionLocal() as db:  # 短会话: Agent 构建跨越请求生命周期
            rows = db.execute(
                select(AgentConfig.agent_key, AgentConfig.prompt, AgentConfig.temperature, AgentConfig.enabled)
                .where(AgentConfig.scene == scene)  # 仅取该场景的配置
            ).all()
            return {r.agent_key: {"prompt": r.prompt, "temperature": r.temperature, "enabled": r.enabled} for r in rows}  # 行转 {agent_key: 配置}
    except Exception as e:  # 表不存在/连接失败等, 不阻断对话
        print(f"[WARN] 读取 agent_config 失败, 场景 {scene} 使用代码默认配置: {e}")
        return {}  # 空字典 -> agent 包回退 registry 默认值
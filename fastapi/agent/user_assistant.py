"""
用户端「开黑小助手」supervisor(代理主管) 图构建

按 agent_config 表动态组装: 仅启用(enabled=0)的子 Agent 参与路由,
提示词/温度取 DB 值(无记录回退 registry 默认); 子 Agent 全部停用时
退化为无工具单 Agent(主管直接对话并告知能力维护中)。
每次请求构建一次(纯内存组装, 开销可忽略), 配置修改无需重启即生效。
"""
from langgraph.prebuilt import create_react_agent  # 第三方: ReAct Agent 构建块

from agent import registry  # 项目内: Agent 注册表
from agent.llm import build_llm  # 项目内: 大模型工厂
from agent.registry import SCENE_USER  # 项目内: 用户端场景标识
from services import agent_service  # 项目内: Agent 运行时配置读取


def build_user_assistant(user_id: int):
    """构建用户端 supervisor 图, 返回 (编译图, 产出最终答案的节点名集合)

    参数: user_id 当前登录用户 ID(闭包绑定给订单类工具, 查询仅限本人数据)
    """
    configs = agent_service.get_effective_configs(SCENE_USER)  # DB 运行时配置(读失败自动回退默认)
    sup_spec = registry.scene_supervisor(SCENE_USER)  # 主管注册项(提示词/温度默认值来源)
    sup_cfg = configs.get(sup_spec.key) or {}  # 主管的 DB 覆盖配置(无记录则为空)
    workers = []  # 参与路由的子 Agent 列表
    for spec in registry.scene_workers(SCENE_USER):  # 组装启用的子 Agent
        cfg = configs.get(spec.key) or {}  # 该子 Agent 的 DB 覆盖配置
        if cfg.get("enabled", 0) != 0:  # enabled 字段: 0 启用 / 非 0 停用
            continue  # 停用的子 Agent 不进图
        prompt = cfg.get("prompt") or spec.default_prompt  # 提示词: DB 优先, 无记录回退注册默认
        temperature = cfg.get("temperature")  # 温度: DB 值(可能为 None)
        temperature = spec.default_temperature if temperature is None else float(temperature)  # 无 DB 值回退注册默认
        workers.append(create_react_agent(
            model=build_llm(temperature),  # 按子 Agent 温度构建模型实例
            tools=spec.tools_builder(user_id),  # 订单类工具闭包绑定 user_id 防越权
            name=spec.key,  # 图中节点名 = 注册键(supervisor 按此移交)
            prompt=prompt,
        ))
    sup_prompt = sup_cfg.get("prompt") or sup_spec.default_prompt  # 主管提示词: DB 优先, 回退注册默认
    sup_temperature = sup_cfg.get("temperature")  # 主管温度: DB 值(可能为 None)
    sup_temperature = sup_spec.default_temperature if sup_temperature is None else float(sup_temperature)  # 回退注册默认
    if not workers:  # 全部停用兑底: 退化为无工具单 Agent, 由主管直接对话
        fallback_prompt = sup_prompt + "\n注意：当前所有专职助手均已停用，请礼貌告知用户相关能力维护中，仅回答通用问题。"
        graph = create_react_agent(model=build_llm(sup_temperature), name="supervisor", prompt=fallback_prompt)  # 退化为无工具单 Agent 由主管直接回答
        return graph, {"agent"}  # react 单图(已编译)的答案节点名为 agent
    # 动态可用助手名单(与 handoff 工具保持一致, 避免主管移交到已停用的助手)
    sup_prompt += "\n当前可用助手: " + ", ".join(w.name for w in registry.scene_workers(SCENE_USER)
                                                if (configs.get(w.key) or {}).get("enabled", 0) == 0)
    graph = registry.build_supervisor(workers, build_llm(sup_temperature), sup_prompt)  # 组装 supervisor 工作流(未编译)
    return graph.compile(), {"supervisor"}  # 编译为可执行图, 答案节点固定为 supervisor
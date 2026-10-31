"""
管理端「经营分析师」supervisor 图构建

与用户端同构: 按 agent_config 动态组装指标查询 Agent(预置统计工具)与
自由查询 Agent(NL2SQL 兜底); 子 Agent 全部停用时退化为无工具单 Agent。
"""
from langgraph.prebuilt import create_react_agent  # 第三方: ReAct Agent 构建块

from agent import registry  # 项目内: Agent 注册表
from agent.llm import build_llm  # 项目内: 大模型工厂
from agent.registry import SCENE_ANALYST  # 项目内: 管理端场景标识
from services import agent_service  # 项目内: Agent 运行时配置读取


def build_analyst():
    """构建管理端 supervisor 图, 返回 (编译图, 产出最终答案的节点名集合)"""
    configs = agent_service.get_effective_configs(SCENE_ANALYST)  # DB 运行时配置(读失败自动回退默认)
    sup_spec = registry.scene_supervisor(SCENE_ANALYST)  # 主管注册项(提示词/温度默认值来源)
    sup_cfg = configs.get(sup_spec.key) or {}  # 主管的 DB 覆盖配置(无记录则为空)
    workers = []  # 参与路由的子 Agent 列表
    for spec in registry.scene_workers(SCENE_ANALYST):  # 遍历场景内全部专职子 Agent
        cfg = configs.get(spec.key) or {}  # 该子 Agent 的 DB 覆盖配置
        if cfg.get("enabled", 0) != 0:  # enabled 字段: 0 启用 / 非 0 停用
            continue  # 停用的子 Agent 不进图
        prompt = cfg.get("prompt") or spec.default_prompt  # 提示词: DB 优先, 无记录回退注册默认
        temperature = cfg.get("temperature")  # 温度: DB 值(可能为 None)
        temperature = spec.default_temperature if temperature is None else float(temperature)  # 无 DB 值回退注册默认
        workers.append(create_react_agent(
            model=build_llm(temperature),  # 按子 Agent 温度构建模型实例
            tools=spec.tools_builder(),  # 管理端工具无需绑定用户
            name=spec.key,  # 图中节点名 = 注册键(supervisor 按此移交)
            prompt=prompt,
        ))
    sup_prompt = sup_cfg.get("prompt") or sup_spec.default_prompt  # 主管提示词: DB 优先, 回退注册默认
    sup_temperature = sup_cfg.get("temperature")  # 主管温度: DB 值(可能为 None)
    sup_temperature = sup_spec.default_temperature if sup_temperature is None else float(sup_temperature)  # 回退注册默认
    if not workers:  # 全部停用兑底
        fallback_prompt = sup_prompt + "\n注意：当前所有专职助手均已停用，请礼貌告知管理员分析能力维护中。"
        graph = create_react_agent(model=build_llm(sup_temperature), name="supervisor", prompt=fallback_prompt)  # 退化为无工具单 Agent 由主管直接回答
        return graph, {"agent"}  # react 单图(已编译)的答案节点名为 agent
    # 动态可用助手名单(与 handoff 工具保持一致, 避免主管移交到已停用的助手)
    sup_prompt += "\n当前可用助手: " + ", ".join(w.name for w in registry.scene_workers(SCENE_ANALYST)
                                                if (configs.get(w.key) or {}).get("enabled", 0) == 0)
    graph = registry.build_supervisor(workers, build_llm(sup_temperature), sup_prompt)  # 组装 supervisor 工作流(未编译)
    return graph.compile(), {"supervisor"}  # 编译为可执行图, 答案节点固定为 supervisor
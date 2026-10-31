"""
大模型工厂
"""
from langchain_deepseek import ChatDeepSeek

from core.config import settings


def build_llm(temperature: float = 0.3) -> ChatDeepSeek:
    """
    构建deepseek聊天模型实例
    """
    return ChatDeepSeek(
        model=settings.deepseek_model,  # 模型名(.env 配置, 如 deepseek-flash)
        api_key=settings.deepseek_api_key,  # API 密钥(.env 配置)
        api_base=settings.deepseek_base_url,  # 接口地址(.env 配置, 可指向中转网关)
        temperature=temperature,  # 采样温度: 调用方按 Agent 注册项传入
        timeout=60,  # 单次请求超时(秒), Agent 多轮调用避免无限等待
        max_retries=1,  # 网络类失败重试 1 次(业务错误不重试)
        streaming=True,  # 显式开启流式: supervisor 图内嵌套 ainvoke 时 token 级 chunk 才能冒泡到 astream(messages)
        # 关闭思考模式: 思考模式下带 tools 的多轮请求必须完整回传 reasoning_content,
        # LangChain 不回传会报 400(The reasoning_content ... must be passed back);
        # 业务 Agent 无需思维链, 关闭后响应更快更省 token(参见 DeepSeek 思考模式文档)
        extra_body={"thinking": {"type": "disabled"}},
    )

"""
配置加载器：所有配置值只来自 fastapi/.env 文件（唯一配置入口，改配置只需改 .env）

本文件不写任何具体值，只声明配置项的名称和类型：
- 改数据库密码/密钥等 -> 只改 .env
- 新增配置项 -> 在这里加一行声明 + 在 .env 里加一行值
"""
# 标准库: 路径处理(用于定位 .env 文件)
from pathlib import Path

# 第三方: 从 .env 文件读取配置的基类与配置项
from pydantic_settings import BaseSettings, SettingsConfigDict

# .env 固定位于 fastapi/ 目录（本文件的上一级），与启动时的工作目录无关
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, env_file_encoding="utf-8", extra="ignore")  # 指定 .env 路径与编码, 忽略未声明的多余变量

    # 数据库
    db_host: str  # 数据库主机地址
    db_port: int  # 数据库端口
    db_user: str  # 数据库用户名
    db_password: str  # 数据库密码
    db_name: str  # 连接的数据库名

    # JWT 令牌
    token_header: str  # 携带 token 的请求头名称(Authorization)
    token_secret: str  # JWT 签名密钥(变更后已签发 token 全部失效)
    token_expire_minutes: int  # token 有效期(分钟)

    # API 文档
    docs_enabled: bool  # 是否开启接口文档页(/docs, /redoc, /openapi.json)

    # 上传文件基础路径
    profile: str  # 上传文件根目录(头像/通用上传都存放于此)

    deepseek_api_key: str  # API 密钥(只从 .env 读取, 切勿写入代码或提交仓库)
    deepseek_base_url: str # API地址
    deepseek_model: str # 模型名称

    @property
    def database_url(self) -> str:
        """拼接 SQLAlchemy 数据库连接串"""
        return (  # 结构: 协议 账号:密码@主机:端口/库名?字符集
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )


settings = Settings()  # 模块级单例: 导入即完成加载, 各模块统一 from core.config import settings

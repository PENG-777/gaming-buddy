"""
数据库连接（SQLAlchemy 引擎与 Session 工厂）
"""
# 第三方: SQLAlchemy 引擎创建与 ORM 声明基类/Session 工厂
from pymysql.constants import CLIENT  # 第三方: MySQL 客户端标志位(FOUND_ROWS 行数语义)
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# 项目内: 读取数据库连接配置
from core.config import settings

# pool_pre_ping/pool_recycle 检测失效连接并定期回收, 避免长连接被 MySQL 断开
engine = create_engine(
    settings.database_url,  # 连接串(由 .env 配置拼接而来)
    pool_pre_ping=True,  # 取连接前先探活, 失效自动重建
    pool_recycle=3600,  # 连接最长存活 3600 秒后回收
    pool_size=8,  # 连接池常驻连接数
    max_overflow=8,  # 高峰时允许额外超开的临时连接数
    echo=False,  # 不在控制台打印 SQL 日志
    # rowcount 按"匹配行数"统计(与 JDBC 语义一致): UPDATE 值未变化时不再返回 0 行, 避免误报"操作失败"
    connect_args={"client_flag": CLIENT.FOUND_ROWS},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)  # Session 工厂: 手动 flush/commit, 提交后对象不过期仍可访问


class Base(DeclarativeBase):
    """所有 ORM 实体的基类"""
    pass


def get_db():
    """FastAPI 依赖: 每个请求一个 Session, 请求结束自动关闭"""
    db = SessionLocal()  # 为当前请求创建独立 Session
    try:
        yield db  # 生成器依赖: 把 Session 注入路由函数使用
    finally:
        db.close()  # 请求结束(无论成败)关闭 Session 归还连接池

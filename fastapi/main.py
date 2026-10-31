"""
应用入口

启动方式(必须在本目录下执行, 避免目录名 fastapi 与第三方库冲突):
    cd fastapi
    python main.py                                     # 内置 8080 端口 + 热重载 + 彩色日志
    uvicorn main:app --host 0.0.0.0 --port 8080 --reload  # 等价命令(需自行带 --use-colors)
"""
import os  # 标准库: 进程/文件操作
import signal  # 标准库: 发送终止信号
from contextlib import asynccontextmanager  # 标准库: 异步上下文管理器(lifespan)
from multiprocessing import parent_process  # 标准库: 判断是否处于 reload 子进程

# FastAPI: 应用/请求/异常/中间件/响应/静态挂载
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text  # SQLAlchemy: 原生 SQL 文本

from core.config import settings  # 项目内: 配置
from core.database import engine  # 项目内: 数据库引擎
from core.exceptions import ApiError, AuthError  # 项目内: 自定义异常
from routers import ALL_ROUTERS  # 项目内: 聚合的全部模块路由

os.system("")  # Windows 旧控制台启用 ANSI 颜色支持(PyCharm/新终端下无副作用)

HOST = "0.0.0.0"  # 监听地址: 0.0.0.0 表示局域网可访问
PORT = 8080       # 监听端口: 需与前端 vite 代理目标一致

# ANSI 颜色码: 终端彩色日志
_GREEN = "\033[92m"  # 成功/绿色
_RED = "\033[91m"    # 失败/红色
_CYAN = "\033[96m"   # 强调/青色
_GRAY = "\033[90m"   # 次要/灰色
_RESET = "\033[0m"   # 颜色重置


# ==================== 启动校验 =====================

def check_database() -> None:
    """启动时校验数据库连接, 失败则打印原因并终止启动"""
    target = f"mysql://{settings.db_host}:{settings.db_port}/{settings.db_name}"  # 校验目标(主机:端口/库名)
    print(f"正在校验数据库连接: {target} ...")  # 进度提示
    try:
        with engine.connect() as conn:  # 从连接池取连接(自动释放)
            version = conn.execute(text("SELECT VERSION()")).scalar()  # 查询 MySQL 版本
        print(f"{_GREEN}[OK]{_RESET} 数据库连接正常 (MySQL {version})")  # 成功信息(绿色)
    except Exception as e:
        print(f"{_RED}[FAIL]{_RESET} 数据库连接失败, 请检查 fastapi/.env 中的数据库配置")  # 失败提示(红色)
        print(f"       原因: {e}")  # 异常原因
        # --reload 模式下当前进程是 reloader 的子进程, 需先终止主进程再退出, 否则 reloader 会残留占用终端和端口
        if parent_process() is not None:  # 有父进程 -> 是 reload 子进程
            try:
                os.kill(os.getppid(), signal.SIGTERM)  # 向 reloader 主进程发终止信号
            except OSError:
                pass  # 父进程已不存在则忽略
        os._exit(1)  # 立即终止(不触发 atexit 等清理钩子)


@asynccontextmanager
async def lifespan(_: FastAPI):  # 参数为 app 实例(未使用)
    # 启动: 校验数据库 -> 输出启动成功提示
    check_database()  # 失败即终止, 避免带病运行
    print(f"{_GRAY}{'=' * 46}{_RESET}")  # 分隔线(灰色)
    print(f"{_GREEN}后端服务启动成功{_RESET}")  # 标题(绿色)
    print(f"访问地址: {_CYAN}http://localhost:{PORT}{_RESET}")  # 地址(青色, 端口取自 PORT 常量)
    print(f"{_GRAY}{'=' * 46}{_RESET}")
    yield  # 分界: 之上为启动逻辑, 之下为关闭逻辑
    # 关闭: 释放数据库连接池
    engine.dispose()  # 关闭池中所有连接


app = FastAPI(  # 文档页开关由 .env 的 DOCS_ENABLED 控制(默认开启, 生产可关闭)
    title="fast", lifespan=lifespan,
    docs_url="/docs" if settings.docs_enabled else None,  # Swagger 文档
    redoc_url="/redoc" if settings.docs_enabled else None,  # ReDoc 文档
    openapi_url="/openapi.json" if settings.docs_enabled else None,  # OpenAPI 描述文件
)

# 跨域配置: 全放开
app.add_middleware(  # 注册 CORS 中间件
    CORSMiddleware,
    allow_origin_regex=".*",  # 允许任意来源
    allow_credentials=True,  # 允许携带 cookie/凭证
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
    max_age=1800,  # 预检结果缓存 30 分钟
)


# ==================== 异常处理 ====================

@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError):
    """认证失败: HTTP 401 + {code:401, msg}"""
    return JSONResponse(status_code=401, content={"code": 401, "msg": exc.msg})  # 前端据此弹重新登录框


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    """业务异常: HTTP 500 + {code:500, msg}"""
    return JSONResponse(status_code=500, content={"code": 500, "msg": exc.msg})


# 参数校验错误类型 -> 中文提示(只翻译类型本身, 严禁回显输入值, 防敏感信息泄露)
_VALIDATION_MSG_ZH = {
    "missing": "不能为空",  # 必填参数缺失
    "int_parsing": "应为整数",  # 整数解析失败
    "integer_type": "应为整数",  # 类型不符
    "string_type": "应为字符串",  # 类型不符
    "bool_parsing": "应为布尔值",  # 布尔解析失败
    "greater_than_equal": "取值过小",  # 低于下限(如 pageNum < 1)
    "greater_than": "取值过小",  # 低于开区间下限
    "less_than_equal": "取值过大",  # 超过上限(如 pageSize > 500)
    "less_than": "取值过大",  # 超过开区间上限
    "string_pattern_mismatch": "格式不正确",  # 正则不匹配
    "string_too_short": "长度不足",  # 低于最小长度(如密码少于 6 位)
    "string_too_long": "长度超出",  # 超过最大长度(与表列宽一致的约束)
    "json_invalid": "格式不正确",  # JSON 解析失败
    "datetime_parsing": "应为日期时间",  # 日期时间解析失败
}


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """请求参数校验失败: 细化到首条错误的字段与中文提示, 便于前端定位问题"""
    msg = "请求参数错误"  # 兜底文案(取不到错误明细时保持原提示)
    if exc.errors():  # 有错误明细才细化
        first = exc.errors()[0]  # 仅取第一条, 避免多字段报错刷屏
        field = str(first.get("loc", ("?",))[-1])  # loc 尾段即字段名(如 ("query","pageSize") -> pageSize)
        zh = _VALIDATION_MSG_ZH.get(first.get("type", ""), "格式不正确")  # 类型映射中文, 未收录类型统一提示
        msg = f"参数错误: {field} {zh}"  # 如: 参数错误: pageSize 应为整数
    return JSONResponse(status_code=500, content={"code": 500, "msg": msg})


@app.exception_handler(Exception)
async def fallback_error_handler(request: Request, exc: Exception):
    """兜底异常: HTTP 500"""
    return JSONResponse(status_code=500, content={"code": 500, "msg": str(exc) or "操作失败"})  # 未处理异常的最后防线


# ==================== 静态资源: /profile/** -> {profile}/ ====================

_profile_dir = os.path.abspath(settings.profile)  # 上传根目录绝对路径
os.makedirs(os.path.join(_profile_dir, "avatar"), exist_ok=True)  # 确保头像目录存在
os.makedirs(os.path.join(_profile_dir, "upload"), exist_ok=True)  # 确保上传目录存在
app.mount("/profile", StaticFiles(directory=_profile_dir), name="profile")  # 挂载: /profile/** -> 本地目录(公开访问)


# ==================== 路由注册 ====================

# 聚合注册: 模块清单维护在 routers/__init__.py 的 ALL_ROUTERS, 新增模块无需改 main.py
for _router in ALL_ROUTERS:
    app.include_router(_router)  # 逐个挂载模块路由器


# ==================== 直接运行本文件时启动 ====================
# 等价于: uvicorn main:app --host 0.0.0.0 --port 8080 --reload
# 注意: reload 模式必须传可导入字符串 "main:app", 不能传 app 对象

if __name__ == "__main__":  # 直接运行本文件时才启动
    import copy  # 标准库: 深拷贝日志配置模板
    import uvicorn  # 局部导入, 避免模块导入期依赖
    from uvicorn.config import LOGGING_CONFIG  # uvicorn 默认日志配置(dict 模板)

    log_config = copy.deepcopy(LOGGING_CONFIG)  # 复制默认配置再改, 不污染模板
    for handler in log_config["handlers"].values():  # 逐个 handler 调整输出流
        if "stream" in handler:  # 只改流输出型 handler(default/access)
            handler["stream"] = "ext://sys.stdout"  # stderr -> stdout: PyCharm 对 stderr 整行染红且 ANSI 渲染不可靠, stdout 才能按 ANSI 渲染彩色

    uvicorn.run("main:app", host=HOST, port=PORT, reload=True, use_colors=True, log_config=log_config)  # use_colors 强制彩色(管道/PyCharm 下自动检测会关闭颜色)

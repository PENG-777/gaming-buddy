"""
Token 处理

- JWT 使用 HS512 签名
- 用户信息以 JSON 字符串存放在自定义声明 user_key 中
- 退出登录的 Token 加入内存黑名单, 校验时惰性清理

黑名单为进程内存实现, 仅适用于单进程部署(uvicorn 默认单进程/--reload 子进程);
多 worker 或服务重启后黑名单清空, 已登出的 token 会复活至自然过期。
"""
import time  # 标准库: 毫秒时间戳计算

import jwt  # 第三方: PyJWT 编码/解码

from core.config import settings  # 项目内: 读取密钥与有效期配置
from schemas.vo import LoginUser  # 项目内: 登录用户快照模型

# Token 黑名单: {token: 过期时间戳(毫秒)}
_blacklisted_tokens: dict[str, int] = {}


def extract_token(authorization: str | None) -> str | None:
    """从 Authorization 请求头提取 token(自动剥离 Bearer 前缀)"""
    if not authorization:  # 请求头缺失
        return None
    if authorization.startswith("Bearer "):  # 标准格式: Bearer {token}
        return authorization[7:]  # 去掉 "Bearer " 前缀(共 7 个字符)
    return authorization  # 容错: 未带前缀时按原样使用


def create_token(login_user: LoginUser) -> str:
    """根据用户信息生成 JWT token"""
    now_ms = int(time.time() * 1000)  # 当前毫秒时间戳
    expire_ms = now_ms + settings.token_expire_minutes * 60 * 1000  # 过期毫秒时间戳 = 当前 + 配置有效期

    login_user.loginTime = now_ms  # 回写登录时间(随 token 快照携带)
    login_user.expireTime = expire_ms  # 回写过期时间(校验时直接读取)

    claims = {"user_key": login_user.model_dump_json(), "exp": expire_ms // 1000}  # 用户快照存 JSON 字符串, exp 用秒级标准声明
    return jwt.encode(claims, settings.token_secret, algorithm="HS512")  # HS512 签名, 返回 token 字符串


def parse_token(token: str) -> dict | None:
    """解析 token 返回声明字典, 失败/过期返回 None"""
    try:
        return jwt.decode(token, settings.token_secret, algorithms=["HS512"])  # 验签并校验 exp, 通过返回声明字典
    except Exception:
        return None  # 签名不符/已过期/格式错误等一律视为无效


def parse_login_user(token: str) -> LoginUser | None:
    """解析 token 中的登录用户信息, 失败返回 None"""
    claims = parse_token(token)  # 先解析出声明字典
    if not claims or "user_key" not in claims:  # 解析失败或缺少用户声明
        return None
    try:
        # extra="ignore": 忽略声明中多余的字段
        return LoginUser.model_validate_json(claims["user_key"])  # JSON 字符串反序列化为 LoginUser 模型
    except Exception:
        return None  # 模型校验失败(字段类型不符等)


def invalidate_token(token: str | None, expire_ms: int) -> None:
    """将 token 加入黑名单(退出登录时调用)"""
    if not token:  # 无 token 无需拉黑
        return
    _blacklisted_tokens[token] = expire_ms  # 记录过期时间戳, 供惰性清理判断


def is_token_blacklisted(token: str | None) -> bool:
    """检查 token 是否已失效, 已自然过期的记录惰性清理"""
    if not token:  # 无 token 不算黑名单(交给后续流程处理)
        return False
    expire_ms = _blacklisted_tokens.get(token)  # 查询黑名单记录
    if expire_ms is None:
        return False  # 不在黑名单中
    if expire_ms < time.time() * 1000:  # 记录的过期时间已过: token 本身已自然失效
        _blacklisted_tokens.pop(token, None)  # 惰性清理: 顺手移除该条记录
        return False
    return True  # 在黑名单中且未过期 -> 已登出, 视为失效

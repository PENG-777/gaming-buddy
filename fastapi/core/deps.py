"""
认证依赖

用法: 在需要登录的路由上声明 login_user: LoginUser = Depends(get_current_login_user)
校验链路: 提取 token -> 解析用户 -> 黑名单检查 -> 有效期检查, 任一失败返回 HTTP 401

文件末尾还沉淀了路由层通用依赖别名(DbDep/LoginUserDep/PageDep):
用 Annotated 收敛每个接口都要重复声明的 Depends(...) 样板, 新模块路由签名直接复用。
"""
import time  # 标准库: 时间戳(有效期校验)
from typing import Annotated  # 标准库: 类型别名标注(依赖别名)

from sqlalchemy import select
from fastapi import Depends, Header, Query  # FastAPI: 依赖注入/请求头/查询参数
from sqlalchemy.orm import Session  # 第三方: 会话类型标注
from models.entities import Companion

from core.database import get_db  # 项目内: 每请求 Session 依赖
from core.exceptions import AuthError  # 项目内: 认证失败异常
from core.security import extract_token, is_token_blacklisted, parse_login_user  # 项目内: token 提取/黑名单/解析工具
from schemas.vo import LoginUser  # 项目内: 登录用户快照模型
from services.role_service import COMPANION_ROLE_ID


def get_current_login_user(authorization: str | None = Header(default=None)) -> LoginUser:
    # 1. 提取 token
    token = extract_token(authorization)  # 剥离 Bearer 前缀
    if not token:
        raise AuthError()  # 请求头缺失/未携带 token -> 未登录

    # 2. 解析用户信息
    login_user = parse_login_user(token)  # 解析 JWT 中的用户快照
    if login_user is None:
        raise AuthError()  # 签名错误/已过期/格式非法

    # 3. 黑名单检查(退出登录后 token 失效)
    if is_token_blacklisted(token):
        raise AuthError()  # 已登出的 token 拒绝继续使用

    # 4. 有效期检查
    if login_user.expireTime is None or login_user.expireTime - time.time() * 1000 <= 0:
        raise AuthError()  # 无过期时间, 或当前毫秒时间戳已超过过期时间

    return login_user  # 校验全部通过, 返回登录用户信息


def get_current_token(authorization: str | None = Header(default=None)) -> str | None:
    """仅提取原始 token(登出等不强制认证的场景使用)"""
    return extract_token(authorization)  # 无 token 时返回 None, 不抛异常


# ==================== 路由层通用依赖别名 ====================

DbDep = Annotated[Session, Depends(get_db)]  # 请求级数据库 Session: db: DbDep
LoginUserDep = Annotated[LoginUser, Depends(get_current_login_user)]  # 登录校验: login_user: LoginUserDep


class PageParams:
    """分页查询参数依赖, 用法: page: PageDep

    从查询串读取 pageNum/pageSize(均必填), 并在参数层完成取值约束:
    页码 >= 1、1 <= 页大小 <= 500(非法值由校验错误处理器给出中文提示),
    与 core.common.paginate 内部防护形成双保险。
    """

    def __init__(
            self,
            pageNum: int = Query(..., ge=1),  # 页码(必填, 最小 1)
            pageSize: int = Query(..., ge=1, le=500),  # 每页条数(必填, 1~500)
    ):
        self.pageNum = pageNum  # 供路由/业务层直接访问 page.pageNum
        self.pageSize = pageSize  # 供路由/业务层直接访问 page.pageSize


PageDep = Annotated[PageParams, Depends()]  # 分页参数: page: PageDep

# 陪玩师角色ID
COMPANION_ROLE_ID = 3


def get_companion_scope(login_user: LoginUserDep, db: DbDep) -> int | None:
    """
    陪玩师数据范围: 陪玩师角色返回其档案ID, 其他角色返回None
    """
    if login_user.user is None or login_user.user.roleId != COMPANION_ROLE_ID:
        return None  # 不是陪玩师角色, 不做数据过滤
    return db.scalar(
        select(Companion.companion_id).where(Companion.user_id == login_user.userId)
    ) or 0


CompanionScopeDep = Annotated[int | None, Depends(get_companion_scope)]  # 陪玩师数据范围

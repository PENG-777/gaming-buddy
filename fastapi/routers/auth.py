"""
登录/注册/登出/用户信息
"""
# FastAPI: 路由/请求头/原生响应
from fastapi import APIRouter, Header, Response

from core.common import fmt_dt  # 项目内: 日期格式化
from core.deps import DbDep, LoginUserDep  # 项目内: 通用依赖(登录校验/请求级 Session)
from core.response import ajax_error, ajax_success, ajax_success_data  # 项目内: 统一响应
from core.security import create_token, extract_token, invalidate_token, parse_token  # 项目内: token 工具
from schemas.auth import LoginBody, RegisterBody  # 项目内: 登录/注册请求体
from schemas.vo import LoginUser, UserSnapshot  # 项目内: 登录用户与快照模型
from services import user_service  # 项目内: 用户业务层

router = APIRouter(tags=["auth"])  # 本模块路由器(无前缀)


def _make_snapshot(user) -> UserSnapshot:
    """User 实体 -> token 中的用户快照(不含密码, 敏感信息不进 token)"""
    return UserSnapshot(  # 逐字段搬运(键为 camelCase)
        userId=user.user_id,  # 用户ID
        userName=user.user_name,  # 用户名
        sex=user.sex,  # 性别
        avatar=user.avatar,  # 头像 URL
        createTime=fmt_dt(user.create_time),  # 创建时间(统一格式字符串)
        roleId=user.role_id,  # 角色ID
        roleName=None,  # 角色名不随 token 携带
    )


@router.post("/login")
def login(body: LoginBody, db: DbDep):
    """登录: 校验用户名密码, 成功返回 token"""
    # 1. 校验参数(为空返回业务失败, HTTP 200 + code 500)
    if (not body.userName or not body.password  # 空值/空白串均视为未填写
            or not body.userName.strip() or not body.password.strip()):
        return ajax_error("用户名或密码为空")

    # 2. 验证用户是否存在
    user = user_service.get_user_by_name(db, body.userName)  # 按用户名查用户
    if user is None:
        return ajax_error("用户名错误")  # 不提示"用户不存在", 避免账号枚举

    # 3. 验证密码(明文比对)
    if body.password != user.password:
        return ajax_error("密码错误")

    # 4. 生成 JWT 令牌
    token = create_token(LoginUser(userId=user.user_id, user=_make_snapshot(user)))  # 用户快照存入 token

    # 5. 返回 token
    return ajax_success(token=token)  # {code:200, msg, token}


@router.post("/register")
def register(body: RegisterBody, db: DbDep):
    """注册: 用户名密码非空校验 + 落库"""
    if not body.userName:
        return ajax_error("用户名不能为空")  # HTTP 200 + code 500
    if not body.password:
        return ajax_error("密码不能为空")

    if not user_service.register_user(db, body.userName, body.password):  # False 表示用户名已存在
        return ajax_error("用户名已存在, 请更换用户名后再注册")
    return ajax_success()


@router.post("/logout")
def logout(authorization: str | None = Header(default=None)):
    """退出登录: token 加入黑名单, 恒返回 200 空响应体"""
    token = extract_token(authorization)  # 提取原始 token(可能为 None)
    if token:
        claims = parse_token(token)  # 解析声明(拿过期时间)
        if claims and "exp" in claims:  # 解析成功且带 exp
            invalidate_token(token, claims["exp"] * 1000)  # 拉黑至自然过期(秒转毫秒)
    return Response(status_code=200)  # 恒 200, 空响应体


@router.get("/getInfo")
def get_info(login_user: LoginUserDep, db: DbDep):
    """获取当前登录用户信息(含角色名)"""
    user = user_service.get_user_by_id(db, login_user.userId)  # 从库里查最新信息
    return ajax_success_data(user)  # data 为 None 时不输出 data 键

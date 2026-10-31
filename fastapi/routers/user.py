"""用户管理（/system/user 前缀, 不含 profile）"""
# FastAPI: 路由/查询参数
from fastapi import APIRouter, Query

from core.common import body_fields, split_ids  # 项目内: 请求体 -> 数据库列, 删除接口 "1,2,3" 解析
from core.deps import DbDep, LoginUserDep, PageDep  # 项目内: 通用依赖(分页/登录校验/请求级 Session)
from core.response import ajax_error, ajax_success, ajax_success_data, page_data, to_ajax  # 项目内: 统一响应
from schemas.body import UserBody  # 项目内: 用户请求体
from services import user_service  # 项目内: 用户业务层

router = APIRouter(prefix="/system/user", tags=["user"])  # 模块路由器(统一前缀)


@router.get("/selectUserList")
def select_user_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # 通用依赖: 分页参数/登录校验/Session
                     userId: int | None = Query(None),  # 用户ID筛选(可选)
                     userName: str | None = Query(None)):  # 用户名模糊筛选(可选)
    """分页查询用户列表"""
    total, rows = user_service.page_users(db, page.pageNum, page.pageSize, userId, userName)  # 业务层分页查询
    return page_data(rows, total)  # {total, rows, code, msg}


@router.get("/selectUserByUserId/{userId}")
def select_user_by_user_id(userId: int, login_user: LoginUserDep, db: DbDep):
    """按用户ID查询用户详情"""
    user = user_service.get_user_by_id(db, userId)  # 按 ID 查用户(含角色名)
    # data 为 None 时不输出 data 键
    return ajax_success_data(user) if user is not None else ajax_success()


@router.post("/insertUser")
def insert_user(body: UserBody, login_user: LoginUserDep, db: DbDep):
    """新增用户"""
    return to_ajax(user_service.insert_user(db, body))  # 按受影响行数返回


@router.put("/updateUser")
def update_user(body: UserBody, login_user: LoginUserDep, db: DbDep):
    """修改用户"""
    if body.userId is None:  # 缺少主键直接失败
        return to_ajax(0)
    if body.userName is not None and user_service.user_name_taken(db, body.userName, body.userId):
        return ajax_error("用户名已存在")  # 改名查重(排除自己, 防止顶替他人账户)
    return to_ajax(user_service.update_user_by_id(db, body.userId, body_fields(body, skip=("userId",))))  # 动态更新非空字段


@router.delete("/deleteUserByUserIds/{userIds}")
def delete_user_by_user_ids(userIds: str, login_user: LoginUserDep, db: DbDep):
    """批量删除用户(路径参数逗号分隔)"""
    ids = split_ids(userIds)  # "1,2,3" -> [1,2,3]
    if login_user.userId in ids:  # 删除自己会导致当前会话悬空
        return ajax_error("不能删除当前登录用户")
    if user_service.count_admins_except(db, ids) == 0:  # 删完后管理员清零则拒绝
        return ajax_error("不能删除最后一个管理员")
    return to_ajax(user_service.delete_user_by_ids(db, ids))  # 批量删除

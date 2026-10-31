"""角色管理（/system/role 前缀）"""
# FastAPI: 路由/查询参数
from fastapi import APIRouter, Query

from core.common import split_ids  # 项目内: 删除接口 "1,2,3" 解析
from core.deps import DbDep, LoginUserDep, PageDep  # 项目内: 通用依赖(分页/登录校验/请求级 Session)
from core.response import ajax_error, ajax_success, ajax_success_data, page_data, to_ajax  # 项目内: 统一响应
from schemas.body import RoleBody  # 项目内: 角色请求体
from services import role_service  # 项目内: 角色业务层

router = APIRouter(prefix="/system/role", tags=["role"])  # 模块路由器

# 核心角色(超级管理员/普通用户/陪玩师)不允许删除
PROTECTED_ROLE_IDS = {1, 2, 3}  # 受保护的角色ID集合


@router.get("/selectAllRole")
def select_all_role(login_user: LoginUserDep, db: DbDep):
    """查询全部角色(不分页, 供下拉选择)"""
    return ajax_success_data(role_service.select_role_list(db))  # 全量角色列表


@router.get("/selectRoleList")
def select_role_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # 通用依赖: 分页参数/登录校验/Session
                     roleId: int | None = Query(None),  # 角色ID筛选(可选)
                     roleName: str | None = Query(None)):  # 角色名模糊筛选(可选)
    """分页查询角色列表"""
    total, rows = role_service.select_role_page(db, page.pageNum, page.pageSize, roleId, roleName)  # 业务层分页查询
    return page_data(rows, total)  # {total, rows, code, msg}


@router.get("/selectRoleByRoleId/{roleId}")
def select_role_by_role_id(roleId: int, login_user: LoginUserDep, db: DbDep):
    """按角色ID查询角色详情"""
    role = role_service.get_role_by_id(db, roleId)  # 按主键查询
    return ajax_success_data(role) if role is not None else ajax_success()  # 无数据时不输出 data 键


@router.post("/insertRole")
def insert_role(body: RoleBody, login_user: LoginUserDep, db: DbDep):
    """新增角色(含菜单授权)"""
    return to_ajax(role_service.insert_role(db, body))  # 按受影响行数返回


@router.put("/updateRole")
def update_role(body: RoleBody, login_user: LoginUserDep, db: DbDep):
    """修改角色(含菜单授权先删后插)"""
    return to_ajax(role_service.update_role(db, body))  # 按受影响行数返回


@router.delete("/deleteRoleByRoleIds/{roleIds}")
def delete_role_by_role_ids(roleIds: str, login_user: LoginUserDep, db: DbDep):
    """批量删除角色(路径参数逗号分隔)"""
    ids = split_ids(roleIds)  # "1,2,3" -> [1,2,3]
    for role_id in ids:  # 逐个检查受保护角色
        if role_id in PROTECTED_ROLE_IDS:  # 命中保护名单
            return ajax_error("超级管理员、普通用户和陪玩师是系统的核心角色, 不允许删除")
    return to_ajax(role_service.delete_role_by_ids(db, ids))  # 批量删除

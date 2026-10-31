"""菜单管理（/system/menu 前缀）"""
# FastAPI: 路由/查询参数
from fastapi import APIRouter, Query

from core.deps import DbDep, LoginUserDep  # 项目内: 通用依赖(登录校验/请求级 Session)
from core.response import ajax_error, ajax_success, ajax_success_data, to_ajax  # 项目内: 统一响应
from schemas.body import MenuBody  # 项目内: 菜单请求体
from services import menu_service  # 项目内: 菜单业务层

router = APIRouter(prefix="/system/menu", tags=["menu"])  # 模块路由器


@router.get("/selectMenuList")
def select_menu_list(login_user: LoginUserDep, db: DbDep,
                     menuName: str | None = Query(None)):  # 菜单名称模糊筛选(可选)
    """查询菜单列表(管理员全部, 普通用户按角色过滤)"""
    menus = menu_service.select_menu_list(db, login_user.userId, menuName)  # 业务层按角色过滤
    return ajax_success_data(menus)  # 平铺列表(树形结构由前端构建)


@router.post("/insertMenu")
def insert_menu(body: MenuBody, login_user: LoginUserDep, db: DbDep):
    """新增菜单"""
    return to_ajax(menu_service.insert_menu(db, body))  # 按受影响行数返回


@router.get("/selectMenuByMenuId/{menuId}")
def select_menu_by_menu_id(menuId: int, login_user: LoginUserDep, db: DbDep):
    """按菜单ID查询菜单详情"""
    menu = menu_service.get_menu_by_id(db, menuId)  # 按主键查询
    return ajax_success_data(menu) if menu is not None else ajax_success()  # 无数据时不输出 data 键


@router.put("/updateMenu")
def update_menu(body: MenuBody, login_user: LoginUserDep, db: DbDep):
    """修改菜单"""
    # 上级菜单不能选择自己
    if body.menuId is not None and body.menuId == body.parentId:  # 主键与父级相同
        return ajax_error("上级菜单不能选择自己")
    return to_ajax(menu_service.update_menu_by_id(db, body))  # 动态更新非空字段


@router.delete("/deleteMenuByMenuId/{menuId}")
def delete_menu_by_menu_id(menuId: int, login_user: LoginUserDep, db: DbDep):
    """删除菜单"""
    if menu_service.count_child_menus(db, menuId) > 0:  # 有子菜单的父级不允许删除
        return ajax_error("存在子菜单, 不允许删除")
    return to_ajax(menu_service.delete_menu_by_id(db, menuId))  # 级联清理 role_menu


@router.get("/selectRoleMenuTree/{roleId}")
def select_role_menu_tree(roleId: int, login_user: LoginUserDep, db: DbDep):
    """角色授权时查询: 菜单下拉树 + 该角色已勾选的菜单ID"""
    menus = menu_service.select_menu_list(db, login_user.userId, None)  # 当前用户可见菜单
    checked_keys = menu_service.select_menu_ids_by_role_id(db, roleId)  # 该角色已授权的菜单ID
    trees = menu_service.build_menu_tree_select(menus)  # 构建下拉树
    return ajax_success(checkedKeys=checked_keys, menus=trees)  # 勾选键 + 树结构


@router.get("/selectRoleMenusTree")
def select_role_menus_tree(login_user: LoginUserDep, db: DbDep):
    """查询当前用户可见的菜单下拉树"""
    menus = menu_service.select_menu_list(db, login_user.userId, None)  # 可见菜单
    return ajax_success_data(menu_service.build_menu_tree_select(menus))  # 下拉树结构


@router.get("/getRouters")
def get_routers(login_user: LoginUserDep, db: DbDep):
    """构建当前用户的前端动态路由"""
    routers = menu_service.get_routers(db, login_user.userId)  # 业务层构建路由树
    return ajax_success_data(routers)  # 前端 router.addRoute 使用

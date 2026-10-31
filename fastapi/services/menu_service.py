"""
菜单业务层（含动态路由构建）

菜单字典使用 camelCase 键(children 恒为列表)。
前端路由构建规则:
- 一级目录(M): path 加 '/' 前缀, 有子菜单时 alwaysShow=true
- 一级菜单(C): path='/', 自身 meta 不输出, 生成单个子路由(meta 含 path)
- 无组件的非一级目录(M): component='ParentView'; 其余默认 'Layout'
- 空字段不输出
"""
# 第三方: SQLAlchemy 列表达式(查询/计数)
from sqlalchemy import func, select
from sqlalchemy.orm import Session  # 第三方: 会话类型标注

from core.common import (  # 项目内: 泛型工具
    body_fields, delete_by_pks, insert_row, like_if, row_to_dict, update_by_pk, where_if,
)
from models.entities import Menu, RoleMenu, User  # 项目内: 菜单/关联/用户 ORM 实体
from schemas.body import MenuBody  # 项目内: 菜单请求体模型

# 超级管理员角色ID
ADMIN_ROLE_ID = 1  # 该角色拥有全部菜单, 查询时跳过权限过滤

# 官方客服角色ID
SERVICE_ROLE_ID = 4

_MENU_COLS = (  # 菜单查询列(列名与 row_to_dict 转换键一一对应)
    Menu.menu_id, Menu.menu_name, Menu.parent_id, Menu.menu_sort,
    Menu.path, Menu.component, Menu.menu_type, Menu.icon, Menu.create_time,
)


def menu_row_to_dict(row) -> dict:
    """数据库行 -> camelCase 菜单字典"""
    return row_to_dict(row, {"children": [], "userId": None})  # children 树构建时填充, userId 为占位字段


def _get_role_id_by_user(db: Session, user_id: int) -> int | None:
    """查询用户所属角色ID"""
    return db.scalar(select(User.role_id).where(User.user_id == user_id))  # 单值查询, 无结果返回 None


def _query_menus(db: Session, role_id: int | None, menu_name: str | None) -> list[dict]:
    """查询菜单: role_id 为 None 时查全部(管理员), 否则只查该角色授权的菜单; menuName 模糊匹配"""
    stmt = select(*_MENU_COLS).select_from(Menu)  # 显式指定主表
    if role_id is not None:  # 普通用户: 按角色授权过滤(join role_menu)
        stmt = stmt.join(RoleMenu, Menu.menu_id == RoleMenu.menu_id).where(RoleMenu.role_id == role_id)
    stmt = where_if(stmt, like_if(Menu.menu_name, menu_name))  # 拼接动态条件(值非空才生成)
    stmt = stmt.order_by(Menu.parent_id, Menu.menu_sort)  # 先按父级再按顺序, 便于构建树
    return [menu_row_to_dict(r) for r in db.execute(stmt).all()]  # 转 camelCase 字典列表


def select_menu_list(db: Session, current_user_id: int, menu_name: str | None = None) -> list[dict]:
    """查询菜单列表: 管理员显示所有菜单, 普通用户按角色过滤"""
    role_id = _get_role_id_by_user(db, current_user_id)  # 查当前用户角色
    if role_id == ADMIN_ROLE_ID:  # 管理员: 不按角色过滤, 查看全部菜单
        return _query_menus(db, None, menu_name)
    return _query_menus(db, role_id, menu_name)  # 普通用户: 只查自己角色可见的菜单


def select_menu_ids_by_role_id(db: Session, role_id: int) -> list[int]:
    """根据角色ID查询已授权菜单ID列表"""
    stmt = (  # 查询该角色在 role_menu 中授权的菜单ID
        select(Menu.menu_id)
        .join(RoleMenu, Menu.menu_id == RoleMenu.menu_id, isouter=True)
        .where(RoleMenu.role_id == role_id)
        .order_by(Menu.parent_id, Menu.menu_sort)
    )
    return [r[0] for r in db.execute(stmt).all()]  # 每行取第一列(menu_id)


# ==================== 树结构构建(下拉树) ====================

def build_menu_tree(menus: list[dict]) -> list[dict]:
    """平铺菜单列表 -> 树形结构(按 menuId 去重, 找不到父级的作为顶级)"""
    unique: list[dict] = []  # 去重后的菜单列表
    seen: set[int] = set()  # 已见过的菜单ID
    for m in menus:  # 关联查询可能产生重复行, 按 menuId 去重
        if m["menuId"] not in seen:
            seen.add(m["menuId"])
            unique.append(m)
    id_map = {m["menuId"]: m for m in unique}  # 菜单ID -> 菜单字典, 便于找父级
    roots: list[dict] = []  # 顶级菜单列表
    for m in unique:  # 遍历挂载父子关系
        m["children"] = []  # 重置, 避免重复挂载
        if m["parentId"] == 0 or m["parentId"] is None:  # parentId 为 0/空 即顶级
            roots.append(m)
        else:
            parent = id_map.get(m["parentId"])  # 查找父级菜单
            if parent is not None:
                parent["children"].append(m)  # 挂到父级的 children
            else:
                roots.append(m)  # 父级不在列表中, 暂作顶级处理
    return roots


def _menu_to_tree_select(node: dict) -> dict:
    """下拉树节点: {id, label, children(仅非空时输出)}"""
    d = {"id": node["menuId"], "label": node["menuName"]}  # 树组件约定的节点结构
    if node["children"]:  # 有子节点才递归输出 children
        d["children"] = [_menu_to_tree_select(c) for c in node["children"]]
    return d


def build_menu_tree_select(menus: list[dict]) -> list[dict]:
    """构建前端需要的下拉树结构"""
    return [_menu_to_tree_select(t) for t in build_menu_tree(menus)]  # 先建树再逐棵转换


# ==================== 动态路由构建 ====================

def get_routers(db: Session, user_id: int) -> list[dict]:
    """查询用户菜单树并构建前端路由格式"""
    role_id = _get_role_id_by_user(db, user_id)  # 查用户角色
    if role_id == ADMIN_ROLE_ID:  # 管理员: 全部菜单
        menus = _query_menus(db, None, None)
    else:  # 普通用户: 角色可见菜单
        menus = _query_menus(db, role_id, None)

    # 补全缺失的父级目录: 角色可能只授权了子菜单, 不补全会导致菜单丢失
    own_ids = {m["menuId"] for m in menus}  # 当前已查到的菜单ID集合
    missing_parent_ids = {  # 父级不在结果中的 parentId 集合(排除顶级)
        m["parentId"] for m in menus
        if m["parentId"] not in (None, 0) and m["parentId"] not in own_ids
    }
    if missing_parent_ids:  # 存在缺失父级则补查
        rows = db.execute(select(*_MENU_COLS).where(Menu.menu_id.in_(missing_parent_ids))).all()
        menus.extend(menu_row_to_dict(r) for r in rows)  # 追加到菜单列表

    # 统一初始化 children 后再挂载父子关系(先挂载后初始化会丢失子菜单)
    menu_map = {m["menuId"]: m for m in menus}  # 菜单ID -> 菜单字典
    for m in menus:
        m["children"] = []  # 先统一初始化
    roots: list[dict] = []  # 顶级菜单列表
    for m in menus:  # 再挂载父子关系
        if m["parentId"] == 0:  # 顶级菜单
            roots.append(m)
        else:
            parent = menu_map.get(m["parentId"])  # 查找父级
            if parent is not None:
                parent["children"].append(m)  # 挂到父级 children

    return _build_routers(roots)  # 树形结构 -> 前端路由格式


def _build_routers(menus: list[dict]) -> list[dict]:
    """树形菜单 -> 前端路由格式"""
    routers: list[dict] = []  # 前端路由结果列表
    for m in menus:  # 逐个菜单转换
        parent_is_root = m["parentId"] == 0  # 是否一级菜单/目录(父级为 0)
        menu_type = m["menuType"]  # 菜单类型: M 目录 / C 菜单
        component = m["component"]  # 配置的组件路径(可能为空)

        # 路由名称: 顶级菜单加菜单ID后缀保证唯一
        router_name = m["path"]  # 默认用 path 作为路由名
        if parent_is_root and m["menuId"] is not None:  # 顶级且有菜单ID
            router_name = f"{m['path']}_{m['menuId']}"  # 拼接后缀避免同名冲突

        # 路由地址: 一级目录加 '/' 前缀; 一级菜单中首页固定根路径, 其余用 '/' + 自身 path
        router_path = m["path"]  # 默认原样使用
        if parent_is_root and menu_type == "M":  # 一级目录: 加 '/' 前缀
            router_path = "/" + m["path"]
        elif parent_is_root and menu_type == "C":  # 一级菜单
            # 首页(index)保持根路径 '/' 承载(permission.js 根路径重定向依赖它);
            # 其余一级菜单用 '/' + 自身 path, 避免多个一级菜单共用 '/' 导致顶部高亮互相干扰
            router_path = "/" if m["path"] == "index" else "/" + (m["path"] or "")

        # 组件: 有配置且非一级菜单用配置值; 无配置的非一级目录用 ParentView; 其余 Layout
        router_component = "Layout"  # 默认主布局
        if component and not (parent_is_root and menu_type == "C"):  # 有组件配置且非一级菜单
            router_component = component  # 用配置的具体页面组件
        elif not component and (not parent_is_root and menu_type == "M"):  # 无组件的非一级目录
            router_component = "ParentView"  # 空壳父级视图

        router: dict = {  # 单个路由节点
            "name": router_name,  # 路由名称(唯一)
            "path": router_path,  # 路由地址
            "component": router_component,  # 组件(布局/页面/ParentView)
            "meta": {"title": m["menuName"], "icon": m["icon"]},  # 标题与图标
        }

        children = m["children"]  # 子菜单列表
        if children and menu_type == "M":  # 目录且有子菜单
            # 目录: 展开显示, 递归处理子菜单
            router["alwaysShow"] = True  # 恒显示目录(即使只有一个子项)
            router["children"] = _build_routers(children)  # 递归转换子菜单
        elif parent_is_root and menu_type == "C":  # 一级菜单特殊处理
            # 一级菜单: 自身不输出 meta, 由唯一子路由承载页面
            router.pop("meta")  # 移除自身 meta
            child: dict = {"name": m["path"]}  # 构造唯一子路由
            if m["path"] is not None:  # 路径非空才输出
                # 首页: 子路由 path='index' 挂在 '/' 下; 其余一级菜单: 空 path 直接挂载在 '/xxx' 上
                child["path"] = "index" if m["path"] == "index" else ""
            if component is not None:  # 组件非空才输出
                child["component"] = component
            child["meta"] = {"title": m["menuName"], "icon": m["icon"], "path": m["path"]}  # meta 由子路由携带
            router["children"] = [child]  # 挂为唯一子路由

        routers.append(router)  # 加入结果列表
    return routers


# ==================== 菜单 CRUD ====================

def get_menu_by_id(db: Session, menu_id: int) -> dict | None:
    """按主键查询菜单"""
    row = db.execute(select(*_MENU_COLS).where(Menu.menu_id == menu_id)).first()  # 按主键查第一条
    return menu_row_to_dict(row) if row else None  # 无记录返回 None


def insert_menu(db: Session, body: MenuBody) -> int:
    """新增菜单"""
    return insert_row(db, Menu, body_fields(body, skip=("menuId",)))  # 泛型单表插入(直接提交)


def update_menu_by_id(db: Session, body: MenuBody) -> int:
    """按菜单ID更新非 null 字段"""
    if body.menuId is None:  # 缺少主键无法定位记录
        return 0
    return update_by_pk(db, Menu, Menu.menu_id, body.menuId, body_fields(body, skip=("menuId",)))  # 泛型按主键动态更新


def delete_menu_by_id(db: Session, menu_id: int) -> int:
    """删除菜单(外键 ON DELETE CASCADE 自动清理 role_menu 关联记录)"""
    return delete_by_pks(db, Menu, Menu.menu_id, [menu_id])  # 泛型按主键删除


def count_child_menus(db: Session, menu_id: int) -> int:
    """统计菜单的直接子菜单数量(删除前检查, 防止删父级留下孤儿子菜单)"""
    return db.scalar(select(func.count()).select_from(Menu).where(Menu.parent_id == menu_id)) or 0
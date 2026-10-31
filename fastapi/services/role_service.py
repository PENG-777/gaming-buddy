"""
角色业务层

insert_role / update_role 同时操作 role 与 role_menu 两张表, 在同一事务中完成保证原子性。
"""
# 第三方: SQLAlchemy 列表达式(update_role 事务内直接使用 delete/update)
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session  # 第三方: 会话类型标注

from core.common import (  # 项目内: 泛型工具
    body_fields, delete_by_pks, eq_if, like_if, paginate, row_to_dict, where_if,
)
from models.entities import Role, RoleMenu  # 项目内: 角色/角色菜单 ORM 实体
from schemas.body import RoleBody  # 项目内: 角色请求体模型

# 陪玩师角色ID(当管理员新增一个陪玩师后在用户表中应该自动增加一个陪玩师角色的用户)
COMPANION_ROLE_ID = 3

_ROLE_COLS = (Role.role_id, Role.role_name, Role.role_sort, Role.remark, Role.create_time)  # 角色查询列


def role_row_to_dict(row) -> dict:
    """数据库行 -> camelCase 字典"""
    return row_to_dict(row, {"menuIds": None})  # menuIds 为占位字段(按需另行查询填充)


def _base_query(role_id: int | None, role_name: str | None):
    """构造角色基础查询(动态条件, 供列表/分页复用)"""
    stmt = select(*_ROLE_COLS)  # 查询角色列
    stmt = where_if(stmt, eq_if(Role.role_id, role_id), like_if(Role.role_name, role_name))  # 拼接动态条件(值非空才生成)
    return stmt.order_by(Role.role_sort)  # 按显示顺序排序


def select_role_list(db: Session, role_id: int | None = None,
                     role_name: str | None = None) -> list[dict]:
    """查询角色列表(不分页, 按 role_sort 排序)"""
    rows = db.execute(_base_query(role_id, role_name)).all()  # 执行查询取全部行
    return [role_row_to_dict(r) for r in rows]  # 转为 camelCase 字典列表


def select_role_page(db: Session, page_num: int, page_size: int,
                     role_id: int | None = None, role_name: str | None = None) -> tuple[int, list[dict]]:
    stmt = _base_query(role_id, role_name)  # 复用基础查询
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [role_row_to_dict(r) for r in rows]  # 总数 + 当前页字典列表


def get_role_by_id(db: Session, role_id: int) -> dict | None:
    row = db.execute(select(*_ROLE_COLS).where(Role.role_id == role_id)).first()  # 按主键查第一条
    return role_row_to_dict(row) if row else None  # 无记录返回 None


def insert_role(db: Session, body: RoleBody) -> int:
    """新增角色 + 角色菜单关联(事务保证原子性)"""
    role = Role(**body_fields(body, skip=("roleId", "menuIds")))  # 构造角色实体(请求体 -> 数据库列)
    db.add(role)  # 加入会话(未提交)
    db.flush()  # 回填自增主键
    rows = 1  # 默认影响行数: 角色本身 1 行
    if body.menuIds:  # 携带菜单授权列表
        db.add_all([RoleMenu(role_id=role.role_id, menu_id=mid) for mid in body.menuIds])  # 批量构造角色菜单关联
        rows = len(body.menuIds)  # 影响行数取关联记录数
    db.commit()  # role + role_menu 同一事务一次性提交(保证原子性)
    return rows


def update_role(db: Session, body: RoleBody) -> int:
    """修改角色 + 先删后插角色菜单关联(事务保证原子性)

    menuIds 为 None 时不动作关联(保持原授权), 传空列表才清空全部授权。
    """
    if body.roleId is None:  # 缺少主键无法定位记录
        return 0
    fields = body_fields(body, skip=("roleId", "menuIds"))  # 提取非 null 字段
    if not fields and body.menuIds is None:  # 既无可更新字段也未传授权列表, 无事可做
        return 0
    if fields:  # 有可更新字段才执行更新
        db.execute(update(Role).where(Role.role_id == body.roleId).values(**fields))  # 更新角色本身
    rows = 1  # 默认影响行数: 角色本身 1 行
    if body.menuIds is not None:  # 传了 menuIds 才重建关联(None 表示不动作, [] 表示清空)
        db.execute(delete(RoleMenu).where(RoleMenu.role_id == body.roleId))  # 先删除旧的角色菜单关联
        if body.menuIds:  # 携带菜单授权列表
            db.add_all([RoleMenu(role_id=body.roleId, menu_id=mid) for mid in body.menuIds])  # 再插入新的关联
            rows = len(body.menuIds)  # 影响行数取关联记录数
    db.commit()  # 更新 + 删旧 + 插新 同一事务一次性提交(保证原子性)
    return rows


def delete_role_by_ids(db: Session, role_ids: list[int]) -> int:
    """删除角色(外键 ON DELETE CASCADE 自动清理 role_menu 关联记录)"""
    return delete_by_pks(db, Role, Role.role_id, role_ids)  # 泛型按主键批量删除

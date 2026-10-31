"""
用户业务层

列表/单查关联 role 表取 role_name。
"""
# 第三方: SQLAlchemy 列表达式(查询/计数)与唯一约束冲突异常
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session  # 第三方: 会话类型标注

from core.common import (  # 项目内: 泛型工具
    body_fields, delete_by_pks, eq_if, insert_row, like_if, paginate, row_to_dict, update_by_pk, where_if,
)
from models.entities import Role, User  # 项目内: 用户/角色 ORM 实体
from schemas.body import UserBody  # 项目内: 用户请求体模型

# 关联查询需要的 user 列 + role_name(不含 password, 接口不外泄密码)
_USER_COLS = (  # 列顺序与 row_to_dict 的取值键一一对应
    User.user_id, User.user_name, User.sex, User.avatar,
    User.create_time, User.role_id, Role.role_name,
)


def user_row_to_dict(row) -> dict:
    """数据库行 -> camelCase 字典"""
    return row_to_dict(row)  # 无占位字段, 直接用泛型转换


def get_user_by_name(db: Session, user_name: str) -> User | None:
    """通过用户名查询用户(全列)"""
    return db.scalar(select(User).where(User.user_name == user_name))  # 按用户名查整行, 无结果返回 None


def get_user_password(db: Session, user_id: int) -> str | None:
    """通过用户ID查询密码(单列, 供改密时比对使用, 不随接口外泄)"""
    return db.scalar(select(User.password).where(User.user_id == user_id))


def get_user_avatar(db: Session, user_id: int) -> str | None:
    """通过用户ID查询头像 URL(替换头像后清理旧文件用)"""
    return db.scalar(select(User.avatar).where(User.user_id == user_id))


def user_name_taken(db: Session, user_name: str, exclude_user_id: int | None = None) -> bool:
    """用户名是否已被占用(exclude_user_id 用于改名场景排除自己)"""
    stmt = select(User.user_id).where(User.user_name == user_name)
    if exclude_user_id is not None:  # 改名时不算自己占用自己的名字
        stmt = stmt.where(User.user_id != exclude_user_id)
    return db.scalar(stmt) is not None


def get_user_by_id(db: Session, user_id: int) -> dict | None:
    """通过用户ID查询用户信息(left join role 取 role_name)"""
    stmt = (  # 关联 role 表取 role_name(left join, 用户无角色也不丢失)
        select(*_USER_COLS)
        .join(Role, User.role_id == Role.role_id, isouter=True)
        .where(User.user_id == user_id)
    )
    row = db.execute(stmt).first()  # 取第一条(主键查询最多一条)
    return user_row_to_dict(row) if row else None  # 无记录返回 None


def register_user(db: Session, user_name: str, password: str) -> bool:
    """注册用户: 用户名重复返回 False(失败提示由路由层返回 HTTP 200 + code 500)"""
    if get_user_by_name(db, user_name) is not None:  # 用户名已存在
        return False
    try:  # 新用户默认 role_id=2(数据库默认值); 并发注册同名由唯一索引兜底
        db.add(User(user_name=user_name, password=password))
        db.commit()  # 单条单表写操作直接提交
    except IntegrityError:  # 撞唯一索引(user_name 唯一约束)
        db.rollback()  # 回滚保持 Session 可用
        return False
    return True


def page_users(db: Session, page_num: int, page_size: int,
               user_id: int | None, user_name: str | None) -> tuple[int, list[dict]]:
    """分页查询用户列表"""
    stmt = select(*_USER_COLS).join(Role, User.role_id == Role.role_id, isouter=True)  # 基础查询: 用户列 + left join 角色名
    stmt = where_if(stmt, eq_if(User.user_id, user_id), like_if(User.user_name, user_name))  # 拼接动态条件(值非空才生成)
    stmt = stmt.order_by(User.user_id)  # 按 ID 排序
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [user_row_to_dict(r) for r in rows]  # 总数 + 当前页 camelCase 字典列表


def insert_user(db: Session, body: UserBody) -> int:
    """新增用户(仅插入非 null 字段, 主键/创建时间由数据库生成)"""
    fields = body_fields(body, skip=("userId", "createTime"))  # 请求体 -> 数据库列(保持旧行为: 不写 createTime)
    return insert_row(db, User, fields)  # 泛型单表插入(直接提交)


def update_user_by_id(db: Session, user_id: int, fields: dict) -> int:
    """按非 null 字段动态更新, fields 键为数据库列名"""
    return update_by_pk(db, User, User.user_id, user_id, fields)  # 泛型按主键动态更新


def reset_user_pwd(db: Session, user_id: int, new_password: str) -> int:
    return update_by_pk(db, User, User.user_id, user_id, {"password": new_password})  # 按主键更新密码


def update_user_avatar(db: Session, user_id: int, avatar: str) -> int:
    return update_by_pk(db, User, User.user_id, user_id, {"avatar": avatar})  # 按主键更新头像 URL


def delete_user_by_ids(db: Session, user_ids: list[int]) -> int:
    """删除用户(外键 ON DELETE CASCADE 自动清理关联记录)"""
    return delete_by_pks(db, User, User.user_id, user_ids)  # 泛型按主键批量删除


def count_admins_except(db: Session, exclude_ids: list[int]) -> int:
    """统计排除待删除用户后的管理员数量(防止删光最后一个管理员)"""
    stmt = select(func.count()).select_from(User).where(User.role_id == 1)  # role_id=1 即管理员
    if exclude_ids:  # 排除本次要删除的用户
        stmt = stmt.where(User.user_id.not_in(exclude_ids))
    return db.scalar(stmt) or 0

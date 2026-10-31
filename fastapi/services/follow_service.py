"""
用户关注业务层

follow(用户关注) 单表模块:
- 管理端: 分页列表(join user/companion 取用户与陪玩师信息)、批量删除
- 用户端: 关注/取关切换(校验陪玩师存在且启用)、我的关注列表(join companion/game_category)
- 关注为用户行为, 管理端只读查看 + 删除, 不提供代录; (user_id, companion_id) 唯一索引防重复关注
"""
from sqlalchemy import select  # 第三方: SQLAlchemy 列表达式
from sqlalchemy.orm import Session  # 第三方: 会话类型标注

from core.common import (  # 项目内: 泛型工具
    delete_by_pks, like_if, paginate, row_to_dict, where_if,
)
from models.entities import Companion, Follow, GameCategory, User  # 项目内: 用户关注相关 ORM 实体

# 管理端查询列(join user 取用户名, join companion 取陪玩师信息, 转换键一一对应)
_FOLLOW_COLS = (
    Follow.id, User.user_name,
    Follow.companion_id, Companion.nick_name, Companion.avatar, Companion.gender,
    Companion.city, Companion.price, Follow.create_time,
)


def select_follow_page(db: Session, page_num: int, page_size: int,
                       user_name: str | None = None, nick_name: str | None = None) -> tuple[int, list[dict]]:
    """分页查询关注列表(join user/companion, 供管理端查看)

    参数: db 请求级 Session / page_num 页码 / page_size 每页条数 / user_name 用户名模糊(可选) / nick_name 昵称模糊(可选)
    """
    stmt = select(*_FOLLOW_COLS).select_from(Follow)  # 显式指定主表
    stmt = stmt.join(User, Follow.user_id == User.user_id)  # 内连接用户(取用户名/头像)
    stmt = stmt.join(Companion, Follow.companion_id == Companion.companion_id)  # 内连接陪玩师(取昵称/头像等)
    stmt = where_if(  # 拼接动态条件(值非空才生成)
        stmt,
        like_if(User.user_name, user_name),
        like_if(Companion.nick_name, nick_name),
    )
    stmt = stmt.order_by(Follow.id.desc())  # 按记录ID倒序(最新关注的在前)
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [row_to_dict(r) for r in rows]  # 总数 + 当前页字典列表


def delete_follow_by_ids(db: Session, follow_ids: list[int]) -> int:
    """批量删除关注记录

    参数: db 请求级 Session / follow_ids 记录ID列表; 返回受影响行数
    """
    return delete_by_pks(db, Follow, Follow.id, follow_ids)  # 泛型按主键批量删除


def toggle_follow(db: Session, user_id: int, companion_id: int) -> tuple[bool, str | None]:
    """
    关注/取关切换; 如果某个用户已经关注了某个陪玩师, 当点击后为取关, 如果没有关注, 点击后为关注
    """
    companion = db.scalar(  # 陪玩师存在且启用才可关注
        select(Companion.companion_id).where(Companion.companion_id == companion_id, Companion.status == 0)
    )
    if companion is None:
        return False, "陪玩师不存在或已停用"
    row = db.scalar(  # 查询当前用户对该陪玩师的关注记录
        select(Follow).where(Follow.user_id == user_id, Follow.companion_id == companion_id)
    )
    if row is not None:  # 已关注 -> 取消关注
        db.delete(row)  # 删除关注记录
        db.commit()
        return False, None  # 返回已取消关注
    db.add(Follow(user_id=user_id, companion_id=companion_id))  # 未关注 -> 关注(时间走数据库默认值)
    db.commit()
    return True, None  # 返回已关注


def select_my_follows(db: Session, user_id: int) -> list[dict]:
    """我的关注: 当前用户关注列表(join companion/game_category 取陪玩师详情与主游戏名)

    参数: db 请求级 Session / user_id 用户ID
    """
    stmt = (
        select(Follow.companion_id, Companion.nick_name, Companion.avatar, Companion.gender,
               Companion.city, Companion.tags, Companion.certified, Companion.price,
               Companion.main_rank, GameCategory.game_name.label("main_game_name"), Follow.create_time)
        .select_from(Follow)
        .join(Companion, Follow.companion_id == Companion.companion_id)  # 内连接陪玩师
        .join(GameCategory, Companion.main_game_id == GameCategory.game_id, isouter=True)  # 左连接主游戏(可能未设置)
        .where(Follow.user_id == user_id)
        .order_by(Follow.id.desc())  # 最新关注的在前
    )
    return [row_to_dict(r) for r in db.execute(stmt).all()]  # camelCase 字典列表

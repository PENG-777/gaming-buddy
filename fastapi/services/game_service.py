"""
游戏分类业务层
"""
from sqlalchemy import select
from sqlalchemy.orm import Session  # 第三方: 会话类型标注
from core.common import (  # 项目内: 泛型工具
    body_fields, delete_by_pks, eq_if, like_if, paginate, row_to_dict, where_if, insert_row, update_by_pk,
)
from models.entities import GameCategory  # 游戏分类实体
from schemas.body import GameBody  # 游戏分类请求体

_GAME_COLS = (GameCategory.game_id, GameCategory.game_name, GameCategory.image, GameCategory.tags,
              GameCategory.description, GameCategory.status, GameCategory.game_sort, GameCategory.create_time)


def game_row_to_dict(row) -> dict:
    """数据库行 -> camelCase 字典"""
    return row_to_dict(row)


def _base_query(game_name: str | None, status: int | None):
    """
    构造游戏分类基础查询(动态条件, 供列表/分页复用)
    """
    stmt = select(*_GAME_COLS)  # 查询游戏分类表中的所有
    stmt = where_if(stmt, like_if(GameCategory.game_name, game_name), eq_if(GameCategory.status, status))  # 拼接动态条件
    return stmt.order_by(GameCategory.game_sort)  # 根据排序字段正序排序


def select_game_list(db: Session, game_name: str | None = None, status: int | None = None) -> list[dict]:
    """
    查询游戏分类列表(不分页, 按照显示顺序排列)
    """
    rows = db.execute(_base_query(game_name, status)).all()
    return [game_row_to_dict(r) for r in rows]


def select_game_page(db: Session, page_num: int, page_size: int,
                     game_name: str | None = None, status: int | None = None) -> tuple[int, list[dict]]:
    """
    分页查询游戏分类列表
    """
    stmt = _base_query(game_name, status)  # 复用基础查询
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [game_row_to_dict(r) for r in rows]  # 总数 + 当前页字典列表


def get_game_by_id(db: Session, game_id: int) -> dict | None:
    """
    根据游戏ID查询详情信息
    """
    row = db.execute(select(*_GAME_COLS).where(GameCategory.game_id == game_id)).first()  # 按主键查第一条
    return game_row_to_dict(row) if row else None  # 无记录返回 None


def name_exists(db: Session, game_name: str | None, exclude_id: int | None = None) -> bool:
    """
    游戏名称是否已存在
    """
    if not game_name:
        return False
    stmt = select(GameCategory.game_id).where(GameCategory.game_name == game_name)  # 根据游戏名称查询对应的ID
    if exclude_id is not None:  # 更新场景排除自身
        stmt = stmt.where(GameCategory.game_id != exclude_id)
    return db.scalar(stmt) is not None  # 如果查到既存在


def insert_game(db: Session, body: GameBody) -> int:
    """
    新增游戏分类
    """
    return insert_row(db, GameCategory, body_fields(body, skip=("gameId",)))


def update_game_by_id(db: Session, body: GameBody) -> int:
    """
    根据游戏ID更新游戏信息
    """
    if body.gameId is None:  # 缺少主键无法更新
        return 0
    return update_by_pk(db, GameCategory, GameCategory.game_id, body.gameId, body_fields(body, skip=("gameId",)))


def delete_game_by_ids(db: Session, game_ids: list[int]) -> int:
    """
    批量删除游戏分类
    """
    return delete_by_pks(db, GameCategory, GameCategory.game_id, game_ids)








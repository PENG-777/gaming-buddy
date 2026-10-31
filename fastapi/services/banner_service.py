"""
首页轮播图业务层
"""
from sqlalchemy import select
from sqlalchemy.orm import Session  # 第三方: 会话类型标注
from core.common import (  # 项目内: 泛型工具
    body_fields, delete_by_pks, eq_if, like_if, paginate, row_to_dict, where_if, insert_row, update_by_pk,
)
from models.entities import Banner  # 首页轮播图实体
from schemas.body import BannerBody  # 轮播图请求体

_BANNER_COLS = (
    Banner.banner_id, Banner.title, Banner.subtitle, Banner.tag, Banner.image,
    Banner.bg_color, Banner.fg_color, Banner.link_text, Banner.link_url,
    Banner.status, Banner.banner_sort, Banner.create_time,
)


def select_banner_page(db: Session, page_num: int, page_size: int,
                       title: str | None = None, status: int | None = None) -> tuple[int, list[dict]]:
    """
    分页查询轮播图列表
    """
    stmt = select(*_BANNER_COLS)  # 查询轮播图列
    stmt = where_if(  # 拼接动态条件
        stmt,
        like_if(Banner.title, title),
        eq_if(Banner.status, status)
    )
    stmt = stmt.order_by(Banner.banner_sort.asc())  # 根据序号字段排序
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [row_to_dict(r) for r in rows]  # 总数 + 当前页字典列表


def get_banner_by_id(db: Session, banner_id: int) -> dict | None:
    """
    根据轮播图ID查询详情信息
    """
    row = db.execute(select(*_BANNER_COLS).where(Banner.banner_id == banner_id)).first()  # 按主键查第一条
    return row_to_dict(row) if row else None  # 无记录返回 None


def insert_banner(db: Session, body: BannerBody) -> int:
    """
    新增轮播图
    """
    return insert_row(db, Banner, body_fields(body, skip=("bannerId",)))


def update_banner_by_id(db: Session, body: BannerBody) -> int:
    """
    根据轮播图ID更新轮播图信息
    """
    if body.bannerId is None:  # 缺少主键无法更新
        return 0
    return update_by_pk(db, Banner, Banner.banner_id, body.bannerId, body_fields(body, skip=("bannerId",)))


def delete_banner_by_ids(db: Session, banner_ids: list[int]) -> int:
    """
    批量删除轮播图
    """
    return delete_by_pks(db, Banner, Banner.banner_id, banner_ids)


# =========================== 用户端 ===========================

def select_published_banners(db: Session) -> list[dict]:
    """
    用户端轮播图列表: 仅查询"启用"状态的轮播图
    """
    stmt = (
        select(*_BANNER_COLS).where(Banner.status == 0).order_by(Banner.banner_sort.asc())
    )
    return [row_to_dict(r) for r in db.execute(stmt).all()]

"""
打赏礼物业务层
"""
from sqlalchemy import select  # 第三方: SQLAlchemy 列表达式
from sqlalchemy.orm import Session  # 第三方: 会话类型标注

from core.common import (  # 项目内: 泛型工具
    body_fields, delete_by_pks, eq_if, insert_row, like_if, paginate, row_to_dict, update_by_pk, where_if,
)
from models.entities import Gift  # 项目内: 打赏礼物 ORM 实体
from schemas.body import GiftBody  # 项目内: 打赏礼物请求体模型

_GIFT_COLS = (  # 礼物查询列(列名与 row_to_dict 转换键一一对应)
    Gift.gift_id, Gift.gift_name, Gift.image,
    Gift.price, Gift.status, Gift.gift_sort, Gift.create_time,
)


def gift_row_to_dict(row) -> dict:
    """数据库行 -> camelCase 字典"""
    return row_to_dict(row)  # 无占位字段, 直接转换


def select_gift_page(db: Session, page_num: int, page_size: int,
                     gift_name: str | None = None, status: int | None = None) -> tuple[int, list[dict]]:
    """分页查询礼物列表(管理端)

    参数: db 请求级 Session / page_num 页码 / page_size 每页条数 / gift_name 名称模糊(可选) / status 状态(可选)
    """
    stmt = select(*_GIFT_COLS)  # 查询礼物列
    stmt = where_if(stmt, like_if(Gift.gift_name, gift_name), eq_if(Gift.status, status))  # 拼接动态条件(值非空才生成)
    stmt = stmt.order_by(Gift.gift_sort, Gift.gift_id)  # 按显示顺序排序, 同序号按ID
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [gift_row_to_dict(r) for r in rows]  # 总数 + 当前页字典列表


def get_gift_by_id(db: Session, gift_id: int) -> dict | None:
    """按礼物ID查询礼物详情(管理端修改回显)

    参数: db 请求级 Session / gift_id 礼物ID; 无记录返回 None
    """
    row = db.execute(select(*_GIFT_COLS).where(Gift.gift_id == gift_id)).first()  # 按主键查第一条
    return gift_row_to_dict(row) if row else None  # 无记录返回 None


def select_enabled_gifts(db: Session) -> list[dict]:
    """查询全部启用礼物(用户端打赏弹窗, 不分页按显示顺序排序)

    参数: db 请求级 Session; 停用礼物对用户端不可见
    """
    stmt = select(*_GIFT_COLS).where(Gift.status == 0).order_by(Gift.gift_sort, Gift.gift_id)  # 只查启用
    return [gift_row_to_dict(r) for r in db.execute(stmt).all()]  # camelCase 字典列表


def name_exists(db: Session, gift_name: str | None, exclude_id: int | None = None) -> bool:
    """礼物名称是否已存在(exclude_id 用于更新时排除自身)

    参数: db 请求级 Session / gift_name 待查重名称 / exclude_id 排除的礼物ID(可选)
    """
    if not gift_name:  # 空名称不参与查重(必填校验由路由层负责)
        return False
    stmt = select(Gift.gift_id).where(Gift.gift_name == gift_name)  # 按名称查ID
    if exclude_id is not None:  # 更新场景排除自身
        stmt = stmt.where(Gift.gift_id != exclude_id)
    return db.scalar(stmt) is not None  # 查到即存在


def insert_gift(db: Session, body: GiftBody) -> int:
    """新增礼物

    参数: db 请求级 Session / body 礼物请求体; 返回受影响行数
    """
    return insert_row(db, Gift, body_fields(body, skip=("giftId",)))  # 泛型单表插入(直接提交)


def update_gift_by_id(db: Session, body: GiftBody) -> int:
    """按礼物ID更新非 null 字段

    参数: db 请求级 Session / body 请求体(giftId 必填定位, 其余非 null 字段更新); 返回受影响行数
    """
    if body.giftId is None:  # 缺少主键无法定位记录
        return 0
    return update_by_pk(db, Gift, Gift.gift_id, body.giftId, body_fields(body, skip=("giftId",)))  # 泛型按主键动态更新


def delete_gift_by_ids(db: Session, gift_ids: list[int]) -> int:
    """批量删除礼物

    参数: db 请求级 Session / gift_ids 礼物ID列表; 返回受影响行数(历史打赏记录存快照不受影响)
    """
    return delete_by_pks(db, Gift, Gift.gift_id, gift_ids)  # 泛型按主键批量删除

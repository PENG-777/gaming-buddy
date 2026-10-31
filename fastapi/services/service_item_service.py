"""
服务项目业务层
"""
from sqlalchemy import select
from sqlalchemy.orm import Session  # 第三方: 会话类型标注
from core.common import (  # 项目内: 泛型工具
    body_fields, delete_by_pks, eq_if, like_if, paginate, row_to_dict, where_if, insert_row, update_by_pk,
)
from models.entities import ServiceItem  # 服务项目实体
from schemas.body import ServiceItemBody  # 服务项目请求体

_SERVICE_ITEM_COLS = (ServiceItem.service_id, ServiceItem.service_name, ServiceItem.image,
                      ServiceItem.description, ServiceItem.status, ServiceItem.service_sort, ServiceItem.create_time)


def service_item_row_to_dict(row) -> dict:
    """数据库行 -> camelCase 字典"""
    return row_to_dict(row)


def _base_query(service_name: str | None, status: int | None):
    """
    构造服务项目基础查询(动态条件, 供列表/分页复用)
    """
    stmt = select(*_SERVICE_ITEM_COLS)  # 查询服务项目表中的所有
    stmt = where_if(stmt, like_if(ServiceItem.service_name, service_name), eq_if(ServiceItem.status, status))  # 拼接动态条件
    return stmt.order_by(ServiceItem.service_sort)  # 根据排序字段正序排序


def select_service_item_list(db: Session, service_name: str | None = None, status: int | None = None) -> list[dict]:
    """
    查询服务项目列表(不分页, 按照显示顺序排列)
    """
    rows = db.execute(_base_query(service_name, status)).all()
    return [service_item_row_to_dict(r) for r in rows]


def select_service_item_page(db: Session, page_num: int, page_size: int,
                             service_name: str | None = None, status: int | None = None) -> tuple[int, list[dict]]:
    """
    分页查询服务项目列表
    """
    stmt = _base_query(service_name, status)  # 复用基础查询
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [service_item_row_to_dict(r) for r in rows]  # 总数 + 当前页字典列表


def get_service_item_by_id(db: Session, service_id: int) -> dict | None:
    """
    根据服务项目ID查询详情信息
    """
    row = db.execute(select(*_SERVICE_ITEM_COLS).where(ServiceItem.service_id == service_id)).first()  # 按主键查第一条
    return service_item_row_to_dict(row) if row else None  # 无记录返回 None


def name_exists(db: Session, service_name: str | None, exclude_id: int | None = None) -> bool:
    """
    服务项目名称是否已存在
    """
    if not service_name:
        return False
    stmt = select(ServiceItem.service_id).where(ServiceItem.service_name == service_name)  # 根据服务项目名称查询对应的ID
    if exclude_id is not None:  # 更新场景排除自身
        stmt = stmt.where(ServiceItem.service_id != exclude_id)
    return db.scalar(stmt) is not None  # 如果查到既存在


def insert_service_item(db: Session, body: ServiceItemBody) -> int:
    """
    新增服务项目
    """
    return insert_row(db, ServiceItem, body_fields(body, skip=("serviceId",)))


def update_service_item_by_id(db: Session, body: ServiceItemBody) -> int:
    """
    根据服务项目ID更新服务项目信息
    """
    if body.serviceId is None:  # 缺少主键无法更新
        return 0
    return update_by_pk(db, ServiceItem, ServiceItem.service_id, body.serviceId,
                        body_fields(body, skip=("serviceId",)))  # 泛型按照主键进行动态更新


def delete_service_item_by_ids(db: Session, service_ids: list[int]) -> int:
    """
    批量删除服务项目
    """
    return delete_by_pks(db, ServiceItem, ServiceItem.service_id, service_ids)

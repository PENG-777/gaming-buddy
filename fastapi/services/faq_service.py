"""
帮助中心FAQ业务层

faq(帮助中心FAQ)单表模块, 全部复用 core/common 泛型工具:
- 管理端 CRUD: 分页查询(问题模糊/分组/状态筛选)、详情、新增、动态更新、批量删除
- 用户端: 仅返回"显示"状态的FAQ(隐藏即对用户不可见), 按分组+组内排序返回
"""
from sqlalchemy import select  # 第三方: SQLAlchemy 列表达式
from sqlalchemy.orm import Session  # 第三方: 会话类型标注

from core.common import (  # 项目内: 泛型工具
    body_fields, delete_by_pks, eq_if, insert_row, like_if, paginate, row_to_dict, update_by_pk, where_if,
)
from models.entities import Faq  # 项目内: 帮助中心FAQ ORM 实体
from schemas.body import FaqBody  # 项目内: 帮助中心FAQ请求体模型

# FAQ查询列(label 与 row_to_dict 转换键一一对应)
_FAQ_COLS = (
    Faq.faq_id, Faq.category, Faq.question, Faq.answer,
    Faq.sort, Faq.status, Faq.create_time,
)


def select_faq_page(db: Session, page_num: int, page_size: int,
                    keyword: str | None = None, category: str | None = None,
                    status: int | None = None) -> tuple[int, list[dict]]:
    """分页查询FAQ列表(问题模糊/分组/状态动态筛选)

    参数: db 请求级 Session / page_num 页码 / page_size 每页条数 / keyword 问题模糊(可选) /
          category 分组(可选) / status 状态(可选)
    """
    stmt = select(*_FAQ_COLS)  # 查询FAQ列
    stmt = where_if(  # 拼接动态条件(值非空才生成)
        stmt,
        like_if(Faq.question, keyword),
        eq_if(Faq.category, category),
        eq_if(Faq.status, status),
    )
    stmt = stmt.order_by(Faq.category.asc(), Faq.sort.asc(), Faq.faq_id.asc())  # 按分组+组内排序
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [row_to_dict(r) for r in rows]  # 总数 + 当前页字典列表


def get_faq_by_id(db: Session, faq_id: int) -> dict | None:
    """按问题ID查询详情

    参数: db 请求级 Session / faq_id 问题ID; 无记录返回 None
    """
    row = db.execute(select(*_FAQ_COLS).where(Faq.faq_id == faq_id)).first()  # 按主键查第一条
    return row_to_dict(row) if row else None  # 无记录返回 None


def insert_faq(db: Session, body: FaqBody) -> int:
    """新增FAQ

    参数: db 请求级 Session / body FAQ请求体; 返回受影响行数
    """
    return insert_row(db, Faq, body_fields(body, skip=("faqId",)))  # 泛型单表插入(直接提交)


def update_faq_by_id(db: Session, body: FaqBody) -> int:
    """按问题ID更新非 null 字段

    参数: db 请求级 Session / body 请求体(faqId 必填定位, 其余非 null 字段更新); 返回受影响行数
    """
    if body.faqId is None:  # 缺少主键无法定位记录
        return 0
    return update_by_pk(db, Faq, Faq.faq_id, body.faqId, body_fields(body, skip=("faqId",)))  # 泛型按主键动态更新


def delete_faq_by_ids(db: Session, faq_ids: list[int]) -> int:
    """批量删除FAQ

    参数: db 请求级 Session / faq_ids 问题ID列表; 返回受影响行数
    """
    return delete_by_pks(db, Faq, Faq.faq_id, faq_ids)  # 泛型按主键批量删除


# ==================== 用户端 ====================

def select_published_faqs(db: Session) -> list[dict]:
    """用户端FAQ列表: 仅"显示"状态, 按分组+组内排序(与帮助中心手风琴顺序一致)

    参数: db 请求级 Session; 隐藏状态对用户端不可见
    """
    stmt = (
        select(*_FAQ_COLS)
        .where(Faq.status == 0)  # 仅显示状态(0)
        .order_by(Faq.category.asc(), Faq.sort.asc(), Faq.faq_id.asc())  # 分组升序 + 组内排序升序
    )
    return [row_to_dict(r) for r in db.execute(stmt).all()]  # camelCase 字典列表
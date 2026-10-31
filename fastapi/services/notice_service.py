"""
平台公告业务层

notice(平台公告)单表模块, 全部复用 core/common 泛型工具:
- 管理端 CRUD: 分页查询(标题模糊/类型/状态筛选)、详情、新增、动态更新、批量删除
- 用户端: 仅返回"发布"状态的公告(撤下即对用户不可见), 按发布时间倒序
"""
from sqlalchemy import select  # 第三方: SQLAlchemy 列表达式
from sqlalchemy.orm import Session  # 第三方: 会话类型标注

from core.common import (  # 项目内: 泛型工具
    body_fields, delete_by_pks, eq_if, insert_row, like_if, paginate, row_to_dict, update_by_pk, where_if,
)
from models.entities import Notice  # 项目内: 平台公告 ORM 实体
from schemas.body import NoticeBody  # 项目内: 公告请求体模型

# 公告查询列(label 与 row_to_dict 转换键一一对应)
_NOTICE_COLS = (
    Notice.notice_id, Notice.title, Notice.notice_type, Notice.content,
    Notice.status, Notice.create_time,
)


def select_notice_page(db: Session, page_num: int, page_size: int,
                       title: str | None = None, notice_type: str | None = None,
                       status: int | None = None) -> tuple[int, list[dict]]:
    """分页查询公告列表(标题模糊/类型/状态动态筛选)

    参数: db 请求级 Session / page_num 页码 / page_size 每页条数 / title 标题模糊(可选) /
          notice_type 类型(可选) / status 状态(可选)
    """
    stmt = select(*_NOTICE_COLS)  # 查询公告列
    stmt = where_if(  # 拼接动态条件(值非空才生成)
        stmt,
        like_if(Notice.title, title),
        eq_if(Notice.notice_type, notice_type),
        eq_if(Notice.status, status),
    )
    stmt = stmt.order_by(Notice.notice_id.desc())  # 按公告ID倒序(新建的在前)
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [row_to_dict(r) for r in rows]  # 总数 + 当前页字典列表


def get_notice_by_id(db: Session, notice_id: int) -> dict | None:
    """按公告ID查询详情

    参数: db 请求级 Session / notice_id 公告ID; 无记录返回 None
    """
    row = db.execute(select(*_NOTICE_COLS).where(Notice.notice_id == notice_id)).first()  # 按主键查第一条
    return row_to_dict(row) if row else None  # 无记录返回 None


def insert_notice(db: Session, body: NoticeBody) -> int:
    """新增公告

    参数: db 请求级 Session / body 公告请求体; 返回受影响行数
    """
    return insert_row(db, Notice, body_fields(body, skip=("noticeId",)))  # 泛型单表插入(直接提交)


def update_notice_by_id(db: Session, body: NoticeBody) -> int:
    """按公告ID更新非 null 字段

    参数: db 请求级 Session / body 请求体(noticeId 必填定位, 其余非 null 字段更新); 返回受影响行数
    """
    if body.noticeId is None:  # 缺少主键无法定位记录
        return 0
    return update_by_pk(db, Notice, Notice.notice_id, body.noticeId, body_fields(body, skip=("noticeId",)))  # 泛型按主键动态更新


def delete_notice_by_ids(db: Session, notice_ids: list[int]) -> int:
    """批量删除公告

    参数: db 请求级 Session / notice_ids 公告ID列表; 返回受影响行数
    """
    return delete_by_pks(db, Notice, Notice.notice_id, notice_ids)  # 泛型按主键批量删除


# ==================== 用户端 ====================

def select_published_notices(db: Session) -> list[dict]:
    """用户端公告列表: 仅"发布"状态, 按发布时间倒序(最新在前)

    参数: db 请求级 Session; 撤下状态对用户端不可见
    """
    stmt = (
        select(*_NOTICE_COLS)
        .where(Notice.status == 0)  # 仅发布状态(0)
        .order_by(Notice.create_time.desc(), Notice.notice_id.desc())  # 发布时间倒序, 同刻按ID稳定排序
    )
    return [row_to_dict(r) for r in db.execute(stmt).all()]  # camelCase 字典列表
"""
意见反馈业务层

feedback(意见反馈) 单表模块:
- 管理端: 分页列表(join user 取用户名/头像)、回复处理(置为已处理并记录回复时间)、批量删除
- 用户端: 提交反馈(user_id 取自登录用户, 类型白名单校验由路由层负责)
- 反馈由用户端帮助中心提交, 管理端只读查看 + 回复, 不提供管理端代录
"""
from datetime import datetime  # 标准库: 日期时间类型

from sqlalchemy import select  # 第三方: SQLAlchemy 列表达式
from sqlalchemy.orm import Session  # 第三方: 会话类型标注

from core.common import (  # 项目内: 泛型工具
    delete_by_pks, eq_if, insert_row, like_if, paginate, row_to_dict, update_by_pk, where_if,
)
from models.entities import Feedback, User  # 项目内: 意见反馈相关 ORM 实体
from schemas.body import FeedbackBody  # 项目内: 意见反馈请求体模型

# 反馈查询列(join user 取用户名/头像, label 与 row_to_dict 转换键一一对应)
_FEEDBACK_COLS = (
    Feedback.feedback_id, User.user_name, User.avatar, Feedback.feedback_type, Feedback.content,
    Feedback.status, Feedback.reply, Feedback.reply_time, Feedback.create_time,
)


def select_feedback_page(db: Session, page_num: int, page_size: int,
                         user_name: str | None = None, feedback_type: str | None = None,
                         status: int | None = None) -> tuple[int, list[dict]]:
    """分页查询意见反馈列表(join user, 供管理端查看)

    参数: db 请求级 Session / page_num 页码 / page_size 每页条数 / user_name 用户名模糊(可选) /
          feedback_type 类型(可选) / status 处理状态(可选)
    """
    stmt = select(*_FEEDBACK_COLS).select_from(Feedback)  # 显式指定主表
    stmt = stmt.join(User, Feedback.user_id == User.user_id)  # 内连接用户(取用户名/头像)
    stmt = where_if(  # 拼接动态条件(值非空才生成)
        stmt,
        like_if(User.user_name, user_name),
        eq_if(Feedback.feedback_type, feedback_type),
        eq_if(Feedback.status, status),
    )
    stmt = stmt.order_by(Feedback.feedback_id.desc())  # 按反馈ID倒序(最新提交的在前)
    total, rows = paginate(db, stmt, page_num, page_size)  # 泛型分页: count + offset/limit
    return total, [row_to_dict(r) for r in rows]  # 总数 + 当前页字典列表


def update_feedback_by_id(db: Session, body: FeedbackBody) -> int:
    """按反馈ID回复处理: 置为已处理并记录回复与回复时间

    参数: db 请求级 Session / body 请求体(feedbackId 定位/reply 回复内容选填); 返回受影响行数
    """
    if body.feedbackId is None:  # 缺少主键无法定位记录
        return 0
    fields = {  # 回复处理固定写入: 已处理 + 回复内容 + 回复时间(回复选填, 未填置空串)
        "status": 1,
        "reply": body.reply if body.reply is not None else "",
        "reply_time": datetime.now(),
    }
    return update_by_pk(db, Feedback, Feedback.feedback_id, body.feedbackId, fields)  # 泛型按主键更新


def delete_feedback_by_ids(db: Session, feedback_ids: list[int]) -> int:
    """批量删除意见反馈

    参数: db 请求级 Session / feedback_ids 反馈ID列表; 返回受影响行数
    """
    return delete_by_pks(db, Feedback, Feedback.feedback_id, feedback_ids)  # 泛型按主键批量删除


# ==================== 用户端 ====================

def insert_feedback(db: Session, body: FeedbackBody, user_id: int) -> int:
    """提交意见反馈(user_id 取自登录用户, 初始状态待处理)

    参数: db 请求级 Session / body 反馈请求体(feedbackType/content) / user_id 提交用户; 返回受影响行数
    """
    fields = {  # 只取类型与内容两个字段, 其余(状态/时间)走数据库默认值
        "user_id": user_id,
        "feedback_type": body.feedbackType,
        "content": body.content,
        "status": 0,
    }
    return insert_row(db, Feedback, fields)  # 泛型单表插入(直接提交)
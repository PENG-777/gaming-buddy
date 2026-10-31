"""意见反馈管理（/biz/feedback 前缀, 管理端列表/回复/删除 + 用户端提交）"""
# FastAPI: 路由/查询参数
from fastapi import APIRouter, Query

from core.common import split_ids  # 项目内: 删除接口 "1,2,3" 解析
from core.deps import DbDep, LoginUserDep, PageDep  # 项目内: 通用依赖(分页/登录校验/请求级 Session)
from core.response import ajax_error, ajax_success, page_data, to_ajax  # 项目内: 统一响应
from schemas.body import FeedbackBody  # 项目内: 意见反馈请求体
from services import feedback_service  # 项目内: 意见反馈业务层

# 反馈类型白名单(与管理端下拉/用户端帮助中心一致)
FEEDBACK_TYPES = ("功能建议", "体验问题", "内容举报", "其他")

router = APIRouter(prefix="/biz/feedback", tags=["feedback"])  # 模块路由器


@router.get("/selectFeedbackList")
def select_feedback_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # 通用依赖: 分页参数/登录校验/Session
                         userName: str | None = Query(None),  # 用户名模糊筛选(可选)
                         feedbackType: str | None = Query(None),  # 类型筛选(可选: 功能建议/体验问题/内容举报/其他)
                         status: int | None = Query(None)):  # 状态筛选(可选: 0待处理 1已处理)
    """分页查询意见反馈列表(join user 取用户名/头像)

    参数: page 分页参数 / login_user 登录用户 / db 请求级 Session / userName 用户名模糊(可选) /
          feedbackType 类型(可选) / status 状态(可选)
    """
    total, rows = feedback_service.select_feedback_page(db, page.pageNum, page.pageSize, userName, feedbackType, status)
    return page_data(rows, total)  # {total, rows, code, msg}


@router.put("/updateFeedback")
def update_feedback(body: FeedbackBody, login_user: LoginUserDep, db: DbDep):
    """回复处理反馈(置为已处理并记录回复时间, 回复内容选填)

    参数: body 反馈请求体(feedbackId 定位/reply 回复内容) / login_user 登录用户 / db 请求级 Session
    """
    if body.feedbackId is None:  # 缺少主键无法定位记录
        return ajax_error("参数错误: 缺少反馈ID")
    if body.reply is not None and len(body.reply) > 500:  # 回复长度与表列宽一致
        return ajax_error("回复内容不能超过 500 字")
    return to_ajax(feedback_service.update_feedback_by_id(db, body))  # 按受影响行数返回


@router.delete("/deleteFeedbackByFeedbackIds/{feedbackIds}")
def delete_feedback_by_feedback_ids(feedbackIds: str, login_user: LoginUserDep, db: DbDep):
    """批量删除意见反馈(路径参数逗号分隔)

    参数: feedbackIds 路径参数, 反馈ID串如 "1,2,3" / login_user 登录用户 / db 请求级 Session
    """
    feedback_ids = split_ids(feedbackIds)  # "1,2,3" -> [1, 2, 3]
    return to_ajax(feedback_service.delete_feedback_by_ids(db, feedback_ids))  # 按受影响行数返回


# ==================== 用户端 ====================

@router.post("/insertFeedback")
def insert_feedback(body: FeedbackBody, login_user: LoginUserDep, db: DbDep):
    """提交意见反馈(帮助中心, user_id 取自登录用户)

    参数: body 反馈请求体(feedbackType/content) / login_user 登录用户 / db 请求级 Session
    """
    if not body.feedbackType:  # 类型必填
        return ajax_error("请选择反馈类型")
    if body.feedbackType not in FEEDBACK_TYPES:  # 类型必须在白名单内
        return ajax_error("反馈类型不合法")
    if not body.content or not body.content.strip():  # 内容必填
        return ajax_error("反馈内容不能为空")
    if len(body.content.strip()) > 200:  # 内容长度与表列宽一致
        return ajax_error("反馈内容不能超过 200 字")
    body.content = body.content.strip()  # 去除首尾空白后入库
    return to_ajax(feedback_service.insert_feedback(db, body, login_user.userId))  # 按受影响行数返回
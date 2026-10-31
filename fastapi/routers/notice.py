"""平台公告管理（/biz/notice 前缀, 管理端 CRUD + 用户端已发布列表）"""
# FastAPI: 路由/查询参数
from fastapi import APIRouter, Query

from core.common import split_ids  # 项目内: 删除接口 "1,2,3" 解析
from core.deps import DbDep, LoginUserDep, PageDep  # 项目内: 通用依赖(分页/登录校验/请求级 Session)
from core.response import ajax_error, ajax_success, ajax_success_data, page_data, to_ajax  # 项目内: 统一响应
from schemas.body import NoticeBody  # 项目内: 公告请求体
from services import notice_service  # 项目内: 公告业务层

# 公告类型白名单(与管理端下拉/用户端标签一致)
NOTICE_TYPES = ("保障", "活动", "上新", "安全")

router = APIRouter(prefix="/biz/notice", tags=["notice"])  # 模块路由器


@router.get("/selectNoticeList")
def select_notice_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # 通用依赖: 分页参数/登录校验/Session
                       title: str | None = Query(None),  # 标题模糊筛选(可选)
                       noticeType: str | None = Query(None),  # 类型筛选(可选: 保障/活动/上新/安全)
                       status: int | None = Query(None)):  # 状态筛选(可选: 0发布 1撤下)
    """分页查询公告列表

    参数: page 分页参数 / login_user 登录用户 / db 请求级 Session / title 标题模糊(可选) /
          noticeType 类型(可选) / status 状态(可选)
    """
    total, rows = notice_service.select_notice_page(db, page.pageNum, page.pageSize, title, noticeType, status)
    return page_data(rows, total)  # {total, rows, code, msg}


@router.get("/selectNoticeByNoticeId/{noticeId}")
def select_notice_by_notice_id(noticeId: int, login_user: LoginUserDep, db: DbDep):
    """按公告ID查询详情

    参数: noticeId 路径参数, 公告ID / login_user 登录用户 / db 请求级 Session
    """
    notice = notice_service.get_notice_by_id(db, noticeId)  # 按主键查询
    return ajax_success_data(notice) if notice is not None else ajax_success()  # 无数据时不输出 data 键


@router.post("/insertNotice")
def insert_notice(body: NoticeBody, login_user: LoginUserDep, db: DbDep):
    """新增公告

    参数: body 公告请求体(标题/类型/正文/状态) / login_user 登录用户 / db 请求级 Session
    """
    if not body.title:  # 标题必填
        return ajax_error("公告标题不能为空")
    if not body.noticeType:  # 类型必填
        return ajax_error("公告类型不能为空")
    if body.noticeType not in NOTICE_TYPES:  # 类型必须在白名单内
        return ajax_error("公告类型不合法")
    if not body.content:  # 正文必填
        return ajax_error("公告正文不能为空")
    return to_ajax(notice_service.insert_notice(db, body))  # 按受影响行数返回


@router.put("/updateNotice")
def update_notice(body: NoticeBody, login_user: LoginUserDep, db: DbDep):
    """修改公告

    参数: body 公告请求体(noticeId 必填定位记录, 仅非 null 字段更新) / login_user 登录用户 / db 请求级 Session
    """
    if body.noticeId is None:  # 缺少主键无法定位记录
        return ajax_error("参数错误: 缺少公告ID")
    if body.noticeType is not None and body.noticeType not in NOTICE_TYPES:  # 传了类型才校验
        return ajax_error("公告类型不合法")
    return to_ajax(notice_service.update_notice_by_id(db, body))  # 按受影响行数返回


@router.delete("/deleteNoticeByNoticeIds/{noticeIds}")
def delete_notice_by_notice_ids(noticeIds: str, login_user: LoginUserDep, db: DbDep):
    """批量删除公告(路径参数逗号分隔)

    参数: noticeIds 路径参数, 公告ID串如 "1,2,3" / login_user 登录用户 / db 请求级 Session
    """
    notice_ids = split_ids(noticeIds)  # "1,2,3" -> [1, 2, 3]
    return to_ajax(notice_service.delete_notice_by_ids(db, notice_ids))  # 按受影响行数返回


# ==================== 用户端 ====================

@router.get("/selectPublishedNoticeList")
def select_published_notice_list(login_user: LoginUserDep, db: DbDep):
    """用户端公告列表: 仅返回已发布公告, 按发布时间倒序

    参数: login_user 登录用户 / db 请求级 Session
    """
    return ajax_success_data(notice_service.select_published_notices(db))  # 已发布公告列表
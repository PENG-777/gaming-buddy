"""帮助中心FAQ管理（/biz/faq 前缀, 管理端 CRUD + 用户端显示中列表）"""
# FastAPI: 路由/查询参数
from fastapi import APIRouter, Query

from core.common import split_ids  # 项目内: 删除接口 "1,2,3" 解析
from core.deps import DbDep, LoginUserDep, PageDep  # 项目内: 通用依赖(分页/登录校验/请求级 Session)
from core.response import ajax_error, ajax_success, ajax_success_data, page_data, to_ajax  # 项目内: 统一响应
from schemas.body import FaqBody  # 项目内: 帮助中心FAQ请求体
from services import faq_service  # 项目内: 帮助中心FAQ业务层

# FAQ分组白名单(与管理端下拉/用户端帮助中心分组一致)
FAQ_CATEGORIES = ("新手指南", "下单支付", "服务保障")

router = APIRouter(prefix="/biz/faq", tags=["faq"])  # 模块路由器


@router.get("/selectFaqList")
def select_faq_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # 通用依赖: 分页参数/登录校验/Session
                    keyword: str | None = Query(None),  # 问题模糊筛选(可选)
                    category: str | None = Query(None),  # 分组筛选(可选: 新手指南/下单支付/服务保障)
                    status: int | None = Query(None)):  # 状态筛选(可选: 0显示 1隐藏)
    """分页查询FAQ列表

    参数: page 分页参数 / login_user 登录用户 / db 请求级 Session / keyword 问题模糊(可选) /
          category 分组(可选) / status 状态(可选)
    """
    total, rows = faq_service.select_faq_page(db, page.pageNum, page.pageSize, keyword, category, status)
    return page_data(rows, total)  # {total, rows, code, msg}


@router.get("/selectFaqByFaqId/{faqId}")
def select_faq_by_faq_id(faqId: int, login_user: LoginUserDep, db: DbDep):
    """按问题ID查询详情

    参数: faqId 路径参数, 问题ID / login_user 登录用户 / db 请求级 Session
    """
    faq = faq_service.get_faq_by_id(db, faqId)  # 按主键查询
    return ajax_success_data(faq) if faq is not None else ajax_success()  # 无数据时不输出 data 键


@router.post("/insertFaq")
def insert_faq(body: FaqBody, login_user: LoginUserDep, db: DbDep):
    """新增FAQ

    参数: body FAQ请求体(分组/问题/答案/排序/状态) / login_user 登录用户 / db 请求级 Session
    """
    if not body.question:  # 问题必填
        return ajax_error("问题标题不能为空")
    if not body.category:  # 分组必填
        return ajax_error("所属分组不能为空")
    if body.category not in FAQ_CATEGORIES:  # 分组必须在白名单内
        return ajax_error("所属分组不合法")
    if not body.answer:  # 答案必填
        return ajax_error("答案正文不能为空")
    return to_ajax(faq_service.insert_faq(db, body))  # 按受影响行数返回


@router.put("/updateFaq")
def update_faq(body: FaqBody, login_user: LoginUserDep, db: DbDep):
    """修改FAQ

    参数: body FAQ请求体(faqId 必填定位记录, 仅非 null 字段更新) / login_user 登录用户 / db 请求级 Session
    """
    if body.faqId is None:  # 缺少主键无法定位记录
        return ajax_error("参数错误: 缺少问题ID")
    if body.category is not None and body.category not in FAQ_CATEGORIES:  # 传了分组才校验
        return ajax_error("所属分组不合法")
    return to_ajax(faq_service.update_faq_by_id(db, body))  # 按受影响行数返回


@router.delete("/deleteFaqByFaqIds/{faqIds}")
def delete_faq_by_faq_ids(faqIds: str, login_user: LoginUserDep, db: DbDep):
    """批量删除FAQ(路径参数逗号分隔)

    参数: faqIds 路径参数, 问题ID串如 "1,2,3" / login_user 登录用户 / db 请求级 Session
    """
    faq_ids = split_ids(faqIds)  # "1,2,3" -> [1, 2, 3]
    return to_ajax(faq_service.delete_faq_by_ids(db, faq_ids))  # 按受影响行数返回


# ==================== 用户端 ====================

@router.get("/selectPublishedFaqList")
def select_published_faq_list(login_user: LoginUserDep, db: DbDep):
    """用户端帮助中心FAQ列表: 仅返回"显示"状态的问答, 按分组+组内排序

    参数: login_user 登录用户 / db 请求级 Session
    """
    return ajax_success_data(faq_service.select_published_faqs(db))  # 显示中的问答列表
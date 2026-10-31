"""轮播图管理（/biz/banner 前缀）"""
# FastAPI: 路由/查询参数
from fastapi import APIRouter, Query

from core.common import split_ids  # 项目内: 删除接口 "1,2,3" 解析
from core.deps import DbDep, LoginUserDep, PageDep  # 项目内: 通用依赖(分页/登录校验/请求级 Session)
from core.response import ajax_error, ajax_success, ajax_success_data, page_data, to_ajax  # 项目内: 统一响应
from schemas.body import BannerBody
from services import banner_service

router = APIRouter(prefix="/biz/banner", tags=["banner"])  # 模块路由器


@router.get("/selectBannerList")
def select_banner_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # 通用依赖: 分页参数/登录校验/Session
                       title: str | None = Query(None),  # 标题模糊筛选(可选)
                       status: int | None = Query(None)):  # 状态筛选(可选)
    """分页查询轮播图列表"""
    total, rows = banner_service.select_banner_page(db, page.pageNum, page.pageSize, title, status)  # 业务层分页查询
    return page_data(rows, total)  # {total, rows, code, msg}


@router.get("/selectBannerByBannerId/{bannerId}")
def select_banner_by_banner_id(bannerId: int, login_user: LoginUserDep, db: DbDep):
    """
    按轮播图ID查询轮播图详情
    """
    banner = banner_service.get_banner_by_id(db, bannerId)  # 按主键查询
    return ajax_success_data(banner) if banner is not None else ajax_success()  # 无数据时不输出 data 键


@router.post("/insertBanner")
def insert_banner(body: BannerBody, login_user: LoginUserDep, db: DbDep):
    """
    新增轮播图
    """
    if not body.title:  # 如果标题为空
        return ajax_error("标题不能为空")
    return to_ajax(banner_service.insert_banner(db, body))  # 按受影响行数返回


@router.put("/updateBanner")
def update_banner(body: BannerBody, login_user: LoginUserDep, db: DbDep):
    """
    修改轮播图
    """
    if body.bannerId is None:  # 如果该轮播图ID在数据库中不存在
        return ajax_error("轮播图ID不存在")
    return to_ajax(banner_service.update_banner_by_id(db, body))  # 按受影响行数返回


@router.delete("/deleteBannerByBannerIds/{bannerIds}")
def delete_banner_by_banner_ids(bannerIds: str, login_user: LoginUserDep, db: DbDep):
    """
    批量删除轮播图
    """
    return to_ajax(banner_service.delete_banner_by_ids(db, split_ids(bannerIds)))


# =========================== 用户端 ===========================

@router.get("/selectPublishedBannerList")
def select_published_banner_list(login_user: LoginUserDep, db: DbDep):
    """
    用户端轮播图列表
    """
    return ajax_success_data(banner_service.select_published_banners(db))  # 返回启用状态的轮播图列表数据

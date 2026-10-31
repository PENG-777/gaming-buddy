"""服务项目管理（/biz/serviceItem 前缀）"""
# FastAPI: 路由/查询参数
from fastapi import APIRouter, Query

from core.common import split_ids  # 项目内: 删除接口 "1,2,3" 解析
from core.deps import DbDep, LoginUserDep, PageDep  # 项目内: 通用依赖(分页/登录校验/请求级 Session)
from core.response import ajax_error, ajax_success, ajax_success_data, page_data, to_ajax  # 项目内: 统一响应
from schemas.body import ServiceItemBody
from services import service_item_service

router = APIRouter(prefix="/biz/serviceItem", tags=["serviceItem"])  # 模块路由器


@router.get("/selectAllServiceItem")
def select_all_service_item(login_user: LoginUserDep, db: DbDep):
    """
    查询全部服务项目(不分页, 供下拉选择)
    """
    return ajax_success_data(service_item_service.select_service_item_list(db))  # 全量服务项目列表


@router.get("/selectServiceItemList")
def select_service_item_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # 通用依赖: 分页参数/登录校验/Session
                     serviceName: str | None = Query(None),  # 服务名称名称模糊筛选(可选)
                     status: int | None = Query(None)):  # 状态筛选(可选)
    """分页查询服务项目列表"""
    total, rows = service_item_service.select_service_item_page(db, page.pageNum, page.pageSize, serviceName, status)  # 业务层分页查询
    return page_data(rows, total)  # {total, rows, code, msg}


@router.get("/selectServiceItemByServiceItemId/{serviceId}")
def select_service_item_by_service_item_id(serviceId: int, login_user: LoginUserDep, db: DbDep):
    """
    按服务项目ID查询服务项目详情
    """
    service_item = service_item_service.get_service_item_by_id(db, serviceId)  # 按主键查询
    return ajax_success_data(service_item) if service_item is not None else ajax_success()  # 无数据时不输出 data 键


@router.post("/insertServiceItem")
def insert_service_item(body: ServiceItemBody, login_user: LoginUserDep, db: DbDep):
    """
    新增服务项目
    """
    if not body.serviceName:  # 如果服务项目名称为空
        return ajax_error("服务项目名称不能为空")
    if service_item_service.name_exists(db, body.serviceName):  # 如果服务项目名已存在
        return ajax_error("服务项目名称已存在")
    return to_ajax(service_item_service.insert_service_item(db, body))  # 按受影响行数返回


@router.put("/updateServiceItem")
def update_service_item(body: ServiceItemBody, login_user: LoginUserDep, db: DbDep):
    """
    修改服务项目
    """
    if body.serviceId is None:  # 如果该服务项目ID在数据库中不存在
        return ajax_error("服务项目ID不存在")
    if service_item_service.name_exists(db, body.serviceName, exclude_id=body.serviceId):  # 传了服务项目名称才查重
        return ajax_error("服务项目名称已存在")
    return to_ajax(service_item_service.update_service_item_by_id(db, body))  # 按受影响行数返回


@router.delete("/deleteServiceItemByServiceItemIds/{serviceIds}")
def delete_service_item_by_service_item_ids(serviceIds: str, login_user: LoginUserDep, db: DbDep):
    """
    批量删除服务项目
    """
    return to_ajax(service_item_service.delete_service_item_by_ids(db, split_ids(serviceIds)))

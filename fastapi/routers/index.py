"""首页"""
from fastapi import APIRouter  # FastAPI: 路由器

from core.deps import DbDep, LoginUserDep  # 项目内: 通用依赖(请求级 Session/登录校验)
from core.response import ajax_success, ajax_success_data  # 项目内: 统一响应
from services import stats_service  # 项目内: 平台统计业务层

router = APIRouter(tags=["index"])  # 模块路由器(无前缀)


@router.get("/")  # 根路径(公开接口, 用于探活)
def home():
    """服务探活: 验证后端已启动"""
    return ajax_success("恭喜你, 成功启动了后端~")  # {code:200, msg}


@router.get("/platformStats")  # 公开接口(首页统计条, 未登录也可浏览)
def platform_stats(db: DbDep):
    """平台统计数据: 陪玩师数/成交订单/服务时长/好评率(真实数据聚合)

    参数: db 请求级 Session(无登录要求, 公开接口)
    """
    return ajax_success_data(stats_service.get_platform_stats(db))  # 统计字典


@router.get("/adminStats")  # 需登录(管理端首页看板)
def admin_stats(db: DbDep, login_user: LoginUserDep):
    """管理端首页数据分析: 指标卡 + 订单状态/游戏分布 + 热门服务 TOP5 + 星级分布

    参数: db 请求级 Session / login_user 登录用户(需登录)
    """
    return ajax_success_data(stats_service.get_admin_dashboard(db))  # 看板数据字典
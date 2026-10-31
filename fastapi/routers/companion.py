"""陪玩师管理（/biz/companion 前缀）"""
# FastAPI: 路由/查询参数
from fastapi import APIRouter, Query

from core.common import split_ids  # 项目内: 删除接口 "1,2,3" 解析
from core.deps import DbDep, LoginUserDep, PageDep  # 项目内: 通用依赖(分页/登录校验/请求级 Session)
from core.response import ajax_error, ajax_success, ajax_success_data, page_data, to_ajax  # 项目内: 统一响应
from schemas.body import CompanionBody  # 项目内: 陪玩师请求体
from services import companion_service, user_service  # 项目内: 陪玩师/用户业务层

router = APIRouter(prefix="/biz/companion", tags=["companion"])  # 模块路由器


@router.get("/selectCompanionList")
def select_companion_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # 通用依赖: 分页参数/登录校验/Session
                          nickName: str | None = Query(None),  # 昵称模糊筛选(可选)
                          gender: int | None = Query(None),  # 性别筛选(可选: 0男 1女)
                          mainGameId: int | None = Query(None),  # 主游戏筛选(可选)
                          certified: int | None = Query(None),  # 认证状态筛选(可选: 0未认证 1已认证)
                          status: int | None = Query(None)):  # 状态筛选(可选: 0启用 1停用)
    """分页查询陪玩师列表(含主游戏名)

    参数: page 分页参数 / login_user 登录用户 / db 请求级 Session / nickName 昵称模糊(可选) /
          gender 性别(可选) / mainGameId 主游戏(可选) / certified 认证状态(可选) / status 状态(可选)
    """
    total, rows = companion_service.select_companion_page(  # 业务层分页查询
        db, page.pageNum, page.pageSize, nickName, gender, mainGameId, certified, status)
    return page_data(rows, total)  # {total, rows, code, msg}


@router.get("/selectCompanionByCompanionId/{companionId}")
def select_companion_by_companion_id(companionId: int, login_user: LoginUserDep, db: DbDep):
    """按陪玩师ID查询陪玩师详情(含擅长游戏与服务项目)

    参数: companionId 路径参数, 陪玩师ID / login_user 登录用户 / db 请求级 Session
    """
    companion = companion_service.get_companion_by_id(db, companionId)  # 按主键查询(含关联数据)
    return ajax_success_data(companion) if companion is not None else ajax_success()  # 无数据时不输出 data 键


@router.get("/selectAllCompanion")
def select_all_companion(login_user: LoginUserDep, db: DbDep):
    """查询全部启用陪玩师(含擅长游戏与服务项目, 供用户端一次拉全量)

    参数: login_user 登录用户 / db 请求级 Session
    """
    return ajax_success_data(companion_service.select_user_companion_all(db))  # 全量启用陪玩师列表


@router.post("/insertCompanion")
def insert_companion(body: CompanionBody, login_user: LoginUserDep, db: DbDep):
    """新增陪玩师

    参数: body 陪玩师请求体(基础信息+games/services 关联) / login_user 登录用户 / db 请求级 Session
    """
    if not body.nickName:  # 昵称必填
        return ajax_error("陪玩师昵称不能为空")
    if not body.games:  # 至少一个擅长游戏
        return ajax_error("请至少添加一个擅长游戏")
    if companion_service.name_exists(db, body.nickName):  # 昵称查重
        return ajax_error("陪玩师昵称已存在")
    if user_service.user_name_taken(db, body.nickName):  # 关联用户用户名=昵称, 需未被占用
        return ajax_error("该昵称已被注册为用户名, 请更换昵称")
    return to_ajax(companion_service.insert_companion(db, body))  # 按受影响行数返回(同步创建关联用户)


@router.put("/updateCompanion")
def update_companion(body: CompanionBody, login_user: LoginUserDep, db: DbDep):
    """修改陪玩师

    参数: body 陪玩师请求体(companionId 必填定位记录; games/services 为 None 不动作、空数组清空) /
          login_user 登录用户 / db 请求级 Session
    """
    if body.companionId is None:  # 缺少主键无法定位记录
        return ajax_error("参数错误: 缺少陪玩师ID")
    if not body.nickName:  # 昵称必填
        return ajax_error("陪玩师昵称不能为空")
    if body.games is not None and len(body.games) == 0:  # 传了游戏列表但不允许清空(主游戏必填)
        return ajax_error("请至少添加一个擅长游戏")
    if companion_service.name_exists(db, body.nickName, exclude_id=body.companionId):  # 传了昵称才查重(排除自己)
        return ajax_error("陪玩师昵称已存在")
    companion_user_id = companion_service.get_companion_user_id(db, body.companionId)  # 关联用户ID(无关联为 None)
    if body.nickName is not None and companion_user_id is not None \
            and user_service.user_name_taken(db, body.nickName, exclude_user_id=companion_user_id):  # 新昵称撞其他用户(排除关联账号)
        return ajax_error("该昵称已被其他用户占用, 请更换昵称")
    return to_ajax(companion_service.update_companion(db, body))  # 按受影响行数返回(同事务维护 games/services 关联)


@router.delete("/deleteCompanionByCompanionIds/{companionIds}")
def delete_companion_by_companion_ids(companionIds: str, login_user: LoginUserDep, db: DbDep):
    """批量删除陪玩师(路径参数逗号分隔, 关联数据外键级联清理)

    参数: companionIds 路径参数, 陪玩师ID串如 "1,2,3" / login_user 登录用户 / db 请求级 Session
    """
    return to_ajax(companion_service.delete_companion_by_ids(db, split_ids(companionIds)))  # "1,2,3" -> 批量删除
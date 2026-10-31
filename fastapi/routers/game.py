"""游戏分类管理（/biz/game 前缀）"""
# FastAPI: 路由/查询参数
from fastapi import APIRouter, Query

from core.common import split_ids  # 项目内: 删除接口 "1,2,3" 解析
from core.deps import DbDep, LoginUserDep, PageDep  # 项目内: 通用依赖(分页/登录校验/请求级 Session)
from core.response import ajax_error, ajax_success, ajax_success_data, page_data, to_ajax  # 项目内: 统一响应
from schemas.body import GameBody
from services import game_service

router = APIRouter(prefix="/biz/game", tags=["game"])  # 模块路由器


@router.get("/selectAllGame")
def select_all_game(login_user: LoginUserDep, db: DbDep):
    """
    查询全部游戏分类(不分页, 供下拉选择)
    """
    return ajax_success_data(game_service.select_game_list(db))  # 全量游戏分类列表


@router.get("/selectGameList")
def select_game_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # 通用依赖: 分页参数/登录校验/Session
                     gameName: str | None = Query(None),  # 游戏名称模糊筛选(可选)
                     status: int | None = Query(None)):  # 状态筛选(可选)
    """分页查询游戏分类列表"""
    total, rows = game_service.select_game_page(db, page.pageNum, page.pageSize, gameName, status)  # 业务层分页查询
    return page_data(rows, total)  # {total, rows, code, msg}


@router.get("/selectGameByGameId/{gameId}")
def select_game_by_game_id(gameId: int, login_user: LoginUserDep, db: DbDep):
    """
    按游戏ID查询游戏分类详情
    """
    game = game_service.get_game_by_id(db, gameId)  # 按主键查询
    return ajax_success_data(game) if game is not None else ajax_success()  # 无数据时不输出 data 键


@router.post("/insertGame")
def insert_game(body: GameBody, login_user: LoginUserDep, db: DbDep):
    """
    新增游戏分类
    """
    if not body.gameName:  # 如果游戏名称为空
        return ajax_error("游戏名称不能为空")
    if game_service.name_exists(db, body.gameName):  # 如果游戏名已存在
        return ajax_error("游戏名称已存在")
    return to_ajax(game_service.insert_game(db, body))  # 按受影响行数返回


@router.put("/updateGame")
def update_game(body: GameBody, login_user: LoginUserDep, db: DbDep):
    """
    修改游戏分类
    """
    if body.gameId is None:  # 如果该游戏ID在数据库中不存在
        return ajax_error("游戏ID不存在")
    if game_service.name_exists(db, body.gameName, exclude_id=body.gameId):  # 传了游戏名称才查重
        return ajax_error("游戏名称已存在")
    return to_ajax(game_service.update_game_by_id(db, body))  # 按受影响行数返回


@router.delete("/deleteGameByGameIds/{gameIds}")
def delete_game_by_game_ids(gameIds: str, login_user: LoginUserDep, db: DbDep):
    """
    批量删除游戏分类
    """
    return to_ajax(game_service.delete_game_by_ids(db, split_ids(gameIds)))

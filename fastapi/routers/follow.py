"""用户关注管理（/biz/follow 前缀, 管理端列表/删除 + 用户端关注切换/我的关注）"""
# FastAPI: 路由/查询参数
from fastapi import APIRouter, Query

from core.common import split_ids  # 项目内: 删除接口 "1,2,3" 解析
from core.deps import DbDep, LoginUserDep, PageDep  # 项目内: 通用依赖(分页/登录校验/请求级 Session)
from core.response import ajax_error, ajax_success, ajax_success_data, page_data, to_ajax  # 项目内: 统一响应
from schemas.body import FollowBody  # 项目内: 用户关注请求体
from services import follow_service  # 项目内: 用户关注业务层

router = APIRouter(prefix="/biz/follow", tags=["follow"])  # 模块路由器


@router.get("/selectFollowList")
def select_follow_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # 通用依赖: 分页参数/登录校验/Session
                       userName: str | None = Query(None),  # 用户名模糊筛选(可选)
                       nickName: str | None = Query(None)):  # 陪玩师昵称模糊筛选(可选)
    """分页查询关注列表(join user/companion 取用户与陪玩师信息)

    参数: page 分页参数 / login_user 登录用户 / db 请求级 Session / userName 用户名模糊(可选) / nickName 昵称模糊(可选)
    """
    total, rows = follow_service.select_follow_page(db, page.pageNum, page.pageSize, userName, nickName)
    return page_data(rows, total)  # {total, rows, code, msg}


@router.delete("/deleteFollowByIds/{followIds}")
def delete_follow_by_ids(followIds: str, login_user: LoginUserDep, db: DbDep):
    """批量删除关注记录(路径参数逗号分隔)

    参数: followIds 路径参数, 记录ID串如 "1,2,3" / login_user 登录用户 / db 请求级 Session
    """
    follow_ids = split_ids(followIds)  # "1,2,3" -> [1, 2, 3]
    return to_ajax(follow_service.delete_follow_by_ids(db, follow_ids))  # 按受影响行数返回


# ==================== 用户端 ====================

@router.post("/toggleFollow")
def toggle_follow(body: FollowBody, login_user: LoginUserDep, db: DbDep):
    """关注/取关切换(陪玩师详情页/关注页, user_id 取自登录用户)

    参数: body 关注请求体(companionId 必填) / login_user 登录用户 / db 请求级 Session
    """
    if body.companionId is None:  # 陪玩师ID必填
        return ajax_error("参数错误: 缺少陪玩师ID")
    followed, err = follow_service.toggle_follow(db, login_user.userId, body.companionId)  # 切换并取结果
    if err is not None:  # 业务失败(陪玩师不存在或已停用)
        return ajax_error(err)
    return ajax_success(followed=followed)  # 附加 followed: True 已关注 / False 已取消关注


@router.get("/selectMyFollowList")
def select_my_follow_list(login_user: LoginUserDep, db: DbDep):
    """我的关注列表(用户端关注页, 含陪玩师详情与主游戏名)

    参数: login_user 登录用户 / db 请求级 Session
    """
    return ajax_success_data(follow_service.select_my_follows(db, login_user.userId))  # 我的关注列表
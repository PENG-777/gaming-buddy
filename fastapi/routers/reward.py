"""打赏管理（/biz/reward 前缀, 管理端列表/删除 + 用户端打赏）"""
# FastAPI: 路由/查询参数
from fastapi import APIRouter, Query

from core.common import parse_dt, split_ids  # 项目内: 日期字符串解析 / 删除接口 "1,2,3" 解析
from core.deps import CompanionScopeDep, DbDep, LoginUserDep, PageDep  # 项目内: 通用依赖(分页/登录校验/请求级 Session/陪玩师数据范围)
from core.response import ajax_error, ajax_success, page_data, to_ajax  # 项目内: 统一响应
from schemas.body import RewardBody  # 项目内: 用户打赏请求体
from services import reward_service  # 项目内: 用户打赏业务层

router = APIRouter(prefix="/biz/reward", tags=["reward"])  # 模块路由器


@router.get("/selectRewardList")
def select_reward_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # 通用依赖: 分页参数/登录校验/Session
                       companion_scope: CompanionScopeDep,  # 陪玩师数据范围(陪玩师仅看打赏给自己的记录)
                       userName: str | None = Query(None),  # 打赏用户名模糊筛选(可选)
                       nickName: str | None = Query(None),  # 陪玩师昵称模糊筛选(可选)
                       giftName: str | None = Query(None),  # 礼物名称模糊筛选(可选)
                       beginTime: str | None = Query(None),  # 时间范围起(可选, 'yyyy-MM-dd HH:mm:ss')
                       endTime: str | None = Query(None)):  # 时间范围止(可选, 建议传 'yyyy-MM-dd 23:59:59' 含当天)
    """分页查询打赏记录(join user/companion 取用户与陪玩师信息; 陪玩师仅看自己的)

    参数: page 分页参数 / login_user 登录用户 / db 请求级 Session / companion_scope 陪玩师数据范围 /
          userName 用户名模糊(可选) / nickName 昵称模糊(可选) / giftName 礼物名模糊(可选) /
          beginTime/endTime 打赏时间范围(可选)
    """
    total, rows = reward_service.select_reward_page(  # 日期字符串解析失败返回 None(条件自动失效)
        db, page.pageNum, page.pageSize,
        user_name=userName, nick_name=nickName, gift_name=giftName,
        begin_time=parse_dt(beginTime), end_time=parse_dt(endTime),
        companion_id=companion_scope,  # 非 None 时仅查打赏给该陪玩师的记录
    )
    return page_data(rows, total)  # {total, rows, code, msg}


@router.delete("/deleteRewardByIds/{rewardIds}")
def delete_reward_by_ids(rewardIds: str, login_user: LoginUserDep, db: DbDep,
                         companion_scope: CompanionScopeDep):
    """批量删除打赏记录(管理端, 路径参数逗号分隔; 陪玩师只读无权删除)

    参数: rewardIds 路径参数, 打赏ID串如 "1,2,3" / login_user 登录用户 / db 请求级 Session /
          companion_scope 陪玩师数据范围(非 None 拒绝)
    """
    if companion_scope is not None:  # 陪玩师角色拦截
        return ajax_error("陪玩师账号无权执行该操作")
    return to_ajax(reward_service.delete_reward_by_ids(db, split_ids(rewardIds)))  # "1,2,3" -> 批量删除


# ==================== 用户端 ====================

@router.post("/sendReward")
def send_reward(body: RewardBody, login_user: LoginUserDep, db: DbDep):
    """用户打赏(陪玩师详情页送礼物, 扣余额+写流水+写打赏记录一次事务; 金额以后端礼物定价为准)

    参数: body 打赏请求体(companionId/giftId 必填, 金额不接受前端传) / login_user 登录用户 / db 请求级 Session
    """
    if body.companionId is None:  # 陪玩师ID必填
        return ajax_error("参数错误: 缺少陪玩师ID")
    if body.giftId is None:  # 礼物ID必填
        return ajax_error("参数错误: 缺少礼物ID")
    err, balance_after = reward_service.send_reward(db, login_user.userId, body.companionId, body.giftId)  # 返回 (错误或 None, 打赏后余额)
    return ajax_success(balance=balance_after) if err is None else ajax_error(err)  # 成功携带最新余额
"""
钱包管理(/biz/wallet 前缀)
"""
from fastapi import APIRouter, Query

from core.common import parse_dt  # 项目内: 删除接口 "1,2,3" 解析
from core.deps import CompanionScopeDep, DbDep, LoginUserDep, PageDep  # 项目内: 通用依赖(分页/登录校验/请求级 Session)
from core.response import ajax_error, ajax_success, ajax_success_data, page_data, to_ajax  # 项目内: 统一响应
from schemas.body import WalletAdjustBody, WalletChangeBody, WalletRechargeBody
from services import wallet_service

router = APIRouter(prefix="/biz/wallet", tags=["wallet"])  # 模块路由器


@router.get("/my")
def my_wallet(login_user: LoginUserDep, db: DbDep):
    """
    查询我的账户余额
    """
    return ajax_success_data({"balance": wallet_service.get_balance(db, login_user.userId)})


@router.get("/my/transactions")
def my_transactions(page: PageDep, login_user: LoginUserDep, db: DbDep, txType: str | None = Query(None)):
    """
    我的钱包: 分页查询当前的用户的收支明细
    """
    total, rows = wallet_service.select_tx_page(db, page.pageNum, page.pageSize, user_id=login_user.userId,
                                                tx_type=txType)
    return page_data(rows, total)


@router.post("/recharge")
def recharge(body: WalletRechargeBody, login_user: LoginUserDep, db: DbDep):
    """
    余额充值
    """
    if not body.amount:
        return ajax_error("充值金额不能为空")
    err, _ = wallet_service.recharge(db, login_user.userId, body.amount, body.payMethod)
    return ajax_success() if err is None else ajax_error(err)


@router.post("/change")
def change(body: WalletChangeBody, login_user: LoginUserDep, db: DbDep):
    """
    钱包通用变动(订单支付/打赏/退款联动, 仅本人钱包)
    """
    if not body.amount or body.amount == 0:
        return ajax_error("变动金额不能为0")
    if not body.type:
        return ajax_error("变动类型不能为空")
    err, _ = wallet_service.change(db, login_user.userId, body.amount, body.type, body.note)
    return ajax_success() if err is None else ajax_error(err)


@router.get("/list")
def select_wallet_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # 通用依赖: 分页参数/登录校验/Session
                       userName: str | None = Query(None)):
    """分页查询用户余额列表"""
    total, rows = wallet_service.select_wallet_page(db, page.pageNum, page.pageSize, userName)  # 业务层分页查询
    return page_data(rows, total)  # {total, rows, code, msg}


@router.get("/transaction/list")
def select_transaction_list(page: PageDep, login_user: LoginUserDep, db: DbDep,
                            companion_scope: CompanionScopeDep,
                            userName: str | None = Query(None),
                            txType: str | None = Query(None),
                            userId: int | None = Query(None),
                            begin_time: str | None = Query(None),
                            end_time: str | None = Query(None)):
    """
    管理端: 分页查询全局流水钱包(陪玩师只能查看自己的流水)
    """
    scope_user_id = login_user.userId if companion_scope is not None else userId
    total, rows = wallet_service.select_tx_page(db, page.pageNum, page.pageSize, user_name=userName, tx_type=txType,
                                                user_id=scope_user_id, begin_time=parse_dt(begin_time),
                                                end_time=parse_dt(end_time))
    return page_data(rows, total)  # {total, rows, code, msg}


@router.put("/adjust")
def adjust(body: WalletAdjustBody, login_user: LoginUserDep, db: DbDep):
    """
    管理员人工调整用户余额
    """
    if not body.userId:
        return ajax_error("参数错误: 缺少用户ID")
    operator = login_user.user.userName if login_user.user else None  # 操作人
    err, balance_after = wallet_service.adjust_wallet(db, body.userId, body.amount, body.note.strip(), operator)
    return ajax_success(balance=balance_after) if err is None else ajax_error(err)

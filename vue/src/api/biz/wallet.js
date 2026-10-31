import request from '@/utils/request'

//查询用户余额列表(管理端, 附累计充值/累计支出)
export function selectWalletList(query) {
  return request({
    url: '/biz/wallet/list',
    method: 'get',
    params: query
  })
}

//查询全局钱包流水(管理端, 只读审计)
export function selectWalletTransactionList(query) {
  return request({
    url: '/biz/wallet/transaction/list',
    method: 'get',
    params: query
  })
}

//人工调整用户余额(管理端, 正数增加负数扣减)
export function adjustWallet(data) {
  return request({
    url: '/biz/wallet/adjust',
    method: 'put',
    data: data
  })
}

//查询我的钱包余额(用户端)
export function getMyWallet() {
  return request({
    url: '/biz/wallet/my',
    method: 'get'
  })
}

//分页查询我的收支明细(用户端)
export function listMyTransactions(query) {
  return request({
    url: '/biz/wallet/my/transactions',
    method: 'get',
    params: query
  })
}

//余额充值(用户端, 模拟支付成功入账)
export function rechargeWallet(data) {
  return request({
    url: '/biz/wallet/recharge',
    method: 'post',
    data: data
  })
}

//钱包通用变动(用户端, 订单支付/打赏/退款联动)
export function changeWallet(data) {
  return request({
    url: '/biz/wallet/change',
    method: 'post',
    data: data
  })
}
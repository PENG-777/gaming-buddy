import request from '@/utils/request'

//平台统计数据(用户端首页统计条: 陪玩师数/成交订单/服务时长/好评率)
export function getPlatformStats() {
  return request({
    url: '/platformStats', //公开接口, 无需登录
    method: 'get'
  })
}

//管理端首页数据分析(指标卡 + 订单状态/游戏分布 + 热门服务TOP5 + 星级分布)
export function getAdminStats() {
  return request({
    url: '/adminStats', //需登录, 自动携带token
    method: 'get'
  })
}
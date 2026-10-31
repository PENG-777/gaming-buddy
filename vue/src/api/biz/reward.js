import request from '@/utils/request'

//查询打赏记录列表(管理端)
export function selectRewardList(query) {
  return request({
    url: '/biz/reward/selectRewardList',
    method: 'get',
    params: query
  })
}

//删除打赏记录(管理端)
export function deleteRewardByIds(rewardIds) {
  return request({
    url: '/biz/reward/deleteRewardByIds/' + rewardIds,
    method: 'delete'
  })
}

//用户打赏(用户端, 扣余额+写流水+写打赏记录一次事务)
export function sendReward(data) {
  return request({
    url: '/biz/reward/sendReward',
    method: 'post',
    data: data
  })
}
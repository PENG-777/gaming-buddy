import request from '@/utils/request'

//查询订单评价列表
export function selectReviewList(query) {
  return request({
    url: '/biz/review/selectReviewList',
    method: 'get',
    params: query
  })
}

//查询某陪玩师的全部真实评价(用户端详情页)
export function selectCompanionReviews(companionId) {
  return request({
    url: '/biz/review/companionReviews/' + companionId,
    method: 'get'
  })
}

//回复评价(重复回复覆盖更新)
export function updateReviewReply(data) {
  return request({
    url: '/biz/review/updateReviewReply',
    method: 'put',
    data: data
  })
}

//删除订单评价(清空评价字段, 订单保留, 用户可重新评价)
export function deleteReviewByOrderIds(orderIds) {
  return request({
    url: '/biz/review/deleteReviewByOrderIds/' + orderIds,
    method: 'delete'
  })
}
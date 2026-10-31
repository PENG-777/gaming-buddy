import request from '@/utils/request'

// ==================== 管理端 ====================

//查询订单列表(管理端)
export function selectOrderList(query) {
  return request({
    url: '/biz/order/selectOrderList',
    method: 'get',
    params: query
  })
}

//开始服务(管理端, booked -> ongoing)
export function startOrder(orderId) {
  return request({
    url: '/biz/order/startOrder/' + orderId,
    method: 'put'
  })
}

//代取消订单(管理端, pending直接取消/booked取消并退款)
export function cancelOrder(data) {
  return request({
    url: '/biz/order/cancelOrder',
    method: 'put',
    data: data
  })
}

//确认退款(管理端, refunding -> cancelled 并退回余额/返还券)
export function confirmRefund(orderId) {
  return request({
    url: '/biz/order/confirmRefund/' + orderId,
    method: 'put'
  })
}

//批量删除订单(管理端)
export function deleteOrderByOrderIds(orderIds) {
  return request({
    url: '/biz/order/deleteOrderByOrderIds/' + orderIds,
    method: 'delete'
  })
}

// ==================== 用户端 ====================

//创建订单(待支付)
export function createOrder(data) {
  return request({
    url: '/biz/order/create',
    method: 'post',
    data: data
  })
}

//支付订单(余额/微信/支付宝)
export function payOrder(data) {
  return request({
    url: '/biz/order/pay',
    method: 'put',
    data: data
  })
}

//取消订单(待支付直接取消, 已支付进入退款审核)
export function cancelMyOrder(data) {
  return request({
    url: '/biz/order/cancel',
    method: 'put',
    data: data
  })
}

//确认完成(ongoing -> completed)
export function finishOrder(orderNo) {
  return request({
    url: '/biz/order/finish/' + orderNo,
    method: 'put'
  })
}

//评价订单(completed 且未评价)
export function reviewOrder(data) {
  return request({
    url: '/biz/order/review',
    method: 'put',
    data: data
  })
}

//查询我的订单(分页, status 为空查全部)
export function selectMyOrderList(query) {
  return request({
    url: '/biz/order/my',
    method: 'get',
    params: query
  })
}

//查询我的订单各状态计数
export function selectMyOrderCounters() {
  return request({
    url: '/biz/order/my/counters',
    method: 'get'
  })
}

//查询我发出的评价
export function selectMyReviews() {
  return request({
    url: '/biz/order/my/reviews',
    method: 'get'
  })
}

//按订单号查询我的订单详情
export function selectMyOrder(orderNo) {
  return request({
    url: '/biz/order/my/' + orderNo,
    method: 'get'
  })
}

//查询某陪玩师某天已占用时段
export function selectOccupiedSlots(companionId, date) {
  return request({
    url: '/biz/order/slots',
    method: 'get',
    params: { companionId, date }
  })
}

//查询某陪玩师未来几天每天已占用时段(详情页时间表)
export function selectOccupiedSlotsBatch(companionId, days = 7) {
  return request({
    url: '/biz/order/slotsBatch',
    method: 'get',
    params: { companionId, days }
  })
}
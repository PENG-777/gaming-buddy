import request from '@/utils/request'

//查询优惠券列表
export function selectCouponList(query) {
  return request({
    url: '/biz/coupon/selectCouponList',
    method: 'get',
    params: query
  })
}

//根据优惠券ID查询优惠券信息
export function selectCouponByCouponId(couponId) {
  return request({
    url: '/biz/coupon/selectCouponByCouponId/' + couponId,
    method: 'get'
  })
}

//新增优惠券
export function insertCoupon(data) {
  return request({
    url: '/biz/coupon/insertCoupon',
    method: 'post',
    data: data
  })
}

//修改优惠券
export function updateCoupon(data) {
  return request({
    url: '/biz/coupon/updateCoupon',
    method: 'put',
    data: data
  })
}

//删除优惠券
export function deleteCouponByCouponIds(couponIds) {
  return request({
    url: '/biz/coupon/deleteCouponByCouponIds/' + couponIds,
    method: 'delete'
  })
}

//查询用户领取的优惠券记录
export function selectUserCouponList(query) {
  return request({
    url: '/biz/coupon/selectUserCouponList',
    method: 'get',
    params: query
  })
}

//查询领券中心可领取的优惠券(用户端)
export function selectAvailableCouponList() {
  return request({
    url: '/biz/coupon/selectAvailableCouponList',
    method: 'get'
  })
}

//领取优惠券(用户端)
export function receiveCoupon(couponId) {
  return request({
    url: '/biz/coupon/receiveCoupon/' + couponId,
    method: 'post'
  })
}

//查询我的优惠券(用户端)
export function selectMyCouponList() {
  return request({
    url: '/biz/coupon/selectMyCouponList',
    method: 'get'
  })
}

//核销优惠券(订单支付时调用)
export function useCoupon(userCouponId) {
  return request({
    url: '/biz/coupon/useCoupon/' + userCouponId,
    method: 'put'
  })
}

//返还优惠券(订单取消退款时调用)
export function returnCoupon(userCouponId) {
  return request({
    url: '/biz/coupon/returnCoupon/' + userCouponId,
    method: 'put'
  })
}
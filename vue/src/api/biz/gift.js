import request from '@/utils/request'

//查询礼物列表(管理端)
export function selectGiftList(query) {
  return request({
    url: '/biz/gift/selectGiftList',
    method: 'get',
    params: query
  })
}

//按礼物ID查询礼物详情(管理端, 修改回显)
export function selectGiftByGiftId(giftId) {
  return request({
    url: '/biz/gift/selectGiftByGiftId/' + giftId,
    method: 'get'
  })
}

//新增礼物(管理端)
export function insertGift(data) {
  return request({
    url: '/biz/gift/insertGift',
    method: 'post',
    data: data
  })
}

//修改礼物(管理端)
export function updateGift(data) {
  return request({
    url: '/biz/gift/updateGift',
    method: 'put',
    data: data
  })
}

//删除礼物(管理端)
export function deleteGiftByIds(giftIds) {
  return request({
    url: '/biz/gift/deleteGiftByIds/' + giftIds,
    method: 'delete'
  })
}

//启用礼物列表(用户端打赏弹窗)
export function selectEnabledGiftList() {
  return request({
    url: '/biz/gift/selectEnabledGiftList',
    method: 'get'
  })
}
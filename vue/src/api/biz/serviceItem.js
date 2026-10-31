import request from '@/utils/request'

//查询所有服务项目列表
export function selectAllServiceItem() {
  return request({
    url: '/biz/serviceItem/selectAllServiceItem',
    method: 'get'
  })
}

//查询服务项目列表
export function selectServiceItemList(query) {
  return request({
    url: '/biz/serviceItem/selectServiceItemList',
    method: 'get',
    params: query
  })
}

//根据服务项目ID查询服务项目信息
export function selectServiceItemByServiceItemId(serviceItemId) {
  return request({
    url: '/biz/serviceItem/selectServiceItemByServiceItemId/' + serviceItemId,
    method: 'get'
  })
}

//新增服务项目
export function insertServiceItem(data) {
  return request({
    url: '/biz/serviceItem/insertServiceItem',
    method: 'post',
    data: data
  })
}

//修改服务项目
export function updateServiceItem(data) {
  return request({
    url: '/biz/serviceItem/updateServiceItem',
    method: 'put',
    data: data
  })
}

//删除服务项目
export function deleteServiceItemByServiceItemIds(serviceItemIds) {
  return request({
    url: '/biz/serviceItem/deleteServiceItemByServiceItemIds/' + serviceItemIds,
    method: 'delete'
  })
}
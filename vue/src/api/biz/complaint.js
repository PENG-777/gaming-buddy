import request from '@/utils/request'

//查询订单投诉列表
export function selectComplaintList(query) {
  return request({
    url: '/biz/complaint/selectComplaintList',
    method: 'get',
    params: query
  })
}

//处理投诉(置为已处理并记录结果/说明)
export function updateComplaint(data) {
  return request({
    url: '/biz/complaint/updateComplaint',
    method: 'put',
    data: data
  })
}

//删除订单投诉
export function deleteComplaintByComplaintIds(complaintIds) {
  return request({
    url: '/biz/complaint/deleteComplaintByComplaintIds/' + complaintIds,
    method: 'delete'
  })
}

//发起投诉(用户端订单详情页)
export function insertComplaint(data) {
  return request({
    url: '/biz/complaint/insertComplaint',
    method: 'post',
    data: data
  })
}
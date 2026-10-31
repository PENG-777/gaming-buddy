import request from '@/utils/request'

//查询FAQ列表
export function selectFaqList(query) {
  return request({
    url: '/biz/faq/selectFaqList',
    method: 'get',
    params: query
  })
}

//根据问题ID查询FAQ信息
export function selectFaqByFaqId(faqId) {
  return request({
    url: '/biz/faq/selectFaqByFaqId/' + faqId,
    method: 'get'
  })
}

//新增FAQ
export function insertFaq(data) {
  return request({
    url: '/biz/faq/insertFaq',
    method: 'post',
    data: data
  })
}

//修改FAQ
export function updateFaq(data) {
  return request({
    url: '/biz/faq/updateFaq',
    method: 'put',
    data: data
  })
}

//删除FAQ
export function deleteFaqByFaqIds(faqIds) {
  return request({
    url: '/biz/faq/deleteFaqByFaqIds/' + faqIds,
    method: 'delete'
  })
}

//查询显示中的FAQ列表(用户端帮助中心)
export function selectPublishedFaqList() {
  return request({
    url: '/biz/faq/selectPublishedFaqList',
    method: 'get'
  })
}
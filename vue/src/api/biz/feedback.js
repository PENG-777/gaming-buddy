import request from '@/utils/request'

//查询意见反馈列表
export function selectFeedbackList(query) {
  return request({
    url: '/biz/feedback/selectFeedbackList',
    method: 'get',
    params: query
  })
}

//回复处理反馈(置为已处理)
export function updateFeedback(data) {
  return request({
    url: '/biz/feedback/updateFeedback',
    method: 'put',
    data: data
  })
}

//删除意见反馈
export function deleteFeedbackByFeedbackIds(feedbackIds) {
  return request({
    url: '/biz/feedback/deleteFeedbackByFeedbackIds/' + feedbackIds,
    method: 'delete'
  })
}

//提交意见反馈(用户端帮助中心)
export function insertFeedback(data) {
  return request({
    url: '/biz/feedback/insertFeedback',
    method: 'post',
    data: data
  })
}
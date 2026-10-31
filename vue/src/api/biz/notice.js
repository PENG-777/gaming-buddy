import request from '@/utils/request'

//查询公告列表
export function selectNoticeList(query) {
  return request({
    url: '/biz/notice/selectNoticeList',
    method: 'get',
    params: query
  })
}

//根据公告ID查询公告信息
export function selectNoticeByNoticeId(noticeId) {
  return request({
    url: '/biz/notice/selectNoticeByNoticeId/' + noticeId,
    method: 'get'
  })
}

//新增公告
export function insertNotice(data) {
  return request({
    url: '/biz/notice/insertNotice',
    method: 'post',
    data: data
  })
}

//修改公告
export function updateNotice(data) {
  return request({
    url: '/biz/notice/updateNotice',
    method: 'put',
    data: data
  })
}

//删除公告
export function deleteNoticeByNoticeIds(noticeIds) {
  return request({
    url: '/biz/notice/deleteNoticeByNoticeIds/' + noticeIds,
    method: 'delete'
  })
}

//查询已发布的公告列表(用户端)
export function selectPublishedNoticeList() {
  return request({
    url: '/biz/notice/selectPublishedNoticeList',
    method: 'get'
  })
}
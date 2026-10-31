import request from '@/utils/request'

//查询关注列表
export function selectFollowList(query) {
  return request({
    url: '/biz/follow/selectFollowList',
    method: 'get',
    params: query
  })
}

//删除关注记录
export function deleteFollowByIds(followIds) {
  return request({
    url: '/biz/follow/deleteFollowByIds/' + followIds,
    method: 'delete'
  })
}

//关注/取关切换(用户端)
export function toggleFollow(data) {
  return request({
    url: '/biz/follow/toggleFollow',
    method: 'post',
    data: data
  })
}

//我的关注列表(用户端)
export function selectMyFollowList() {
  return request({
    url: '/biz/follow/selectMyFollowList',
    method: 'get'
  })
}
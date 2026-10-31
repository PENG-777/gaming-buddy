import request from '@/utils/request'

//修改个人信息
export function updateProfile(data) {
  return request({
    url: '/system/user/profile',
    method: 'put',
    data: data
  })
}

//重置密码
export function updatePwd(data) {
  return request({
    url: '/system/user/profile/updatePwd',
    method: 'put',
    data: data
  })
}

//为什么要使用params: query 而不使用data: data
//1.GET请求通常不包含请求体(request body), 浏览器和服务器都不会处理get请求的body
//2.@RequestBody期望从请求体中读取数据, 但是GET请求没有body, 所以报错
//3.params参数会自动评价到url后面作为查询参数, 这与GET请求的语义一致

//查询用户列表
export function selectUserList(query) {
  return request({
    url: '/system/user/selectUserList',
    method: 'get',
    params: query
  })
}

//根据用户ID查询用户信息
export function selectUserByUserId(userId) {
  return request({
    url: '/system/user/selectUserByUserId/' + userId,
    method: 'get'
  })
}

//新增用户
export function insertUser(data) {
  return request({
    url: '/system/user/insertUser',
    method: 'post',
    data: data
  })
}

//修改用户
export function updateUser(data) {
  return request({
    url: '/system/user/updateUser',
    method: 'put',
    data: data
  })
}

//删除用户
export function deleteUserByUserIds(userIds) {
  return request({
    url: '/system/user/deleteUserByUserIds/' + userIds,
    method: 'delete'
  })
}

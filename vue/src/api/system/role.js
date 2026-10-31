import request from '@/utils/request'

//查询所有角色列表
export function selectAllRole() {
  return request({
    url: '/system/role/selectAllRole',
    method: 'get'
  })
}

//查询角色列表
export function selectRoleList(query) {
  return request({
    url: '/system/role/selectRoleList',
    method: 'get',
    params: query
  })
}

//根据角色ID查询角色信息
export function selectRoleByRoleId(roleId) {
  return request({
    url: '/system/role/selectRoleByRoleId/' + roleId,
    method: 'get'
  })
}

//新增角色
export function insertRole(data) {
  return request({
    url: '/system/role/insertRole',
    method: 'post',
    data: data
  })
}

//修改角色
export function updateRole(data) {
  return request({
    url: '/system/role/updateRole',
    method: 'put',
    data: data
  })
}

//删除角色
export function deleteRoleByRoleIds(roleIds) {
  return request({
    url: '/system/role/deleteRoleByRoleIds/' + roleIds,
    method: 'delete'
  })
}

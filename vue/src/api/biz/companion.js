import request from '@/utils/request'

//查询陪玩师列表
export function selectCompanionList(query) {
  return request({
    url: '/biz/companion/selectCompanionList',
    method: 'get',
    params: query
  })
}

//根据陪玩师ID查询陪玩师信息(含擅长游戏与服务项目)
export function selectCompanionByCompanionId(companionId) {
  return request({
    url: '/biz/companion/selectCompanionByCompanionId/' + companionId,
    method: 'get'
  })
}

//查询全部启用陪玩师(含擅长游戏与服务项目, 用户端一次拉全量)
export function selectAllCompanion() {
  return request({
    url: '/biz/companion/selectAllCompanion',
    method: 'get'
  })
}

//新增陪玩师
export function insertCompanion(data) {
  return request({
    url: '/biz/companion/insertCompanion',
    method: 'post',
    data: data
  })
}

//修改陪玩师
export function updateCompanion(data) {
  return request({
    url: '/biz/companion/updateCompanion',
    method: 'put',
    data: data
  })
}

//删除陪玩师
export function deleteCompanionByCompanionIds(companionIds) {
  return request({
    url: '/biz/companion/deleteCompanionByCompanionIds/' + companionIds,
    method: 'delete'
  })
}
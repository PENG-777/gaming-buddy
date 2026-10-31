import request from '@/utils/request'

//查询所有游戏分类列表
export function selectAllGame() {
  return request({
    url: '/biz/game/selectAllGame',
    method: 'get'
  })
}

//查询游戏分类列表
export function selectGameList(query) {
  return request({
    url: '/biz/game/selectGameList',
    method: 'get',
    params: query
  })
}

//根据游戏ID查询游戏分类信息
export function selectGameByGameId(gameId) {
  return request({
    url: '/biz/game/selectGameByGameId/' + gameId,
    method: 'get'
  })
}

//新增游戏分类
export function insertGame(data) {
  return request({
    url: '/biz/game/insertGame',
    method: 'post',
    data: data
  })
}

//修改游戏分类
export function updateGame(data) {
  return request({
    url: '/biz/game/updateGame',
    method: 'put',
    data: data
  })
}

//删除游戏分类
export function deleteGameByGameIds(gameIds) {
  return request({
    url: '/biz/game/deleteGameByGameIds/' + gameIds,
    method: 'delete'
  })
}
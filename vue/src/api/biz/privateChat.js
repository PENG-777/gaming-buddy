import request from '@/utils/request'

// ==================== 用户端 ====================

//我的私聊会话列表(含双方昵称/头像与未读数, 不清任何未读)
export function getMyPrivateConversations() {
  return request({
    url: '/privateChat/myConversations',
    method: 'get'
  })
}

//按陪玩师开聊(首次自动建会话, 返回会话+全部历史, 顺带清零我的未读; "聊一聊"直达用)
export function openCompanionConversation(companionId) {
  return request({
    url: '/privateChat/companion/' + companionId + '/open',
    method: 'get'
  })
}

// ==================== 管理端工作台(陪玩师回复 / 管理员监管) ====================

//工作台: 分页查询会话列表(管理员看全部, 陪玩师只看自己的)
export function pageWorkbenchConversations(query) {
  return request({
    url: '/privateChat/workbench/page',
    method: 'get',
    params: query
  })
}

//工作台: 按会话查全部历史消息(陪玩师打开清自己未读, 管理员只读不清)
export function listWorkbenchMessages(conversationId) {
  return request({
    url: '/privateChat/' + conversationId + '/workbenchMessages',
    method: 'get'
  })
}
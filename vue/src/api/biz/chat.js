import request from '@/utils/request'

//我的客服会话+全部历史消息(首次自动建会话, 顺带清零未读)
export function getMyConversation() {
  return request({
    url: '/chat/myConversation',
    method: 'get'
  })
}

//我的客服未读数(WS 断线期间的补偿轮询)
export function getChatUnread() {
  return request({
    url: '/chat/unread',
    method: 'get'
  })
}

//清零我的客服未读数(打开客服会话时调用)
export function markChatRead() {
  return request({
    url: '/chat/read',
    method: 'put'
  })
}

//管理端: 分页查询客服会话列表
export function pageChatConversations(query) {
  return request({
    url: '/chat/page',
    method: 'get',
    params: query
  })
}

//管理端: 按会话查全部历史消息
export function listChatMessages(conversationId) {
  return request({
    url: '/chat/' + conversationId + '/messages',
    method: 'get'
  })
}
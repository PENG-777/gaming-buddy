/**
 * 获取当前用户的认证令牌
 */
export function getToken() {
  return localStorage.getItem('tokenKey')
}

/**
 * 设置(保存)用户的认证令牌
 */
export function setToken(token) {
  return localStorage.setItem('tokenKey', token)
}

/**
 * 移除(删除)用户的认证令牌
 */
export function removeToken() {
  return localStorage.removeItem('tokenKey')
}

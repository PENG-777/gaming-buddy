"""
WebSocket 连接管理（官方客服 + 用户私聊实时推送）

- 浏览器 WebSocket 无法携带 Authorization 请求头, token 改由 query 参数传递, 鉴权逻辑对齐
  core/deps.get_current_login_user(解析 -> 黑名单 -> 有效期), 失败返回 None 由端点关闭连接
- 连接管理为进程内存实现(与 token 黑名单同约束: 仅单进程部署有效)
- 每类连接均按 user_id 注册一条(重复连接踢掉旧的):
  官方客服: user_connections(用户端) + admin_connections(管理端, 广播);
  用户私聊: private_user_connections(用户端) + companion_connections(陪玩师工作台, 定点)
           + private_admin_connections(监管管理员, 广播)
"""
import time  # 标准库: 毫秒时间戳(有效期校验)

from fastapi import WebSocket  # FastAPI: WebSocket 类型标注

from core.security import is_token_blacklisted, parse_login_user  # 项目内: token 解析/黑名单工具
from schemas.vo import LoginUser  # 项目内: 登录用户快照模型


def authenticate_ws(token: str | None) -> LoginUser | None:
    """WebSocket 鉴权: 校验链路与 HTTP 登录依赖一致, 失败返回 None(由端点 close(4401))

    参数: token 从 query 参数拿到的原始 JWT 字符串(浏览器 WS 无法携带请求头)
    """
    if not token:  # 未携带 token
        return None
    login_user = parse_login_user(token)  # 解析 JWT 中的用户快照
    if login_user is None:  # 签名错误/已过期/格式非法
        return None
    if is_token_blacklisted(token):  # 已登出的 token 拒绝连接
        return None
    if login_user.expireTime is None or login_user.expireTime - time.time() * 1000 <= 0:
        return None  # 无过期时间或已过期
    return login_user  # 校验全部通过, 返回登录用户信息


class ConnectionManager:
    """WebSocket 连接管理器(官方客服 + 用户私聊, 各通道连接池相互独立)"""

    def __init__(self):
        self.user_connections: dict[int, WebSocket] = {}  # 客服用户端连接: {user_id: WebSocket}
        self.admin_connections: dict[int, WebSocket] = {}  # 客服管理端连接: {管理员user_id: WebSocket}
        self.private_user_connections: dict[int, WebSocket] = {}  # 私聊用户端连接: {user_id: WebSocket}
        self.companion_connections: dict[int, WebSocket] = {}  # 私聊陪玩师工作台连接: {陪玩师user_id: WebSocket}
        self.private_admin_connections: dict[int, WebSocket] = {}  # 私聊监管管理员连接: {管理员user_id: WebSocket}

    async def _replace(self, pool: dict[int, WebSocket], key: int, ws: WebSocket) -> None:
        """注册连接到指定池(重复连接先断旧, 各池共用策略)

        参数: pool 目标连接池 / key 注册键(通常为 user_id) / ws 新建的 WebSocket 连接
        """
        old = pool.get(key)  # 同 key 的旧连接
        if old is not None and old is not ws:  # 存在旧连接且不是当前连接本身
            try:
                await old.close()  # 关闭旧连接(对方触发断线重连后被新连接替代)
            except Exception:
                pass  # 旧连接已失效则忽略
        pool[key] = ws  # 新连接覆盖注册(同 key 仅保留最新一条)

    @staticmethod
    def _drop(pool: dict[int, WebSocket], key: int, ws: WebSocket) -> None:
        """从指定池移除连接(仅当注册的仍是本连接时才移除, 避免误删新连接)

        参数: pool 目标连接池 / key 注册键 / ws 要移除的连接
        """
        if pool.get(key) is ws:  # 池内注册的仍是本连接(未被新连接覆盖)
            pool.pop(key, None)  # 才真正移除

    @staticmethod
    async def _push(pool: dict[int, WebSocket], key: int, data: dict) -> None:
        """向池内指定 key 的连接推送(不在线静默忽略, 离线消息由 REST 历史兕底)

        参数: pool 目标连接池 / key 目标用户键 / data 推送的 JSON 消息体
        """
        ws = pool.get(key)  # 取目标连接
        if ws is None:
            return  # 不在线直接放弃(离线靠拉历史接口)
        try:
            await ws.send_json(data)  # 向该连接推送 JSON 消息
        except Exception:
            ConnectionManager._drop(pool, key, ws)  # 推送失败视为连接失效, 顺手移除

    async def connect_user(self, user_id: int, ws: WebSocket) -> None:
        """注册客服用户端连接(重复连接先断旧, 保证每用户仅一条活跃连接)

        参数: user_id 用户 ID / ws 新建的 WebSocket 连接
        """
        await self._replace(self.user_connections, user_id, ws)  # 注册到客服用户端池

    def disconnect_user(self, user_id: int, ws: WebSocket) -> None:
        """移除客服用户端连接(仅当注册的仍是本连接时才移除)

        参数: user_id 用户 ID / ws 要移除的连接
        """
        self._drop(self.user_connections, user_id, ws)  # 从客服用户端池移除

    async def connect_admin(self, admin_id: int, ws: WebSocket) -> None:
        """注册客服管理端连接(重复连接先断旧, 与用户端同策略)

        参数: admin_id 管理员用户 ID / ws 新建的 WebSocket 连接
        """
        await self._replace(self.admin_connections, admin_id, ws)  # 注册到客服管理端池

    def disconnect_admin(self, admin_id: int, ws: WebSocket) -> None:
        """移除客服管理端连接(仅当注册的仍是本连接时才移除)

        参数: admin_id 管理员用户 ID / ws 要移除的连接
        """
        self._drop(self.admin_connections, admin_id, ws)  # 从客服管理端池移除

    async def push_to_user(self, user_id: int, data: dict) -> None:
        """向指定用户推送客服消息(不在线静默忽略, 离线消息由 REST 历史兕底)

        参数: user_id 目标用户 ID / data 推送的 JSON 消息体
        """
        await self._push(self.user_connections, user_id, data)  # 定点推送到客服用户端池

    async def push_to_admins(self, data: dict) -> None:
        """向所有在线客服管理员广播(多客服工作台同步)

        参数: data 推送的 JSON 消息体
        """
        await self._broadcast(self.admin_connections, data)  # 广播到客服管理端池

    # ==================== 用户私聊通道 ====================

    async def connect_private_user(self, user_id: int, ws: WebSocket) -> None:
        """注册私聊用户端连接(重复连接先断旧, 与客服用户端分池互不影响)

        参数: user_id 用户 ID / ws 新建的 WebSocket 连接
        """
        await self._replace(self.private_user_connections, user_id, ws)  # 注册到私聊用户端池

    def disconnect_private_user(self, user_id: int, ws: WebSocket) -> None:
        """移除私聊用户端连接(仅当注册的仍是本连接时才移除)

        参数: user_id 用户 ID / ws 要移除的连接
        """
        self._drop(self.private_user_connections, user_id, ws)  # 从私聊用户端池移除

    async def push_to_private_user(self, user_id: int, data: dict) -> None:
        """向指定用户推送私聊消息(陪玩师回复; 不在线静默忽略, REST 历史兕底)

        参数: user_id 目标用户 ID / data 推送的 JSON 消息体
        """
        await self._push(self.private_user_connections, user_id, data)  # 定点推送到私聊用户端池

    async def connect_companion(self, companion_user_id: int, ws: WebSocket) -> None:
        """注册陪玩师工作台连接(按陪玩师登录账号 user_id, 重复连接先断旧)

        参数: companion_user_id 陪玩师登录账号的用户 ID / ws 新建的 WebSocket 连接
        """
        await self._replace(self.companion_connections, companion_user_id, ws)  # 注册到陪玩师工作台池

    def disconnect_companion(self, companion_user_id: int, ws: WebSocket) -> None:
        """移除陪玩师工作台连接(仅当注册的仍是本连接时才移除)

        参数: companion_user_id 陪玩师登录账号的用户 ID / ws 要移除的连接
        """
        self._drop(self.companion_connections, companion_user_id, ws)  # 从陪玩师工作台池移除

    async def push_to_companion(self, companion_user_id: int, data: dict) -> None:
        """向指定陪玩师工作台推送(用户发来私聊; 不在线静默忽略)

        参数: companion_user_id 陪玩师登录账号的用户 ID / data 推送的 JSON 消息体
        """
        await self._push(self.companion_connections, companion_user_id, data)  # 定点推送到陪玩师工作台池

    async def connect_private_admin(self, admin_id: int, ws: WebSocket) -> None:
        """注册私聊监管管理员连接(重复连接先断旧)

        参数: admin_id 管理员用户 ID / ws 新建的 WebSocket 连接
        """
        await self._replace(self.private_admin_connections, admin_id, ws)  # 注册到私聊监管池

    def disconnect_private_admin(self, admin_id: int, ws: WebSocket) -> None:
        """移除私聊监管管理员连接(仅当注册的仍是本连接时才移除)

        参数: admin_id 管理员用户 ID / ws 要移除的连接
        """
        self._drop(self.private_admin_connections, admin_id, ws)  # 从私聊监管池移除

    async def push_to_private_admins(self, data: dict) -> None:
        """向所有在线监管管理员广播(工作台/监管页多开同步)

        参数: data 推送的 JSON 消息体
        """
        await self._broadcast(self.private_admin_connections, data)  # 广播到私聊监管池

    async def _broadcast(self, pool: dict[int, WebSocket], data: dict) -> None:
        """向池内全部连接广播(失败连接顺手移除)

        参数: pool 目标连接池 / data 推送的 JSON 消息体
        """
        dead = []  # 推送失败的连接(稍后统一移除)
        for key, ws in list(pool.items()):  # 复制快照遍历(避免边发边删)
            try:
                await ws.send_json(data)  # 逐个推送 JSON 消息
            except Exception:
                dead.append((key, ws))  # 记录失败连接, 循环后统一清理
        for key, ws in dead:
            self._drop(pool, key, ws)  # 移除失效连接


# 模块级单例: 全进程共享一份连接表
manager = ConnectionManager()
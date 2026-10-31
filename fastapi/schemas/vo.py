"""
视图对象（登录用户身份与用户信息快照）

字段名直接使用 camelCase, 与前端交互的 JSON 键保持一致。
createTime 为 'yyyy-MM-dd HH:mm:ss' 字符串。
"""
from typing import Optional  # 标准库: 可空类型标注

from pydantic import BaseModel, ConfigDict  # 第三方: 模型基类与配置


class UserSnapshot(BaseModel):
    """用户信息快照: 存放在 token 的 user_key 声明中"""
    model_config = ConfigDict(extra="ignore")  # 忽略多余字段(保证旧 token 兼容)

    userId: Optional[int] = None  # 用户ID
    userName: Optional[str] = None  # 用户名
    sex: Optional[int] = None  # 性别
    avatar: Optional[str] = None  # 头像 URL
    createTime: Optional[str] = None  # 创建时间('yyyy-MM-dd HH:mm:ss' 字符串)
    roleId: Optional[int] = None  # 角色 ID
    roleName: Optional[str] = None  # 角色名称


class LoginUser(BaseModel):
    """登录用户身份, extra=ignore 忽略声明中的多余字段"""
    model_config = ConfigDict(extra="ignore")  # 忽略声明中多余字段(保证旧 token 兼容)

    userId: Optional[int] = None  # 用户ID
    loginTime: Optional[int] = None  # 登录时间(毫秒时间戳, 签发 token 时写入)
    expireTime: Optional[int] = None  # 过期时间(毫秒时间戳, 签发 token 时写入)
    user: Optional[UserSnapshot] = None  # 用户信息快照

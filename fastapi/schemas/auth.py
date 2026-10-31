"""
请求体模型（登录 / 注册 / 重置密码）

登录兼容旧短密码不加最小长度; 注册/新密码要求至少 6 位。
"""
from typing import Optional  # 标准库: 可空类型标注

from pydantic import BaseModel, ConfigDict, Field  # 第三方: 请求体模型基类与配置/字段约束


class LoginBody(BaseModel):
    """登录请求体"""
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    userName: Optional[str] = Field(None, max_length=50)  # 用户名
    password: Optional[str] = Field(None, max_length=100)  # 密码(不加最小长度, 兼容旧密码)


class RegisterBody(BaseModel):
    """注册请求体"""
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    userName: Optional[str] = Field(None, max_length=50)  # 用户名
    password: Optional[str] = Field(None, min_length=6, max_length=100)  # 密码(至少 6 位)


class SubmitPwdBody(BaseModel):
    """重置密码请求体"""
    model_config = ConfigDict(extra="ignore")  # 忽略请求中多余字段

    oldPassword: Optional[str] = Field(None, max_length=100)  # 旧密码
    newPassword: Optional[str] = Field(None, min_length=6, max_length=100)  # 新密码(至少 6 位)

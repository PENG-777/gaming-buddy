"""
自定义异常

- AuthError: 认证失败(未登录/token过期/token无效), 返回 HTTP 401 + {code:401, msg}
- ApiError:  业务异常, 返回 HTTP 500 + {code:500, msg}
- 普通业务失败是 HTTP 200 + code 500, 见 core/response.py
"""


class AuthError(Exception):
    """认证失败(未登录/token过期/token无效/token已登出)"""

    def __init__(self, msg: str = "登录已过期, 请重新登录"):  # 默认提示文案
        self.msg = msg  # 保存文案, 供全局异常处理器读取
        super().__init__(msg)  # 同步传给 Exception 基类


class ApiError(Exception):
    """业务异常"""

    def __init__(self, msg: str):  # 必传业务错误信息
        self.msg = msg  # 保存文案, 供全局异常处理器读取
        super().__init__(msg)  # 同步传给 Exception 基类

"""个人中心（/system/user/profile 前缀）"""
# 标准库: 文件/目录操作(旧头像清理)
import os

# FastAPI: 路由/文件上传/请求头
from fastapi import APIRouter, File, Header, UploadFile

from core.config import settings  # 项目内: 上传基础路径
from core.deps import DbDep, LoginUserDep  # 项目内: 通用依赖(登录校验/请求级 Session)
from core.files import save_upload  # 项目内: 通用文件保存(分块写盘)
from core.response import ajax_error, ajax_success, to_ajax  # 项目内: 统一响应
from core.security import extract_token, invalidate_token, parse_token  # 项目内: token 提取/拉黑/解析
from schemas.auth import SubmitPwdBody  # 项目内: 重置密码请求体
from schemas.body import UserBody  # 项目内: 用户请求体
from services import user_service  # 项目内: 用户业务层

router = APIRouter(prefix="/system/user/profile", tags=["profile"])  # 模块路由器


def _remove_old_avatar(old_url: str | None) -> None:
    """删除旧头像磁盘文件(仅清理头像目录内的文件, 任何异常忽略)"""
    if not old_url or not old_url.startswith("/profile/avatar/"):
        return  # 空地址或非本地上传的头像不处理
    file_path = os.path.join(settings.profile, "avatar", os.path.basename(old_url))  # 拼出磁盘路径
    try:
        os.remove(file_path)
    except OSError:
        pass  # 文件不存在/被占用等情况直接忽略, 不影响头像更新


@router.post("/avatar")
async def avatar(login_user: LoginUserDep, db: DbDep,
                 file: UploadFile = File(...)):
    """上传头像: 存 {profile}/avatar, 成功返回新头像地址(旧头像文件同步清理)"""
    try:
        saved = await save_upload(file, "avatar")  # 通用保存(UUID去横线+扩展名命名, 分块写盘)
        old_url = user_service.get_user_avatar(db, login_user.userId)  # 更新前的旧头像地址
        if user_service.update_user_avatar(db, login_user.userId, saved["url"]) > 0:  # 更新库中头像
            _remove_old_avatar(old_url)  # 清理已被替换的旧头像文件(失败不影响结果)
            return ajax_success(imgUrl=saved["url"])  # 返回新头像地址
    except ValueError:  # 空文件由 save_upload 抛出, 走统一失败提示
        pass
    return ajax_error("上传头像失败, 请重新上传")  # 空文件/更新失败


@router.put("")
def update_profile(body: UserBody, login_user: LoginUserDep, db: DbDep):
    """修改个人信息: 用户名/性别以请求为准, 头像仅在传入非空时更新"""
    if login_user.userId is None:  # 无用户ID直接失败
        return to_ajax(0)

    if body.userName is not None and user_service.user_name_taken(db, body.userName, login_user.userId):
        return ajax_error("用户名已存在")  # 改名查重(排除自己, 防止顶替他人账户)

    fields: dict = {}  # 待更新列(仅收集非空字段)
    if body.userName is not None:  # 用户名以请求为准
        fields["user_name"] = body.userName
    if body.sex is not None:  # 性别以请求为准
        fields["sex"] = body.sex
    if body.avatar:  # 头像仅在传入非空时更新
        fields["avatar"] = body.avatar
    return to_ajax(user_service.update_user_by_id(db, login_user.userId, fields))  # 动态更新


@router.put("/updatePwd")
def update_pwd(body: SubmitPwdBody, login_user: LoginUserDep, db: DbDep,
               authorization: str | None = Header(default=None)):  # 提取当前请求的 token(改密成功后拉黑)
    current = user_service.get_user_password(db, login_user.userId)  # 从库里取当前密码(token 快照可能已过期)
    if current is None:  # 用户不存在
        return ajax_error("修改密码失败, 请重新填写后提交")

    if body.newPassword == current:  # 新旧密码相同
        return ajax_error("新密码不能与旧密码相同")
    if body.oldPassword != current:  # 旧密码不正确
        return ajax_error("旧密码错误")

    if user_service.reset_user_pwd(db, login_user.userId, body.newPassword) > 0:  # 更新成功
        token = extract_token(authorization)  # 提取当前 token
        if token:  # 拉黑当前 token, 强制重新登录(旧密码已失效)
            claims = parse_token(token)  # 解析声明(拿过期时间)
            if claims and "exp" in claims:
                invalidate_token(token, claims["exp"] * 1000)  # 拉黑至自然过期(秒转毫秒)
        return ajax_success()
    return ajax_error("修改密码失败, 请重新填写后提交")  # 更新失败

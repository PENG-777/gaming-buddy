"""
通用文件保存

收敛 routers/file.py 与 routers/profile.py 原本各自实现的"UUID 命名 + 写盘"逻辑,
新模块需要落盘上传文件时直接调用 save_upload, 不再复制粘贴。

命名规则(与既有行为保持一致):
- 头像(sub_dir="avatar", with_original_stem=False): UUID去横线 + 扩展名
- 通用上传(sub_dir="upload", with_original_stem=True): UUID去横线_原文件主名 + 扩展名
写盘采用分块读取(8192 字节循环), 避免大文件一次性读入内存。
对外访问 URL 由 main.py 的 StaticFiles 挂载提供: /profile/{sub_dir}/{文件名}
"""
import os  # 标准库: 文件/目录操作
import uuid  # 标准库: 生成唯一文件名

from fastapi import UploadFile  # FastAPI: 上传文件类型

from core.config import settings  # 项目内: 读取上传基础路径

_CHUNK_SIZE = 8192  # 分块读写字节数(8KB, 平衡内存占用与写盘次数)


def _split_filename(original: str) -> tuple[str, str]:
    """原始文件名 -> (主名, 含点扩展名); 无扩展名时扩展名为空串"""
    if "." in original:  # 原名含点
        dot = original.rfind(".")  # 最后一个点位置(视为扩展名分隔)
        return original[:dot], original[dot:]
    return original, ""  # 无点: 整体为主名, 无扩展名


async def save_upload(file: UploadFile, sub_dir: str, with_original_stem: bool = False) -> dict:
    """保存上传文件到 {profile}/{sub_dir}/, 返回 {url, newFileName, originalFilename}

    - sub_dir: 子目录名(如 "avatar" / "upload")
    - with_original_stem: True 时文件名拼入原文件主名(通用上传规则), False 时仅 UUID+扩展名(头像规则)
    - 内容为空时抛 ValueError, 由调用方决定如何提示
    """
    original_filename = file.filename or ""  # 原始文件名(可能为空)
    stem, extension = _split_filename(original_filename)  # 拆出主名与扩展名

    # 唯一文件名: UUID去横线(+ 原主名)+ 扩展名, 规则由 with_original_stem 决定
    unique_stem = uuid.uuid4().hex + ("_" + stem if with_original_stem and stem else "")
    unique_filename = unique_stem + extension

    upload_dir = os.path.join(settings.profile, sub_dir)  # 目标目录: {profile}/{sub_dir}
    os.makedirs(upload_dir, exist_ok=True)  # 目录不存在则创建

    first = await file.read(_CHUNK_SIZE)  # 先读第一块(用于空文件判断)
    if not first:  # 空文件没有保存意义
        raise ValueError("上传文件内容为空")

    file_path = os.path.join(upload_dir, unique_filename)  # 完整落盘路径
    with open(file_path, "wb") as f:  # 二进制写文件
        f.write(first)  # 先写第一块
        while chunk := await file.read(_CHUNK_SIZE):  # 继续分块读取直到读空(walrus 循环)
            f.write(chunk)  # 逐块写盘, 大文件不占内存

    return {
        "url": f"/profile/{sub_dir}/{unique_filename}",  # 对外访问 URL(静态挂载)
        "newFileName": unique_filename,  # 存储的唯一文件名
        "originalFilename": original_filename,  # 原始文件名
    }

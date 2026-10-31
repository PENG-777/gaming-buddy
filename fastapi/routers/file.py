"""文件上传（/file 前缀）"""
# FastAPI: 路由/文件上传
from fastapi import APIRouter, File, UploadFile

from core.deps import LoginUserDep  # 项目内: 通用依赖(登录校验, 上传需认证)
from core.files import save_upload  # 项目内: 通用文件保存(分块写盘)
from core.response import ajax_error, ajax_success_data  # 项目内: 统一响应

router = APIRouter(prefix="/file", tags=["file"])  # 模块路由器


@router.post("/upload")
async def upload_file(login_user: LoginUserDep,
                      file: UploadFile = File(...)):
    """文件上传: 文件名 = UUID去横线 + '_' + 原始文件名 + 扩展名"""
    try:  # 上传过程任何异常统一转业务失败
        saved = await save_upload(file, "upload", with_original_stem=True)  # 通用保存(UUID_原主名.扩展名)
        return ajax_success_data({  # 返回前端上传组件需要的字段
            "url": saved["url"],  # 访问地址
            "fileName": saved["url"],  # 文件名(同地址)
            "newFileName": saved["newFileName"],  # 存储的唯一文件名
            "originalFilename": saved["originalFilename"],  # 原始文件名
        })
    except Exception as e:
        return ajax_error(f"文件上传失败: {e}")  # HTTP 200 + code 500

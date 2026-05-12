"""
压缩上传图片的工具模块
在 Photo.save() 中调用
"""
from PIL import Image
import io
import os


def compress_image(image_field, max_size=(1920, 1920), quality=85):
    """
    压缩图片文件

    参数:
        image_field: Django的ImageField或FileField
        max_size: 最大尺寸元组，默认(1920, 1920)
        quality: JPEG质量，默认85

    返回:
        bool: 是否成功压缩
    """
    try:
        if not image_field:
            return False

        filepath = image_field.path
        if not os.path.exists(filepath):
            return False

        img = Image.open(filepath)

        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        img.save(filepath, 'JPEG', quality=quality, optimize=True)

        return True

    except Exception as e:
        print(f"图片压缩失败: {e}")
        return False


def compress_image_from_upload(uploaded_file, max_size=(1920, 1920), quality=85):
    """
    压缩上传的文件对象

    参数:
        uploaded_file: Django的上传文件对象 (InMemoryUploadedFile or TemporaryUploadedFile)
        max_size: 最大尺寸元组，默认(1920, 1920)
        quality: JPEG质量，默认85

    返回:
        BytesIO: 压缩后的文件对象，或None
    """
    try:
        if not uploaded_file:
            return None

        img = Image.open(uploaded_file)

        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)

        return output

    except Exception as e:
        print(f"图片压缩失败: {e}")
        return None

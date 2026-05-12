"""
压缩上传图片的模块
在 Photo.save() 中自动调用
也可用作独立工具模块

使用方法:
    1. 作为Django信号自动执行（已集成到Photo模型save方法）
    2. 手动调用: python compress_remote_photo.py
"""
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
import io
import os


def compress_uploaded_image(uploaded_file, max_size=(1920, 1920), quality=85):
    """
    压缩上传的图片文件

    参数:
        uploaded_file: Django的上传文件对象
        max_size: 最大尺寸元组，默认(1920, 1920)
        quality: JPEG质量，默认85

    返回:
        InMemoryUploadedFile: 压缩后的文件对象，或原文件
    """
    try:
        if not uploaded_file:
            return uploaded_file

        img = Image.open(uploaded_file)

        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)

        filename = os.path.splitext(uploaded_file.name)[0] + '.jpg'

        return InMemoryUploadedFile(
            output,
            'image',
            filename,
            'image/jpeg',
            output.getbuffer().nbytes,
            uploaded_file.charset or 'utf-8'
        )

    except Exception as e:
        print(f"图片压缩失败: {e}")
        return uploaded_file


def compress_image_file(filepath, max_size=(1920, 1920), quality=85):
    """
    压缩指定路径的图片文件

    参数:
        filepath: 图片文件的完整路径
        max_size: 最大尺寸元组，默认(1920, 1920)
        quality: JPEG质量，默认85

    返回:
        bool: 是否成功
    """
    try:
        if not filepath or not os.path.exists(filepath):
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


if __name__ == '__main__':
    print("此模块应在 Django 项目中通过 Photo.save() 自动调用")
    print("或在其他 Python 脚本中导入使用:")
    print("    from photos.utils import compress_image_file")
    print("    compress_image_file('/path/to/image.jpg')")

"""
压缩服务器上所有照片的脚本
使用方法：python compress_host_photo.py
"""
import os
import sys
from PIL import Image

def compress_directory(directory, max_size=(1920, 1920), quality=85):
    """压缩指定目录下的所有图片"""
    compressed_count = 0
    total_count = 0

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                filepath = os.path.join(root, filename)
                total_count += 1

                try:
                    img = Image.open(filepath)

                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')

                    original_size = os.path.getsize(filepath)

                    img.thumbnail(max_size, Image.Resampling.LANCZOS)

                    img.save(filepath, 'JPEG', quality=quality, optimize=True)

                    new_size = os.path.getsize(filepath)
                    saved = original_size - new_size
                    saved_kb = saved / 1024

                    print(f"[{compressed_count + 1}] {filename}")
                    print(f"    原始: {original_size / 1024 / 1024:.2f} MB -> 压缩后: {new_size / 1024 / 1024:.2f} MB")
                    print(f"    节省: {saved_kb:.1f} KB ({(saved / original_size * 100):.1f}%)")
                    print()

                    compressed_count += 1

                except Exception as e:
                    print(f"[X] {filename} 失败: {e}")

    print("=" * 50)
    print(f"完成！共处理 {total_count} 张图片")
    print(f"成功压缩 {compressed_count} 张")

    return compressed_count


if __name__ == '__main__':
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'family_album.settings')
    django.setup()

    from photos.models import Photo

    print("=" * 50)
    print("开始压缩服务器上的照片...")
    print("=" * 50)
    print()

    media_root = '/Users/gdlocal/Flex/100_Projects_WP/Family_Album/media'

    if os.path.exists(media_root):
        compress_directory(media_root)
    else:
        print(f"目录不存在: {media_root}")

    print()
    print("=" * 50)
    print("所有图片压缩完成！")
    print("=" * 50)

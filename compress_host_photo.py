"""
压缩服务器上所有照片的脚本
使用方法：python compress_host_photo.py
目标：将10MB照片压缩到约1MB
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'family_album.settings')
django.setup()

from django.conf import settings
from PIL import Image


def compress_to_target_size(filepath, target_size_mb=1, initial_quality=85, max_iterations=3):
    """
    压缩图片到目标大小（MB）

    参数:
        filepath: 图片路径
        target_size_mb: 目标大小（MB），默认1MB
        initial_quality: 初始质量
        max_iterations: 最大迭代次数

    返回:
        tuple: (是否成功, 压缩后大小)
    """
    target_bytes = target_size_mb * 1024 * 1024
    quality = initial_quality
    max_size = (1920, 1920)

    for iteration in range(max_iterations):
        try:
            img = Image.open(filepath)

            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            img.save(filepath, 'JPEG', quality=quality, optimize=True)

            current_size = os.path.getsize(filepath)

            if current_size <= target_bytes:
                return True, current_size

            quality -= 15
            if quality < 30:
                quality = 30

        except Exception as e:
            print(f"      压缩失败: {e}")
            return False, 0

    return False, os.path.getsize(filepath)


def compress_directory(directory, target_size_mb=1, max_size=(1920, 1920), quality=70):
    """压缩指定目录下的所有图片到目标大小"""
    compressed_count = 0
    total_count = 0
    total_saved = 0

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                filepath = os.path.join(root, filename)
                total_count += 1

                try:
                    original_size = os.path.getsize(filepath)
                    original_mb = original_size / 1024 / 1024

                    if original_mb <= target_size_mb:
                        print(f"[{compressed_count + 1}] {filename}")
                        print(f"    原始: {original_mb:.2f} MB -> 无需压缩（已小于{target_size_mb}MB）")
                        print()
                        compressed_count += 1
                        continue

                    success, new_size = compress_to_target_size(filepath, target_size_mb)
                    new_mb = new_size / 1024 / 1024
                    saved = original_size - new_size
                    total_saved += saved

                    print(f"[{compressed_count + 1}] {filename}")
                    print(f"    原始: {original_mb:.2f} MB -> 压缩后: {new_mb:.2f} MB")

                    if saved > 0:
                        print(f"    节省: {saved / 1024:.1f} KB ({(saved / original_size * 100):.1f}%)")
                    elif new_mb > target_size_mb:
                        print(f"    警告: 仍为 {new_mb:.2f} MB（未达到{target_size_mb}MB目标）")
                    print()

                    compressed_count += 1

                except Exception as e:
                    print(f"[X] {filename} 失败: {e}")

    print("=" * 50)
    print(f"完成！共处理 {total_count} 张图片")
    print(f"成功压缩 {compressed_count} 张")
    print(f"总共节省: {total_saved / 1024 / 1024:.2f} MB")

    return compressed_count


if __name__ == '__main__':
    target_mb = 1

    print("=" * 50)
    print(f"开始压缩照片（目标：每张约{target_mb}MB）...")
    print("=" * 50)
    print()

    media_root = settings.MEDIA_ROOT

    print(f"图片目录: {media_root}")
    print()

    if os.path.exists(media_root):
        compress_directory(media_root, target_size_mb=target_mb)
    else:
        print(f"目录不存在: {media_root}")
        print("请检查 settings.py 中的 MEDIA_ROOT 配置")

    print()
    print("=" * 50)
    print("所有图片压缩完成！")
    print("=" * 50)

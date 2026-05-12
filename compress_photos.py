"""
压缩服务器上所有照片的脚本
使用方法：python manage.py compress_photos
"""
from photos.models import Photo
from PIL import Image
import os

def compress_all_photos():
    photos = Photo.objects.all()
    total = photos.count()
    compressed = 0

    print(f"开始压缩 {total} 张照片...")

    for photo in photos:
        if photo.image:
            filepath = photo.image.path
            if os.path.exists(filepath):
                try:
                    img = Image.open(filepath)
                    original_size = os.path.getsize(filepath)

                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')

                    max_size = (1920, 1920)
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)

                    img.save(filepath, 'JPEG', quality=85, optimize=True)

                    new_size = os.path.getsize(filepath)
                    saved = original_size - new_size
                    compressed += 1

                    if compressed % 10 == 0:
                        print(f"已压缩 {compressed}/{total} 张，节省 {saved/1024:.1f} KB")

                except Exception as e:
                    print(f"压缩失败 {photo.title}: {e}")

    print(f"\n完成！共压缩 {compressed} 张照片")

if __name__ == '__main__':
    compress_all_photos()

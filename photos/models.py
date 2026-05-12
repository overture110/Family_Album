from django.db import models
from django.utils import timezone
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


class Album(models.Model):
    name = models.CharField(max_length=100)
    folder_name = models.CharField(max_length=100, unique=True, default='default_album')
    year = models.IntegerField(default=2024)
    album_date = models.DateField(default='2024-01-01')
    is_holiday = models.BooleanField(default=False)
    holiday_name = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    cover_photo = models.ForeignKey(
        'Photo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cover_for_albums'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-album_date']

    def __str__(self):
        return f"{self.name} ({self.album_date})"

    @property
    def date_display(self):
        if self.is_holiday:
            return self.album_date.strftime('%Y年%m月') + f" · {self.holiday_name}"
        return self.album_date.strftime('%Y年%m月')

    @property
    def folder_display(self):
        if self.is_holiday:
            return f"{self.year}_{self.holiday_name}"
        return self.album_date.strftime('%Y%m')


def photo_upload_to(instance, filename):
    return f"albums/{instance.album.folder_name}/{filename}"


class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    image = models.FileField(upload_to=photo_upload_to)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    taken_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-taken_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk is None:
            img = Image.open(self.image)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            max_size = (1920, 1920)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)

            filename = os.path.basename(self.image.name)
            self.image.save(filename, output, save=False)

        super().save(*args, **kwargs)
        if self.album and not self.album.cover_photo:
            self.album.cover_photo = self
            self.album.save(update_fields=['cover_photo'])

    @property
    def thumbnail_url(self):
        return self.image.url

    @property
    def medium_url(self):
        return self.image.url


class LoginAttempt(models.Model):
    device_id = models.CharField(max_length=255, unique=True)
    login_count = models.IntegerField(default=0)
    last_login_date = models.DateField(default=timezone.now)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_login_date']

    def __str__(self):
        return f"{self.device_id} - {self.login_count} attempts on {self.last_login_date}"

    def check_and_record_login(self):
        today = timezone.now().date()
        if self.last_login_date < today:
            self.login_count = 0
            self.is_blocked = False
            self.last_login_date = today
        if self.login_count >= 5:
            self.is_blocked = True
            return False
        self.login_count += 1
        self.save()
        return True

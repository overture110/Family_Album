from django.contrib import admin
from .models import Album, Photo


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'year', 'created_at']
    list_filter = ['year']
    search_fields = ['name']
    inlines = [PhotoInline]


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'album', 'taken_date', 'created_at']
    list_filter = ['album', 'taken_date']
    search_fields = ['title', 'description']
    date_hierarchy = 'taken_date'

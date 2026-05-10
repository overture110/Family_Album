from django.contrib import admin
from .models import Album, Photo


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1
    fields = ['title', 'image', 'taken_date', 'description']


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'folder_name', 'year', 'album_date', 'is_holiday', 'holiday_name']
    list_filter = ['year', 'is_holiday', 'created_at']
    search_fields = ['name', 'folder_name', 'holiday_name']
    readonly_fields = ['created_at']
    inlines = [PhotoInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'folder_name', 'year', 'album_date')
        }),
        ('节日标签', {
            'fields': ('is_holiday', 'holiday_name'),
            'classes': ('collapse',)
        }),
        ('高级', {
            'fields': ('cover_photo', 'description'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'album', 'taken_date', 'created_at']
    list_filter = ['album', 'taken_date']
    search_fields = ['title', 'description']
    date_hierarchy = 'taken_date'

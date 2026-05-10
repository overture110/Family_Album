from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView
from django.core.paginator import Paginator
from .models import Photo, Album
from collections import defaultdict


class HomeView(TemplateView):
    template_name = 'photos/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['carousel_photos'] = Photo.objects.order_by('-taken_date')[:10]
        context['recent_photos'] = Photo.objects.order_by('-taken_date')[:20]
        context['family_mottos'] = [
            {'title': '敬爱', 'subtitle': '敬', 'content': '成员互敬，长幼互爱。'},
            {'title': '关怀', 'subtitle': '关', 'content': '远婚姻干涉，近生活冷暖。'},
            {'title': '通达', 'subtitle': '通', 'content': '凡事有交代，沟通不隔夜。'},
            {'title': '包容', 'subtitle': '包', 'content': '礼待传统，亦守自由。'},
            {'title': '共生', 'subtitle': '共', 'content': '爱己为本，舍己为家。'},
        ]
        return context


class MottoView(TemplateView):
    template_name = 'photos/motto.html'


class TimelineView(ListView):
    template_name = 'photos/timeline.html'
    model = Album
    context_object_name = 'albums'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        albums = context['albums']
        albums_by_year = defaultdict(list)
        for album in albums:
            albums_by_year[album.year].append(album)
        albums_by_year = dict(sorted(albums_by_year.items(), reverse=True))
        context['albums_by_year'] = albums_by_year
        context['years'] = sorted(albums_by_year.keys(), reverse=True)
        return context


class AlbumDetailView(DetailView):
    template_name = 'photos/album_detail.html'
    model = Album
    context_object_name = 'album'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = self.object.photos.all()
        return context


class PhotoDetailView(DetailView):
    template_name = 'photos/photo_detail.html'
    model = Photo
    context_object_name = 'photo'


def api_photos(request):
    year = request.GET.get('year')
    album_id = request.GET.get('album_id')
    if album_id:
        photos = Photo.objects.filter(album_id=album_id)
    elif year:
        photos = Photo.objects.filter(album__year=year)
    else:
        photos = Photo.objects.all()
    data = [
        {
            'id': p.id,
            'src': p.image.url,
            'title': p.title,
            'date': p.taken_date.strftime('%Y-%m-%d'),
            'album': p.album.name,
            'album_id': p.album.id
        }
        for p in photos
    ]
    return JsonResponse(data, safe=False)


def api_albums(request):
    year = request.GET.get('year')
    album_id = request.GET.get('album_id')
    if album_id:
        albums = Album.objects.filter(id=album_id)
    elif year:
        albums = Album.objects.filter(year=year)
    else:
        albums = Album.objects.all()
    data = [
        {
            'id': a.id,
            'name': a.name,
            'year': a.year,
            'date_display': a.date_display,
            'folder_display': a.folder_display,
            'is_holiday': a.is_holiday,
            'holiday_name': a.holiday_name,
            'photo_count': a.photos.count(),
            'cover_url': a.cover_photo.image.url if a.cover_photo else None
        }
        for a in albums
    ]
    return JsonResponse(data, safe=False)

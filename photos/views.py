from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView
from .models import Photo, Album


class HomeView(TemplateView):
    template_name = 'photos/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['carousel_photos'] = Photo.objects.order_by('-taken_date')[:10]
        context['recent_photos'] = Photo.objects.order_by('-taken_date')[:20]
        return context


class TimelineView(ListView):
    template_name = 'photos/timeline.html'
    model = Album
    context_object_name = 'albums'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for album in context['albums']:
            album.photo_count = album.photos.count()
        return context


class PhotoDetailView(DetailView):
    template_name = 'photos/photo_detail.html'
    model = Photo
    context_object_name = 'photo'


def api_photos(request):
    year = request.GET.get('year')
    if year:
        photos = Photo.objects.filter(album__year=year)
    else:
        photos = Photo.objects.all()
    data = [
        {
            'id': p.id,
            'src': p.image.url,
            'title': p.title,
            'date': p.taken_date.strftime('%Y-%m-%d'),
            'album': p.album.name
        }
        for p in photos
    ]
    return JsonResponse(data, safe=False)

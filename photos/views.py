from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView
from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Photo, Album, LoginAttempt
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


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return ip


class LoginView(TemplateView):
    template_name = 'photos/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        device_id = self.request.session.get('device_id')
        if not device_id:
            import uuid
            device_id = str(uuid.uuid4())
            self.request.session['device_id'] = device_id
        context['device_id'] = device_id

        today = timezone.now().date()
        login_record, created = LoginAttempt.objects.get_or_create(
            device_id=device_id,
            defaults={'login_count': 0, 'last_login_date': today, 'is_blocked': False}
        )
        if login_record.last_login_date < today:
            login_record.login_count = 0
            login_record.is_blocked = False
            login_record.last_login_date = today
            login_record.save()

        context['remaining_attempts'] = max(0, 5 - login_record.login_count)
        context['is_blocked'] = login_record.is_blocked
        return context

    def post(self, request, *args, **kwargs):
        device_id = request.session.get('device_id')
        if not device_id:
            import uuid
            device_id = str(uuid.uuid4())
            request.session['device_id'] = device_id

        today = timezone.now().date()
        login_record, created = LoginAttempt.objects.get_or_create(
            device_id=device_id,
            defaults={'login_count': 0, 'last_login_date': today, 'is_blocked': False}
        )

        if login_record.is_blocked:
            return render(request, 'photos/login.html', {
                'error': '今日登录次数已用完，请明天再试',
                'is_blocked': True,
                'device_id': device_id
            })

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = None
        if username == 'admin' and password == '1234$#@!':
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(username='admin')
            except User.DoesNotExist:
                user = User.objects.create_superuser('admin', 'admin@family.com', '1234$#@!')

        if user:
            from django.contrib.auth import login as django_login
            django_login(request, user)
            login_record.login_count = 0
            login_record.save()
            return HttpResponseRedirect('/manage/')
        else:
            allowed = login_record.check_and_record_login()
            remaining = max(0, 5 - login_record.login_count)
            return render(request, 'photos/login.html', {
                'error': f'用户名或密码错误，剩余尝试次数: {remaining}',
                'remaining_attempts': remaining,
                'is_blocked': login_record.is_blocked,
                'device_id': device_id
            })


class ManageAlbumsView(TemplateView):
    template_name = 'photos/manage_albums.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            return context
        context['albums'] = Album.objects.all().order_by('-album_date')
        return context

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/login/')
        return super().dispatch(request, *args, **kwargs)


def upload_photos(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': '请先登录'}, status=401)

    if request.method == 'POST':
        import os
        from datetime import datetime
        from django.conf import settings

        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        taken_date_str = request.POST.get('taken_date', '')
        album_folder = request.POST.get('album_folder', '')
        files = request.FILES.getlist('photos')

        if not taken_date_str:
            return JsonResponse({'success': False, 'error': '请选择拍摄日期'})

        try:
            taken_date = datetime.strptime(taken_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'error': '日期格式错误'})

        folder_year = taken_date.strftime('%Y')
        folder_month = taken_date.strftime('%m')

        if album_folder:
            folder_name = album_folder
            album, created = Album.objects.get_or_create(
                folder_name=folder_name,
                defaults={
                    'name': f'{folder_name[:4]}年{folder_name[4:6]}月',
                    'year': int(folder_year),
                    'album_date': taken_date,
                }
            )
        else:
            folder_name = f'{folder_year}{folder_month}'
            album, created = Album.objects.get_or_create(
                folder_name=folder_name,
                defaults={
                    'name': f'{folder_year}年{folder_month}月',
                    'year': int(folder_year),
                    'album_date': taken_date,
                }
            )

        upload_dir = os.path.join(settings.MEDIA_ROOT, 'albums', folder_name)
        os.makedirs(upload_dir, exist_ok=True)

        uploaded = []
        for f in files:
            photo = Photo.objects.create(
                album=album,
                image=f,
                title=title or f.name,
                description=description,
                taken_date=taken_date,
            )
            uploaded.append({
                'id': photo.id,
                'title': photo.title,
                'url': photo.image.url
            })

        return JsonResponse({
            'success': True,
            'uploaded': uploaded,
            'album_id': album.id,
            'album_name': album.name
        })

    return JsonResponse({'success': False, 'error': '仅支持POST请求'})


def delete_photo(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': '请先登录'}, status=401)

    if request.method == 'POST':
        import os
        from django.conf import settings

        photo_id = request.POST.get('photo_id')
        if not photo_id:
            return JsonResponse({'success': False, 'error': '缺少照片ID'})

        try:
            photo = Photo.objects.get(id=photo_id)
        except Photo.DoesNotExist:
            return JsonResponse({'success': False, 'error': '照片不存在'})

        album = photo.album
        folder_name = album.folder_name
        album_dir = os.path.join(settings.MEDIA_ROOT, 'albums', folder_name)

        if photo.image:
            file_path = photo.image.path
            if os.path.exists(file_path):
                os.remove(file_path)

        photo.delete()

        if not album.photos.exists():
            if os.path.exists(album_dir):
                try:
                    os.rmdir(album_dir)
                except OSError:
                    import shutil
                    shutil.rmtree(album_dir, ignore_errors=True)
            album.delete()

        return JsonResponse({'success': True, 'message': '照片已删除'})

    return JsonResponse({'success': False, 'error': '仅支持POST请求'})


def logout_view(request):
    from django.contrib.auth import logout as django_logout
    django_logout(request)
    return HttpResponseRedirect('/login/')

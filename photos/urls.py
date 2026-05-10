from django.urls import path
from . import views

app_name = 'photos'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('motto/', views.MottoView.as_view(), name='motto'),
    path('timeline/', views.TimelineView.as_view(), name='timeline'),
    path('album/<int:pk>/', views.AlbumDetailView.as_view(), name='album_detail'),
    path('photo/<int:pk>/', views.PhotoDetailView.as_view(), name='photo_detail'),
    path('api/photos/', views.api_photos, name='api_photos'),
    path('api/albums/', views.api_albums, name='api_albums'),
]

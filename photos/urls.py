from django.urls import path
from . import views

app_name = 'photos'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('timeline/', views.TimelineView.as_view(), name='timeline'),
    path('photo/<int:pk>/', views.PhotoDetailView.as_view(), name='photo_detail'),
    path('api/photos/', views.api_photos, name='api_photos'),
]

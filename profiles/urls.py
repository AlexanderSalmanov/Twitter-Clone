from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [

    path('profile/my/', views.CurrentProfile.as_view(), name='my'),
    path('profile/<slug:slug>/', views.ProfileDetail.as_view(), name='single'),
    path('interact/', views.interact, name='interact'),
    path('settings/', views.profile_settings, name='settings')
]

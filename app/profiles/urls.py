from django.urls import path

from . import views 

app_name = 'profiles'

urlpatterns = [
    path('my/', views.MyProfile.as_view(), name='my'),
    path('edit/', views.ChangeProfile.as_view(), name='edit'),
    path('followed/', views.FollowedSection.as_view(), name='followed'),
    path('search/', views.ProfileSearch.as_view(), name='search'),
    path('interact/<int:user_id>/', views.interact, name='interact'),
    path('<slug:slug>/', views.ProfileDetail.as_view(), name='single'),
]
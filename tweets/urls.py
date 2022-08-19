from django.urls import path
from . import views

app_name = 'tweets'

urlpatterns = [
    path('new/', views.AddTweet.as_view(), name='new'),
    path('<int:pk>/', views.TweetDetail.as_view(), name='single'),
    path('delete/<int:id>/', views.delete_tweet, name='delete'),
    path('like-unlike/<int:id>/', views.like_unlike, name='like-unlike'),
    path('feed/', views.Feed.as_view(), name='feed'),
    path('followed/', views.followed_section, name='followed'),
    path('pin/<int:id>/', views.pin_action, name='pin'),
    path('retweet/<int:id>/', views.retweet, name='retweet'),
    path('respondo-to/<int:id>/', views.respond, name='respond')
]

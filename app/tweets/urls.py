from django.urls import path

from . import views

app_name = 'tweets'

urlpatterns = [
    path('new/', views.AddTweet.as_view(), name='new'),
    path('reply/<int:tweet_id>/', views.add_reply, name='reply'),
    path('view/<int:tweet_id>/', views.tweet_detail, name='single'),
    path('view-branch/<int:tweet_id>/', views.tweet_branch_view, name='branch'),
    path('like/<int:tweet_id>/', views.like_unlike, name='like'),
    path('delete/<int:tweet_id>/', views.delete_tweet, name='delete'),
    path('retweet/<int:tweet_id>/', views.retweet, name='retweet')
]

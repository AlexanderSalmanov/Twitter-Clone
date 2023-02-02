from django.contrib import admin

from .models import Tweet, LikedTweet, Retweet
from profiles.models import Profile 
# Register your models here.

@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'created']
    list_filter = ['author', ]
    

@admin.register(LikedTweet)
class LikedTweetAdmin(admin.ModelAdmin):
    list_display = ['profile', 'tweet']
    
    
@admin.register(Retweet)
class RetweetAdmin(admin.ModelAdmin):
    list_display = ['profile', 'tweet']
    

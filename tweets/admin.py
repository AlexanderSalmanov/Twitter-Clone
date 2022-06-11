from django.contrib import admin

from .models import Tweet, LikedTweet, Retweet, Conversation
# Register your models here.

admin.site.register(Tweet)
admin.site.register(LikedTweet)

@admin.register(Retweet)
class RetweetAdmin(admin.ModelAdmin):
    list_display = ['profile', 'tweet']
    class Meta:
        model = Retweet

admin.site.register(Conversation)

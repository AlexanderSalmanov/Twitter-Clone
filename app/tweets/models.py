from django.db import models
from django.conf import settings
from django.urls import reverse

from profiles.models import Profile

# Create your models here.
User = settings.AUTH_USER_MODEL


class TweetQueryset(models.query.QuerySet):

    def time_order(self):
        return self.order_by('-created')
    
    def reverse_time_order(self):
        return self.order_by('created')
    
    def no_replies(self):
        return self.filter(is_reply=False)


class TweetManager(models.Manager):

    def get_queryset(self):
        return TweetQueryset(self.model, using=self._db)

    def time_order(self):
        """This ordering is chronological and is
            meant for feed and profile sections"""
        return self.get_queryset().time_order()
    
    def reverse_time_order(self):
        """This ordering is meant for single tweet sections where replies 
            are meant to be displayed from the first down to the most recent one."""
        return self.get_queryset().reverse_time_order()
    
    def no_replies(self):
        return self.get_queryset().no_replies()


class Tweet(models.Model):

    author = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        related_name="tweets")
    text = models.CharField(max_length=140)
    image = models.ImageField(blank=True, null=True, upload_to='tweets/attachments/')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_reply = models.BooleanField(default=False)
    branch_start = models.ForeignKey(
        "self", 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True, 
        related_name='branch_tweets')
    reply_to = models.ForeignKey(
        "self", 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True, 
        related_name='replies')

    objects = TweetManager()
    
    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f"author: {str(self.author)} tweet_id({self.id})"

    @property
    def like_count(self):
        return self.likes.all().count()

    @property 
    def retweet_count(self):
        return self.retweets.all().count()
    
    @property 
    def branch_length(self):
        return self.branch_tweets.all().count()
    
    @property 
    def reply_count(self):
        return self.replies.all().count()

    def get_absolute_url(self):
        return reverse("tweets:single", kwargs={'tweet_id': self.id})    
    
    def get_retweet_url(self):
        return reverse('tweets:retweet', kwargs={'tweet_id': self.id})
    

class LikedTweet(models.Model):
    profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        related_name="likes")
    tweet = models.ForeignKey(
        Tweet, 
        on_delete=models.CASCADE, 
        related_name="likes")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"user=({self.profile.nickname}); tweet=({self.tweet.id})"
    
    
class Retweet(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='retweets'
    )
    tweet = models.ForeignKey(
        Tweet,
        on_delete=models.CASCADE,
        related_name="retweets"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"user=({self.profile.nickname}); tweet=({self.tweet.id})"
        

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.db.models.signals import pre_save, pre_delete

# Create your models here.

from profiles.models import Profile
from accounts.models import User

import random
import string


class Conversation(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Conversation {self.id} created at {self.timestamp}'

    @property
    def conversation_tweets(self):
        return self.tweet_set.all()


    @property
    def responses(self):
        return self.tweet_set.filter(as_response=True)

    @property
    def responses_count(self):
        return self.tweet_set.filter(as_response=True).count()


class TweetQuerySet(models.query.QuerySet):
    def time_and_pin_order(self):
        return self.order_by('-rank', '-is_pinned', '-timestamp')

    def time_order(self):
        return self.order_by('-timestamp')

class TweetManager(models.Manager):
    def get_queryset(self):
        return TweetQuerySet(self.model, using=self._db)

    def time_and_pin_order(self):
        return self.get_queryset().time_and_pin_order()

    def time_order(self):
        return self.get_queryset().time_order()

class Tweet(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    text = models.CharField(max_length=140, default='')
    is_pinned = models.BooleanField(default=False)
    rank = models.PositiveIntegerField(default=1)
    as_response = models.BooleanField(default=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='tweets/attached_images/', blank=True, null=True)

    objects = TweetManager()

    def __str__(self):
        return f'Tweet №{self.pk} by {self.author.user.email}'

    def get_absolute_url(self):
        return reverse('tweets:single', kwargs={'pk': self.pk})

    @property
    def all_retweets(self):
        return self.retweet_set.all()

    @property
    def retweet_count(self):
        return self.retweet_set.all().count()

    # @property
    # def like_count(self):
    #     return LikedTweet.objects.filter(tweet=self).count()

    @property
    def like_count(self):
        return self.likedtweet_set.all().count()


class LikedTweet(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Tweet №{self.tweet.id} liked by {self.profile.nickname}'

    class Meta:
        ordering = ['-timestamp']


class Retweet(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'Tweet {self.tweet.id} by {self.tweet.author.nickname} retweeted by {self.profile.nickname}'


# def pre_save_tweet_manager(sender, instance, *args,  **kwargs):
#     # request = kwargs.get('request')
#     # profile_obj = Profile.objects.get(user=request.user)
#     # instance.author = profile_obj
#     # if request.FILES.get('image', None) is not None:
#     #     instance.image = request.FILES['image']
#     conv_obj = Conversation.objects.create()
#     print(f'KWARGS:{kwargs}')
#     print(f'ARGS: {args}')
#     instance.conversation = conv_obj
#
#
# pre_save.connect(pre_save_tweet_manager, sender=Tweet, dispatch_uid=random.choice(string.digits))





# def pre_delete_tweet_receiver(sender, instance, *args, **kwargs):
#     if instance.conversation and instance.conversation.responses_count <= 1:
#         conv_obj = instance.conversation
#
#         conv_obj.delete()

# pre_delete.connect(pre_delete_tweet_receiver, sender=Tweet)

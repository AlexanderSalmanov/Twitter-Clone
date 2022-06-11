import random
import string

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.db.models.signals import post_save
from django.utils.text import slugify

# Create your models here.

User = settings.AUTH_USER_MODEL


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=50, unique=True)
    profile_pic = models.ImageField(upload_to='profiles/profile_pics/')
    nickname = models.CharField(unique=True, max_length=150)
    slug = models.SlugField(allow_unicode=True, null=True)
    bio = models.CharField(max_length=200, blank=True, null=True)
    reading = models.ManyToManyField(User, related_name='reading', blank=True, null=True)
    followers = models.ManyToManyField(User, related_name='followers', blank=True, null=True)


    def __str__(self):
        return f'@{self.nickname}'

    def get_absolute_url(self):
        # return reverse
        return reverse('profiles:single', kwargs={'slug': self.slug})

    @property
    def all_tweets(self):
        return self.tweet_set.filter(as_response=False)

    @property
    def tweet_count(self):
        return self.tweet_set.all().count()

    @property
    def all_reading(self):
        return self.reading.all()

    @property
    def reading_count(self):
        return self.reading.all().count()

    @property
    def all_followers(self):
        return self.followers.all()

    @property
    def followers_count(self):
        return self.followers.all().count()

    # def save(self, *args, **kwargs):
    #     self.slug = slugify(self.nickname)
    #     super().save(*args, **kwargs)


def post_save_user_receiver(sender, instance, created, *args, **kwargs):
    if created:
        random_prefix = ''.join([random.choice(string.digits) for _ in range(5)])
        nick = ''
        if instance.email:
            profile_username = instance.email + random_prefix
        if instance.full_name:
            nick = instance.full_name + random_prefix

        Profile.objects.get_or_create(user=instance, nickname=nick, username=profile_username, slug=slugify(profile_username))


post_save.connect(post_save_user_receiver, sender=User)

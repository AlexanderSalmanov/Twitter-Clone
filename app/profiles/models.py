from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

User = settings.AUTH_USER_MODEL

from core import utils

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(blank=True, unique=True, allow_unicode=True)
    nickname = models.CharField(blank=True, null=True, max_length=50)
    profile_pic = models.ImageField(upload_to='profiles/profile_pics', blank=True, null=True)
    bio = models.TextField(default='No bio provided yet.')
    reading = models.ManyToManyField(
        "self",
        related_name='reading_whom',
        blank=True,
        symmetrical=False
    )
    followers = models.ManyToManyField(
        "self",
        related_name='followers_who',
        blank=True,
        symmetrical=False
    )

    def __str__(self):
        return f"@{self.nickname}" if self.nickname else self.username

    def get_absolute_url(self):
        return reverse("profiles:single", kwargs={'slug': self.slug})
    
    @property 
    def reading_count(self):
        return self.reading_whom.all().count()
    
    @property 
    def followers_count(self):
        return self.followers_who.all().count()


@receiver(post_save, sender=User)
def post_signup_profile_creator(sender, instance, created, *args, **kwargs):
    if created:
        nick = ''
        if instance.full_name:
            nick = instance.full_name + utils.random_suffix(3)

        if instance.email:
            username = instance.email.split('@')[0] + utils.random_suffix(8)

        Profile.objects.get_or_create(
            user=instance,
            username=username,
            slug=slugify(username),
            nickname=nick or None
        )

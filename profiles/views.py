from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.text import slugify
from django.core.files.storage import FileSystemStorage
from django.db.models.query import QuerySet

from .models import Profile
from .forms import BioForm, ProfileSettingsForm
from tweets.forms import TweetForm
from accounts.models import User
from tweets.models import Tweet, LikedTweet, Retweet

from itertools import chain
import string
import random
# Create your views here.

class ProfileDetail(generic.DetailView):
    """
    View showing given user's profile
    """
    template_name = 'profiles/single.html'
    model = Profile

    def get_context_data(self, *args, **kwargs):
        """
        1. Adding all needed forms to context.
        2. Extracting profile's tweets just this way in order to apply ordering options
        which allow us order objects based on their timestamp and on their is_pinned and rank fields.
        3. Extracting user's likes and adding them to the context.
        4. At the same time, we fetch all retweet objects and then we're taking
        out all tweet objects related to them. It's done in order to cast all
        differently typed objects to the same tweet type to apply all ordering
        options to them.

        """
        context = super().get_context_data(*args, **kwargs)
        request = self.request
        profile = context['profile']
        current_profile = Profile.objects.get(user=request.user)
        # tweet_pks = [i.pk for i in Tweet.objects.filter(author=profile)]
        tweet_pks = [i.pk for i in context['profile'].all_tweets]
        retweet_pks = [i.tweet.pk for i in Retweet.objects.filter(profile=profile)]
        tweet_pks.extend(retweet_pks)
        all_tweets_and_retweets = Tweet.objects.filter(id__in=tweet_pks).time_and_pin_order()
        context['profile_all_tweets'] = all_tweets_and_retweets
        retweets = Retweet.objects.filter(profile__id=context['profile'].id)
        retweets_tweets = [i.tweet for i in retweets]
        context['retweets'] = retweets_tweets
        likes = LikedTweet.objects.filter(profile=profile)
        context['likes'] = [i.tweet for i in likes]
        return context

class CurrentProfile(LoginRequiredMixin, generic.DetailView):
    """
    Special view for showing current user's profile.
    Designed to escape collisions between different profiles.
    """
    template_name = 'profiles/single.html'

    def get_object(self):

        request = self.request
        user_obj = request.user
        profile_obj = Profile.objects.get(user=user_obj)
        return profile_obj


    def get_context_data(self, *args, **kwargs):
        """
        1. Adding all needed forms to context.
        2. Extracting profile's tweets just this way in order to apply ordering options
        which allow us order objects based on their timestamp and on their is_pinned and rank fields.
        3. Extracting user's likes and adding them to the context.
        """
        context = super().get_context_data(*args, **kwargs)
        context['tweet_form'] = TweetForm(self.request.POST or None)
        # tweet_pks = [i.pk for i in Tweet.objects.filter(author=context['profile'])]
        tweet_pks = [i.pk for i in context['profile'].all_tweets]
        retweet_pks = [i.tweet.pk for i in Retweet.objects.filter(profile=context['profile'])]
        tweet_pks.extend(retweet_pks)
        all_tweets_and_retweets = Tweet.objects.filter(id__in=tweet_pks).time_and_pin_order()
        retweets = Retweet.objects.filter(profile__id=context['profile'].id)
        retweets_tweets = [i.tweet for i in retweets]
        context['retweets'] = retweets_tweets
        context['profile_all_tweets'] = all_tweets_and_retweets
        context['settings_form'] = ProfileSettingsForm()
        likes = LikedTweet.objects.filter(profile=Profile.objects.get(user=self.request.user))
        context['likes'] = [i.tweet for i in likes]

        return context

@login_required
def profile_settings(request):
    """
    View for editing some of the current user's profile parameters, such as
    nickname, personal bio, and profile picture.
    1. Instantiating the form and add there both request.POST and request.FILES data (the second one is for images and other file data).
    2. Getting both current user's and profile's objects
    3. If form.is_valid(), then fetching every single form field and modifying current profile objects based on the input data.
        3.1 JS functionality added directly is profiles/single.html. It allows 'username' and 'nickname' fields
        be automatically pre-filled with current nickname and username values.
    4. Making all form fields optional is extremely important!
    """
    settings_form = ProfileSettingsForm(request.POST, request.FILES)
    current_user = request.user
    current_profile_obj = Profile.objects.get(user=current_user)
    if settings_form.is_valid():

        random_prefix = ''.join([random.choice(string.digits) for _ in range(5)])
        if settings_form.cleaned_data.get('username') != '':
            current_profile_obj.username = settings_form.cleaned_data.get('username')
            current_profile_obj.slug = slugify(current_profile_obj.username) + random_prefix
        if settings_form.cleaned_data.get('nickname') != '':
            current_profile_obj.nickname = settings_form.cleaned_data.get('nickname')
        else:
            current_profile_obj.nickname = current_profile_obj.nickname
        if settings_form.cleaned_data.get('bio_input') != '':
            current_profile_obj.bio = settings_form.cleaned_data.get('bio_input')
        else:
            current_profile_obj.bio = current_profile_obj.bio
        if settings_form.cleaned_data.get('image') is not None:
            image = request.FILES['image']
            current_profile_obj.profile_pic = image
        current_profile_obj.save()

    return redirect('profiles:my')



@login_required
def interact(request):
    """
    View implementing follow-unfollow functionality.
    1. Fetching current and target users related to profiles.
        1.1 Target user's slug, which is a unique identifier for all users, is
        given in the interact_form snippet.
    2. Making a conditional check for if current user is present in target user's followers.
    3. If not, then adding him.
    4. In the opposite case, removing him.
    5. Collecting some data for AJAX requests, and moving it to a JSON dictionary.
    """
    current_user_obj = User.objects.get(email=request.user.email)
    current_profile_obj = get_object_or_404(Profile, user=current_user_obj)
    target_user_slug = request.POST.get('target_slug')
    target_profile_obj = get_object_or_404(Profile, slug=target_user_slug)
    target_user_obj = target_profile_obj.user
    if current_user_obj not in target_profile_obj.all_followers:
        followed = True
        target_profile_obj.followers.add(current_user_obj)
        current_profile_obj.reading.add(target_user_obj)
    else:
        followed = False
        target_profile_obj.followers.remove(current_user_obj)
        current_profile_obj.reading.remove(target_user_obj)
    if request.is_ajax:
        target_follower_count = target_profile_obj.followers_count
        json = {
            'followed': followed,
            'unfollowed': not followed,
            'follower_count': target_follower_count
        }
        return JsonResponse(json)
    return redirect('profiles:single', slug=target_user_slug)

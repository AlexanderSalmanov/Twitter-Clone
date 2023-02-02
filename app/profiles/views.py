from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.urls import reverse
from django.forms.models import model_to_dict
from django.http import JsonResponse

from tweets.forms import TweetForm

from .models import Profile
from .forms import ProfileSettingsForm

from tweets.models import Tweet

User = get_user_model()

# Create your views here.

class ProfileDetail(generic.DetailView):

    model = Profile
    lookup_field = 'slug'
    template_name = 'profiles/single.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        tweet_ids = [i.id for i in context['profile'].tweets.all()]
        tweet_ids.extend([i.tweet.id for i in context['profile'].retweets.all()]) # getting retweets too 
        context['profile_tweets'] = Tweet.objects.filter(
            id__in=tweet_ids,
            is_reply=False
        ).time_order()
        context['retweets'] = [i.tweet for i in context['profile'].retweets.all()]
        liked_tweet_ids = [i.tweet.id for i in context['profile'].likes.all()]
        context['liked_tweets'] = Tweet.objects.filter(id__in=liked_tweet_ids)
        return context 


class MyProfile(LoginRequiredMixin, generic.View):

    def get(self, *args, **kwargs):
        request = self.request
        context = {
            'profile': request.user.profile,
            'tweet_form': TweetForm(),
            'tweet_form_action': reverse('tweets:new'),
            'profile_settings_form': ProfileSettingsForm(),
            'profile_settings_action': reverse('profiles:edit'),
            'retweets': [i.tweet for i in request.user.profile.retweets.all()]
        }
        # context['profile_tweets'] = context['profile'].tweets.filter(is_reply=False)
        tweet_ids = [i.id for i in request.user.profile.tweets.all()]
        tweet_ids.extend([i.tweet.id for i in request.user.profile.retweets.all()])
        context['profile_tweets'] = Tweet.objects.filter(
            id__in=tweet_ids,
            is_reply=False,
        )
        liked_tweet_ids = [i.tweet.id for i in context['profile'].likes.all()]
        context['liked_tweets'] = Tweet.objects.filter(id__in=liked_tweet_ids)
        return render(request, 'profiles/single.html', context)


class ChangeProfile(LoginRequiredMixin, generic.View):

    def post(self, *args, **kwargs):
        request = self.request
        profile_obj = request.user.profile
        form = ProfileSettingsForm(request.POST or None, request.FILES or None)

        if form.is_valid():
            form_data = form.cleaned_data
            truthy_values = {key:value for key, value in form_data.items() if form_data[key]}
            if request.FILES.get('profile_pic', None) is not None:
                img = request.FILES['profile_pic']
                truthy_values['profile_pic'] = img

            if truthy_values:
                profile_obj.__dict__.update(**truthy_values)
            profile_obj.save()
            return redirect('profiles:my')
        messages.warning(request, "WRONG PROFILE FORM!")
        return redirect('profiles:my')
    
    
@login_required 
def interact(request, user_id):
    current_profile_obj = request.user.profile
    target_user_profile = get_object_or_404(Profile, id=user_id)
    if target_user_profile in current_profile_obj.reading_whom.all():
        current_profile_obj.reading_whom.remove(target_user_profile)
        target_user_profile.followers_who.remove(current_profile_obj)
        followed = False
    else:
        current_profile_obj.reading_whom.add(target_user_profile)
        target_user_profile.followers_who.add(current_profile_obj)
        followed = True
    current_profile_obj.save(); target_user_profile.save()
    if request.is_ajax:
        data = {
            'followed': followed,
            'unfollowed': not followed,
            'followers_count': target_user_profile.followers_count,
        }
        return JsonResponse(data)
        
    return redirect('profiles:my')


class FollowedSection(LoginRequiredMixin, generic.View):
    
    def get(self, *args, **kwargs):
        request = self.request
        followed_profiles = [profile for profile in request.user.profile.reading.all()]
        tweets = []
        for profile in followed_profiles:
            tweets.extend([tweet for tweet in profile.tweets.all().filter(is_reply=False)])
        context = {
            'tweets': tweets,
            'hero_unit_msg': 'Check only those authors which interest you the most.',
            'hero_unit_class': 'info'
        }
        return render(request, 'feed.html', context)
    
    
class ProfileSearch(generic.View):
    
    def get(self, *args, **kwargs):
        request = self.request 
        
        query = request.GET.get('search-q')
        context = {
            'query': query
        }
        profile_qs = Profile.objects.filter(
            nickname__icontains=query
        ).union(Profile.objects.filter(
            username__icontains=query
        ))
        
        context['profiles'] = profile_qs or None 
        return render(request, "profiles/search-list.html", context)
    

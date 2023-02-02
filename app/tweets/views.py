from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import JsonResponse

from .forms import TweetForm
from .models import Tweet, LikedTweet, Retweet

from profiles.models import Profile
# Create your views here.


class Feed(generic.ListView):
    model = Tweet
    template_name = "feed.html"
    context_object_name = "tweets"
    
    def get_queryset(self):
        return self.model.objects.filter(is_reply=False).time_order()[:20]
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['hero_unit_msg'] = 'Stay tuned with the latest saying from the ' \
                                    'best and the smartest authors.'
        context['hero_unit_class'] = 'primary'
        return context


class AddTweet(LoginRequiredMixin, generic.CreateView):

    def post(self, *args, **kwargs):
        request = self.request
        form = TweetForm(request.POST, request.FILES or None)
        if form.is_valid():
            tweet_obj = form.save(commit=False)
            tweet_obj.author = request.user.profile
            if request.FILES.get('image', None) is not None:
                tweet_obj.image = request.FILES['image']
            tweet_obj.save()
            messages.success(request, "Net tweet added!")
            return redirect('profiles:my')

        messages.warning(request, "Something's wrong...")
        return redirect('profiles:my')


@login_required(redirect_field_name="next")
def like_unlike(request, tweet_id):
    tweet_obj = get_object_or_404(Tweet, id=tweet_id)
    profile_obj = request.user.profile
    liked_tweet, created = LikedTweet.objects.get_or_create(
        profile=profile_obj,
        tweet=tweet_obj
    )
    if not created:
        liked_tweet.delete()

    if request.is_ajax:
        json = {
            'liked': created,
            'unliked': not created,
            'like_count': tweet_obj.like_count
        }
        return JsonResponse(json)
    
    
@login_required 
def retweet(request, tweet_id):
    tweet_obj = get_object_or_404(Tweet, id=tweet_id)
    retweet_obj, created = Retweet.objects.get_or_create(
        profile=request.user.profile,
        tweet=tweet_obj
    )
    if not created:
        retweet_obj.delete()
    if request.is_ajax:
        data = {
            'created': created,
            'deleted': not created,
            'retweet_count': tweet_obj.retweet_count
        }
        return JsonResponse(data)


@login_required
def delete_tweet(request, tweet_id):
    tweet_obj = get_object_or_404(Tweet, id=tweet_id)
    profile_obj = request.user.profile
    try:
        related_like = LikedTweet.objects.get(
            profile=profile_obj,
            tweet=tweet_obj
        )
    except LikedTweet.DoesNotExist:
        related_like = None 
    if related_like:
        related_like.delete()
    tweet_obj.delete()
    messages.success(request, "Tweet has been successfully deleted!")
    return redirect(request.META.get('HTTP_REFERER'))


def tweet_detail(request, tweet_id):
    tweet_obj = get_object_or_404(Tweet, id=tweet_id)
    tweet_replies = tweet_obj.replies.all().reverse_time_order()
        
    context = {
        'tweet': tweet_obj,
        'tweet_replies': tweet_replies
    }
    return render(request, 'tweets/single.html', context)


def tweet_branch_view(request, tweet_id):
    tweet_obj = get_object_or_404(Tweet, id=tweet_id)
    branch_starter = tweet_obj.branch_start
    branch_tweets = branch_starter.branch_tweets.all().reverse_time_order()
    
    context = {
        'tweet': branch_starter,
        'tweet_replies': branch_tweets
    }
    return render(request, 'tweets/single.html', context)


@login_required 
def add_reply(request, tweet_id):
    tweet_obj = get_object_or_404(Tweet, id=tweet_id)
    reply_text = request.POST.get('replyText')
    reply_image = None
    if request.FILES.get('replyImage', None) is not None:
        reply_image = request.FILES['replyImage']
        
    reply_tweet = Tweet.objects.create(
        author=request.user.profile,
        text=reply_text,
        image=reply_image or None,
        is_reply=True,
        reply_to=tweet_obj
    )
    reply_tweet.branch_start = tweet_obj if not tweet_obj.is_reply \
                                else tweet_obj.branch_start
    reply_tweet.save()
    messages.success(request, "A reply has been added!")
    return redirect(request.META.get('HTTP_REFERER'))




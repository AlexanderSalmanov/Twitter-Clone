from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.contrib import messages
from django.db.models.query import QuerySet
from django.utils import timezone

from profiles.models import Profile
from .models import Tweet, LikedTweet, Retweet, Conversation
from .forms import TweetForm

from copy import deepcopy



class Feed(generic.ListView):
    """
    View imitating twitter so-called feed behaviour
    """
    model = Tweet
    template_name = 'tweets/feed.html'

    def get_context_data(self, *args, **kwargs):
        """
        Extracting all tweets from all profiles and applying list operations
        to them. The approach differs from querysets. Here we use 'sorted'
        function to order items by an attribute.
        """
        context = super().get_context_data(*args, **kwargs)
        tweets = []
        for profile in Profile.objects.all():
            tweet_buffer = [i for i in profile.all_tweets]
            tweets.extend(tweet_buffer)
        # context['tweets'] = Tweet.objects.time_order()[:20]

        context['tweets'] = sorted(tweets, key=lambda x: x.timestamp, reverse=True)[:20]
        return context

class AddTweet(LoginRequiredMixin, generic.CreateView):
    """
    View for posting new tweets.
    Successfully realized option of adding thubmnails as the user wishes.
    """
    model = Tweet
    success_url = reverse_lazy('profiles:my')
    form_class = TweetForm

    def form_valid(self, form):
        """
        1. Retrieving request data and user object.
        2. Creating a tweet instance with commit=False to apply some ongoing changes.
        3. First, checking presence of image data in the form, and, if it is present, then connecting it to
        the tweet object.
        4. Next, we attach current profile object to tweet's author.
        """
        request = self.request
        user_obj = request.user
        tweet_obj = form.save(commit=False)
        if request.FILES.get('image', None) is not None:
            tweet_obj.image = request.FILES['image']
        profile_obj = Profile.objects.get(user=user_obj)
        tweet_obj.author = profile_obj
        tweet_obj.save()
        return super().form_valid(form)

class TweetDetail(generic.DetailView):
    """
    Tweet Detail CBV created to implement response functionality.
    Its key functionality is implemented in 'get_context_data' method.
    """

    model = Tweet
    template_name = 'tweets/single.html'

    def get_context_data(self, *args, **kwargs):
        """
        1. Making a conditional check for the presence of conversation on a
        given tweet, is it's absent - just pass and keep getting stuff which is
        not related to conversation.
        2. If the conversation exists, extracting conversation related to particular tweet.
        3. Retrieving all tweets associated to this conversation.
        4. Getting response_counter property value.
        """
        context = super().get_context_data(*args, **kwargs)
        conversation = context['tweet'].conversation
        if conversation:
            context['conversation'] = conversation
            context['conversation_tweets'] = conversation.conversation_tweets
            context['responses_count'] = conversation.responses_count
        else:
            pass
        context['tweet_form'] = TweetForm()

        # Explicitly added tweet_author and tweet_author_slug fields to context
        # to escape possible name conflict in tweet snippet.

        context['profile'] = context['tweet'].author
        context['tweet_id'] = context['tweet'].id
        context['tweet_author'] = context['tweet'].author.nickname
        context['tweet_author_slug'] = context['tweet'].author.slug
        return context


@login_required
def respond(request, id):
    """
    Response function-based view. The entire response functionality needs major
    revision.
    1. Getting the tweet instance and checking presence of the conversation.
    2. If it's not in there - then creating it.
    3. Getting current_profile object.
    4. Then, we're applying default tweet create operations but with some
    slight differences: we set as_response attribute to true to prevent the
    response from being displayed in the profile page because then things get
    too messy. Also, we relate the response object to original tweet's conversation.
    5. Finally, we're getting redirected to the original tweet's detail page.

    """
    tweet_obj = get_object_or_404(Tweet, id=id)
    if not tweet_obj.conversation:
        tweet_obj.conversation = Conversation.objects.create()
        tweet_obj.save()
    current_profile = Profile.objects.get(user=request.user)

    tweet_form = TweetForm(request.POST or None)
    if tweet_form.is_valid():
        obj = tweet_form.save(commit=False)
        obj.author = current_profile
        obj.conversation = tweet_obj.conversation
        obj.as_response = True
        if request.FILES.get('image') is not None:
            image = request.FILES['image']
            obj.image = image

        obj.save()

    return redirect('tweets:single', pk=id)



@login_required
def delete_tweet(request, id):
    """
    AJAX simple view for instantly deleting tweets.
    1. Getting user and profile objects.
    2. Getting the needed tweet object.
    3. Deleting the object.
    4. For AJAX request, we only pass the tweet_count variable.
    ---SOME EXTRAS ADDED JUST ON THE FLY BECAUSE THIS VIEW IS REALLY COMPLICATED---
    """
    user = request.user
    profile_obj = Profile.objects.get(user=user)
    tweet_obj = get_object_or_404(Tweet, id=id)
    ### CHECKING IF THE CURRENT TWEET OBJECT IS A RETWEET
    profile_retweets = Retweet.objects.filter(profile=profile_obj)
    profile_retweets_tweets = [i.tweet for i in profile_retweets]
    profile_retweets_ids = [i.tweet.id for i in profile_retweets]
    if tweet_obj.id in profile_retweets_ids:
        retweet_obj = Retweet.objects.get(tweet=tweet_obj, profile=profile_obj)
        # checking if this tweet is in users retweets
        # if this tweet is user's own retweet, then delete both this tweet and
        # retweet. In case if this tweet's author is not current user, then simply
        # delete its retweet object without affecting the original tweet object.
        tweet_in_retweets = any([tweet_obj == i for i in profile_retweets_tweets])
        is_own_tweet = any([tweet_obj.author.user == user for i in profile_retweets_tweets])
        if tweet_in_retweets:
            retweet_obj.delete()
            if is_own_tweet:
                tweet_obj.delete()
        else:
            retweet_obj.delete()
    else:
        # handling deletion for tweet that has responses to it
        if tweet_obj.conversation:
            conv_obj = tweet_obj.conversation

            # if it's just a response, that simply delete this response
            if tweet_obj.as_response:
                tweet_obj.delete()

            # if this tweet is a dialog starter, then delete it and all responses
            # linked to it
            else:
                for item in tweet_obj.conversation.responses:
                    item.delete()
                tweet_obj.delete()
                conv_obj.delete()
        # default case behaviour
        else:
            tweet_obj.delete()
    if request.is_ajax:
        json = {
            'tweet_count': profile_obj.tweet_count
        }
        return JsonResponse(json)


def like_unlike(request, id):
    """
    View imitating a wide-spread like functionality.
    Has some issues to be fixed in the future.
    """
    current_profile = Profile.objects.get(user=request.user)
    tweet_obj = Tweet.objects.get(id=id)
    new_tweet_obj = deepcopy(tweet_obj)
    new_tweet_obj.is_pinned = False
    print(new_tweet_obj.is_pinned)
    new_tweet_obj.rank = 1
    new_tweet_obj.as_response = False


    liked_tweet, created = LikedTweet.objects.get_or_create(profile=current_profile, tweet=new_tweet_obj)


    if not created:
        liked_tweet.delete()


    if request.is_ajax:
        like_count = tweet_obj.like_count
        print(f'NUM OF LIKES BEFORE REFRESHING: {like_count}')
        json = {
            'liked': created,
            'unliked': not created,
            'likes_count': like_count,
        }
        return JsonResponse(json)


@login_required
def pin_action(request, id):
    """
    Very simple view for pinning/unpinning tweets.
    Here we simply grab the tweet instance, and check if it's already pinned.
    If it isn't, we slighly modify some of its attributes and then model
    ordering described in tweet's models.py file, more exactly - in Tweet's model
    manager, does everyting for us.
    """
    tweet_obj = get_object_or_404(Tweet, id=id)
    if not tweet_obj.is_pinned:
        tweet_obj.is_pinned = True
        tweet_obj.rank = 2
        tweet_obj.save()
    else:
        tweet_obj.is_pinned = False
        tweet_obj.rank = 1
        tweet_obj.save()
    return redirect('profiles:my')


@login_required
def followed_section(request):
    """
    View displaying tweets from users being followed by the current user
    """
    current_profile_obj = get_object_or_404(Profile, user=request.user)
    followed_users = current_profile_obj.reading.all() # EXTRACTING USER OBJECTS

    followed_profiles = [Profile.objects.get(user__id=item.id) for item in followed_users] #FETCHING PROFILES RELATED TO USER OBJECTS

    tweets_list = []
    for profile in followed_profiles: # iterating though every single profile object to access a tweet_set object
        for tweet in profile.all_tweets: # not iterating through profile.all_tweets return a queryset and we need all separate tweets.
            tweets_list.append(tweet)
    tweets_pks = [i.pk for i in tweets_list]
    tweets = Tweet.objects.filter(pk__in=tweets_pks).time_order()

    return render(request, 'tweets/followed_section.html', {'tweets': tweets})


@login_required
def retweet(request, id):
    """
    Function-based view implementing retweet functionality.
    1. Fetching needed tweet instance.
    2. Deepcopying it to change it later and prevent the database calls.
    3. The changes are designed to return the tweet 'to defaults': it's not pinned,
    it's not a response, and it has an ordinary rank.
    4. Next, we're checking the retweet instance on the given tweet already exists
    with get_or_create method.
    5. If it doesn't exist, then create it.
    6. If it already exists, then we delete it.
    7. Passing some extra data for AJAX calls.
    """
    tweet_obj = Tweet.objects.get(id=id)
    new_tweet_obj = deepcopy(tweet_obj) # COPYING TWEET OBJ TO PREVENT ORIGINAL FROM BEING ALTERED
    new_tweet_obj.is_pinned = False
    new_tweet_obj.rank = 1
    new_tweet_obj.as_response = False
    current_profile_obj = Profile.objects.get(user=request.user)
    retweet, created = Retweet.objects.get_or_create(profile=current_profile_obj, tweet=new_tweet_obj)
    retweet.timestamp = timezone.now()
    print(new_tweet_obj.is_pinned)
    print(tweet_obj.is_pinned)
    if not created:
        retweet.delete()

    if request.is_ajax:
        json = {
            'created': created,
            'deleted': not created,
            'retweet_count': tweet_obj.retweet_count
        }
        return JsonResponse(json)

    return redirect('profiles:my')

from django.contrib.auth.decorators import login_required

from profiles.models import Profile
from tweets.models import LikedTweet, Tweet, Retweet


def current_user_and_likes(request):
    if not request.user.is_authenticated:
        return {}
    else:
        current_profile_obj = Profile.objects.get(user=request.user)
        liked_tweets = LikedTweet.objects.filter(profile=current_profile_obj)
        current_user_likes = [i.tweet for i in liked_tweets]
        my_retweets = Retweet.objects.filter(profile=current_profile_obj)
        my_retweets_tweets = [i.tweet for i in my_retweets]
        return {
            'current_user_likes': current_user_likes,
            'current_user': request.user,
            'current_profile': current_profile_obj,
            'my_retweets': my_retweets_tweets
        }

from profiles.models import Profile
from tweets.models import Tweet


def current_profile_and_likes(request):
    if not request.user.is_authenticated:
        return {}
    else:
        profile_obj = Profile.objects.get(user=request.user)
        profile_likes_ids = [i.tweet.id for i in profile_obj.likes.all()]
        profile_likes = Tweet.objects.filter(id__in=profile_likes_ids)
        profile_retweets = [i.tweet for i in profile_obj.retweets.all()]
        return {
            'current_profile': profile_obj,
            'current_profile_likes': profile_likes,
            'current_profile_retweets': profile_retweets
        }

# Generated by Django 3.2.12 on 2022-05-20 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0008_remove_tweet_liked'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='liked',
            field=models.ManyToManyField(blank=True, null=True, related_name='_tweets_tweet_liked_+', through='tweets.LikedTweet', to='tweets.Tweet'),
        ),
    ]

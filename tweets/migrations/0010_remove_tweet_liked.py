# Generated by Django 3.2.12 on 2022-05-20 11:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0009_tweet_liked'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tweet',
            name='liked',
        ),
    ]

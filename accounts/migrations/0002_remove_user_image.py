# Generated by Django 3.2.12 on 2022-05-17 13:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='image',
        ),
    ]

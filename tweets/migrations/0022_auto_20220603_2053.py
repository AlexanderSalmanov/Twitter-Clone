# Generated by Django 3.2.5 on 2022-06-03 17:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0021_auto_20220603_1939'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='tweet',
            name='conversation',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='tweets.conversation'),
            preserve_default=False,
        ),
    ]

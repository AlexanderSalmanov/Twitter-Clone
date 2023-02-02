from django.contrib import admin

from .models import Profile 
from accounts.models import User 
# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'user']

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# Create your models here.

class UserManager(BaseUserManager):
    
    def create_user(self, email, password=None, full_name=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email!")
        
        if not password:
            raise ValueError("Users must have a password!")
        
        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            **extra_fields 
        )
        user.set_password(password)
        user.save()
        return user 
    
    
    def create_superuser(self, email, password=None, full_name=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(
            email=email,
            password=password,
            full_name=full_name,
            **extra_fields
        )
        
        
class User(AbstractBaseUser, PermissionsMixin):
    email = models.CharField(max_length=64, unique=True, db_index=True)
    full_name = models.CharField(max_length=64, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    
    objects = UserManager()
    
    def __str__(self):
        return self.email 
    
    def get_full_name(self):
        return self.full_name if self.full_name else self.email 
    
    def get_short_name(self):
        if self.full_name:
            if ' ' in self.full_name:
                return self.full_name.split()[0]
            return self.full_name 
        return self.email 
    
    @property 
    def username(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser 
    
    def has_module_perms(self, app_label):
        return self.is_superuser

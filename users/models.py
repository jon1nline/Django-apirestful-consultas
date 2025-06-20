from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email deve ser fornecido')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractUser):
    username = None  
    nome_social = models.CharField(max_length=255)
    email = models.EmailField(unique=True)  
    
    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['nome_social', 'password']  
    
    objects = UserManager()

    def __str__(self):
        return self.email


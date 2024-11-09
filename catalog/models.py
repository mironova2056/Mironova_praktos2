from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.core.exceptions import ValidationError
# Create your models here.

class User(AbstractUser):
    first_name = models.CharField(max_length=254, verbose_name="Имя")
    patronymic = models.CharField(max_length=254,blank=True, verbose_name="Отчество")
    last_name = models.CharField(max_length=254, verbose_name="Фамилия")
    username = models.CharField(max_length=254, verbose_name="Логин", unique=True)
    email = models.EmailField(max_length=254, verbose_name="Почта", unique=True)
    password = models.CharField(max_length=254, verbose_name="Пароль")

    USERNAME_FIELD = 'username'

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}"


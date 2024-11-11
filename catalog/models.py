from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image



# Create your models here.

class User(AbstractUser):
    first_name = models.CharField(max_length=254, verbose_name="Имя")
    patronymic = models.CharField(max_length=254,blank=True, verbose_name="Отчество")
    last_name = models.CharField(max_length=254, verbose_name="Фамилия")
    username = models.CharField(max_length=254, verbose_name="Логин", unique=True)
    email = models.EmailField(max_length=254, verbose_name="Почта", unique=True)
    password = models.CharField(max_length=254, verbose_name="Пароль")
    failed_attempts = models.PositiveIntegerField(default=0, verbose_name="Неудачные попытки")
    is_blocked = models.BooleanField(default=False, verbose_name="Заблокирован")

    USERNAME_FIELD = 'username'

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}"

def validate_image(image):
    valid_mime_types = ['image/jpeg', 'image/png', 'image/bmp']
    mime_type = getattr(image.file, 'content_type', None)
    if mime_type:
        if mime_type not in valid_mime_types:
            raise ValidationError('Формат файла может быть: jpg, jpeg, png, bmp ', code='invalid_mime_type')
    else:
        raise ValidationError('Не удалось определить формат файла', code='unknown_mime_type')

    file_size = image.size
    if file_size > 2 * 1024 * 1024:
        raise ValidationError('Размер файла не должен превышать 2 Мб', code='file_too_large')
    try:
        img = Image.open(image)
        img.verify()
        width, height = img.size
        max_resolution = 2000
        if width > max_resolution  or height > max_resolution:
            raise ValidationError('Разрешение картинки не должно превышать 2000 рх по ширине или высоте',
                                  code='resolution_too_large')
    except Image.UnidentifiedImageError:
        raise ValidationError('Загруженный файл не поддерживается', code='invalid_image')
    except Exception as e:
        raise ValidationError(f"Ошибка при обработке картинки {e}", code='processing_errr')

class Category(models.Model):
    name = models.CharField(max_length=100, help_text='выберите категорию')
    def __str__(self):
        return self.name
class Application(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='Пользователь'
    )
    title = models.CharField(max_length=200, verbose_name='Напишите заголовок к заявке ')
    description = models.TextField(verbose_name='Напишите описание для заявки')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Выберите категорию заявки')
    image = models.FileField(
        upload_to='application',
        validators=[validate_image],
        verbose_name='Загрузите фото заявки'
    )
    LOAN_STATUS = (
        ('new', 'новая'),
        ('active','принято'),
        ('done','выполнено'),
    )
    status = models.CharField(max_length=20, choices=LOAN_STATUS,
                              default='n', verbose_name='статус заявки',
                              help_text='статус заявки')
    created_at = models.DateTimeField(auto_now_add=True, help_text='дата и время создания')
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('application-detail', args=[str(self.id)])
    def display_category(self):
        return self.category.name if self.category else 'Без категории'
    display_category.short_description = 'Category'

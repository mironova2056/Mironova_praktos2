from django.contrib import admin
from .models import Category, Application
from unicodedata import category
from django.core.exceptions import ValidationError
from django import forms
from django.db import transaction

class ApplicationAdminForm(forms.ModelForm):
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows':3}),
        label='комментарий (обязателен, при смене статуса на "приято") '
    )
    design_image = forms.ImageField(
        required=False,
        label='изображение дизайна (обязательно при смене статуса на  "выполнено")'
    )
    class Meta:
        model = Application
        fields = '__all__'
        exclude = ['image']

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        previous_status = self.instance.status if self.instance else None

        if previous_status in ['ative', 'done'] and status != previous_status:
            raise ValidationError("Нельзя менять статус после 'приянто' или 'выполнено' ")
        if status == 'active' and not cleaned_data.get('comment'):
            raise ValidationError('Пожалуйста, добавьте комментарий')
        if status == 'done' and not cleaned_data.get('design_image'):
            raise ValidationError('Пожалуйста, загрузите изображение')
        return cleaned_data


admin.site.register(Category)


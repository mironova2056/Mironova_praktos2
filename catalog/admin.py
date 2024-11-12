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
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    form = ApplicationAdminForm
    list_display = ('title', 'user', 'status', 'created_at', 'category')
    readonly_fields = ('user', 'title', 'description', 'category', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'user__username', 'description')
    exclude = ['image']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            status = obj.status

            if status == 'active':
                if 'design_image' in form.base_fields:
                    form.base_fields['design_image'].required = False
                    del form.base_fields['design_image']
            if status == 'done':
                if 'comment' in form.base_fields:
                    form.base_fields['comment'].required = False
                    del form.base_fields['comment']
        return form
    def save_model(self, request, obj, form, change):
        if form.is_valid():
            obj.comment = form.cleaned_data.get('comment', '')
            obj.design_image = form.cleaned_data.get('design_image', None)
            with transaction.atomic():
                obj.save()

admin.site.register(Category)


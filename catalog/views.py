from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from .forms import RegisterForm
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from .models import User

def check_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username=username).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'Логин уже занят.'
    return JsonResponse(data)

def index(request):
    return render(request, 'catalog/index.html')

class Register(generic.CreateView):
    template_name = 'authentication/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('catalog:login')


def logout_user(request):
    logout(request)
    return redirect('catalog:index')

MAX_FAILED_ATTEMPTS = 5

class CustomLoginView(LoginView):
    template_name = 'authentication/login.html'
    def form_valid(self, form):
        user = form.get_user()
        if user.is_blocked:
            messages.error(self.request, 'Ваш аккаунт заблокирован из-за множества неудачных попыток входа.')
            return redirect('catalog:login')
        user.failed_attempts = 0
        user.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        username = form.data.get('username')
        try:
            user = User.objects.get(username=username)
            if not user.is_blocked:
                user.failed_attempts += 1
                if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
                    user.is_blocked = True
                    messages.error(self.request, 'Ваш аккаунт был заблокирован после 5 неудачных попыток входа.')

                user.save()
        except User.DoesNotExist:
            pass
        messages.error(self.request, 'Неправильный логин или пароль.')
        return super().form_invalid(form)
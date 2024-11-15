from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from .forms import RegisterForm, ApplicationForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from .models import User, Application, ApplicationHistory
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


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
class Profile(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = 'catalog/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return self.request.user
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            applications = Application.objects.filter(user = self.request.user, status = status_filter).order_by('-created_at')
        else:
            applications = Application.objects.filter(user = self.request.user).order_by('-created_at')

        context['applications'] = applications
        context['status_filter'] = status_filter
        return context


def create_application(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            return redirect('catalog:profile')
    else:
        form = ApplicationForm()

    return render(request, 'catalog/create_application.html', {'form': form})
def application_detail(request, pk):
    application = get_object_or_404(Application, pk=pk)
    return render(request, 'catalog/application_detail.html', {'application': application})
@login_required
def delete_application(request, pk):
    application = get_object_or_404(Application, pk=pk)
    if application.user == request.user:
        if application.status == 'new':
            application.delete()
            messages.success(request, 'Заявка успешно удалена')
        else:
            messages.error(request, 'Вы можете удалять заявки только со статусом "новая" ')
    else:
        messages.error(request, 'вы не можете удалять заявки, не принадлежащие вам')
    return redirect('catalog:profile')
def application_history(request, pk):
    application = get_object_or_404(Application, pk=pk)
    history = application.history.all()
    return render(request, 'catalog/application_history.html', {'application': application, 'history': history})
def update_application(request, pk):
    application = get_object_or_404(Application, pk=pk)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            form.save()
            ApplicationHistory.objects.create(
                application=application,
                changed_by=request.user,
                change_description=f"Заявка обновлена: {form.cleaned_data['title']}"
            )
            return redirect('catalog:application_detail', pk=application.pk)
    else:
        form = ApplicationForm(instance=application)
    return render(request, 'catalog/application_form.html', {'form': form})


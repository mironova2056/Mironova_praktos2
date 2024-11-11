from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'catalog'

urlpatterns = [
    path('', views.index, name='index'),
    path('check-username/', views.check_username, name='check_username'),
    path('register', views.Register.as_view(), name='register'),
    path('login', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('new/', views.create_application, name='create_application'),
    path('<int:pk>/', views.application_detail, name='application_detail'),
    path('application/<int:pk>/delete', views.delete_application, name='delete_application'),
    path('application/<int:pk>/edit/', views.update_application, name='edit_application'),
    path('application/<int:pk>/history/', views.application_history, name='application_history'),
]

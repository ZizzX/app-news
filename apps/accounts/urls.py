from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.ProfileView.as_view(), name='user-list'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('delete/', views.UserDeleteView.as_view(), name='delete'),
    path('deactivate/', views.UserDeactivateView.as_view(), name='deactivate'),
]
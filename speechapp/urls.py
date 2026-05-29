from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('correct/',views.correct_text, name='correct'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),
    path('chatbot/', views.chatbot, name='chatbot'),
]
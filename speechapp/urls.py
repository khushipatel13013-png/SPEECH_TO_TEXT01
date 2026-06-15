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
    path('history/', views.history_page, name='history'),
    path('delete-history/<int:id>/', views.delete_history, name='delete_history'),
    path('chat-history/',views.chat_history_page,name='chat_history'),
    path('delete-chat/<int:id>/',views.delete_chat,name='delete_chat'),
    path('upload-pdf/', views.upload_pdf, name='upload_pdf'),
    
]
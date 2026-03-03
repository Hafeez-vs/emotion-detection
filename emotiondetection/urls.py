"""
URL configuration for emotiondetection project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from emotionapp import views

urlpatterns = [

    path('admin/', admin.site.urls),
    path('', views.home_redirect, name='home'),
    path('register/', views.student_register, name='student_register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/',views.logout_view, name='logout'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher_room/<int:classroom_id>/', views.teacher_room, name='teacher_room'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('join/<int:class_id>/', views.join_class, name='join_class'),
    path('student_room/<int:classroom_id>/', views.student_room, name='student_room'),
    path('detect_emotion/',views.detect_emotion,name="detect_emotion"),
    path('kick_student/', views.kick_student, name='kick_student'),

]

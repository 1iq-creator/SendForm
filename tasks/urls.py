from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', views.login_view, name='login'),
    path('create_task/', login_required(views.create_task), name='create_task'),
    path('view_tasks/', views.view_tasks, name='view_tasks'),
    path('moderator_view/', views.moderator_view, name='moderator_view'),
    path('task_history/', views.task_history, name='task_history'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('check-email/', views.check_email, name='check_email'),
]
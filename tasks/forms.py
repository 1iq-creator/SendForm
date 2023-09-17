from django import forms
from .models import Task

class LoginForm(forms.Form):
    username = forms.CharField(label='Имя пользователя', max_length=100)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['task_type', 'description', 'file', 'importance', 'region']

class StatusComment(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['status', 'comments']

from django.db import models
from django.contrib.auth.models import User  # Если вы хотите связать задачу с пользователем
from simple_history.models import HistoricalRecords


class Task(models.Model):
    TASK_TYPES = (
        ('Тип1', 'Общее'),
        ('Тип2', 'Не зачислен платеж'),
        ('Тип3', 'Запрос закрывающих документов'),
    )

    task_type = models.CharField(max_length=10, choices=TASK_TYPES, verbose_name='Тип задачи*', default='Тип1')
    description = models.TextField(verbose_name='Описание')
    file = models.FileField(verbose_name='Файл', upload_to='uploads/', null=True, blank=True)
    IMPORTANCE_CHOICES = (
        ('низкая', 'Низкая'),
        ('средняя', 'Средняя'),
        ('высокая', 'Высокая'),
    )
    importance = models.CharField(max_length=50, choices=IMPORTANCE_CHOICES, verbose_name='Важность', default='низкая')
    REGION_CHOICES = (
        ('регион1', 'Республика Адыгея'),
        ('регион2', 'Республика Алтай'),
        ('регион3', 'Алтайский край'),
        ('регион4', 'Амурская область'),
        ('регион5', 'Архангельская область'),
        ('регион6', 'Астраханская область'),
    )
    region = models.CharField(max_length=100, choices=REGION_CHOICES, verbose_name='Регион*', default='регион1')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', verbose_name='Пользователь')

    STATUS_CHOICES = (
        ('в ожидании', 'В ожидании'),
        ('в процессе', 'В процессе'),
        ('завершено', 'Завершено'),
    )
    comments = models.TextField(verbose_name='Комментарий', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='в ожидании')

    history = HistoricalRecords()

    def __str__(self):
        return self.description



# Generated by Django 4.2.5 on 2023-09-15 11:42

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_task_task_number_alter_task_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='task_number',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]

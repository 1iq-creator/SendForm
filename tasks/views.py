from django.contrib.auth import authenticate, login
from django.db.models import Count, Q
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from email.header import decode_header
from SendForm.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
from .forms import LoginForm, StatusComment
from django.contrib.auth.decorators import login_required
from .forms import TaskForm
from .models import Task
import imaplib
import email

def send_email(subject, message):
    from_email = settings.EMAIL_HOST_USER
    recipient_list = ['masyakasteam@gmail.com']
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

@login_required
def create_task(request):
    user = request.user
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            form = TaskForm()
            subject = 'Новая задача создана'
            message = f'Новая задача с номером {task.id} создана.'
            send_email(subject, message)
            return redirect('create_task')
    else:
        form = TaskForm()

    return render(request, 'create_task.html', {'form': form, 'user': user})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('create_task/')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def view_tasks(request):
    user = request.user
    tasks = Task.objects.filter(user=user)
    return render(request, 'view_tasks.html', {'tasks': tasks})

@login_required
def moderator_view(request):
    tasks = Task.objects.all()

    if request.method == 'POST':
        form = StatusComment(request.POST)

        if form.is_valid():
            task_id = request.POST.get('task_id')
            new_status = request.POST.get('status')
            comment_text = request.POST.get('comments')

            task = Task.objects.get(pk=task_id)

            task.status = new_status
            task.comments = comment_text
            task.save()

            if new_status == 'завершено':
                subject = 'Задача завершена'
                message = f'Задача {task.id} завершена: {comment_text}'
                send_email(subject, message)

            return redirect('moderator_view')

    else:
        form = StatusComment()

    return render(request, 'moderator_view.html', {'tasks': tasks, 'form': form, })



def task_history(request):
    tasks = Task.objects.all()
    history_entries = []
    user = request.user
    if request.method == 'POST':
        task_id_to_delete = request.POST.get('task_to_delete')
        try:
            task_to_delete = Task.objects.get(pk=task_id_to_delete)
            task_to_delete.delete()
            return redirect('task_history')
        except Task.DoesNotExist:
            pass

    for task in tasks:
        task_history = task.history.all()
        for entry in task_history:
            status_change = entry.history_object.status
            comment_change = entry.history_object.comments

            if entry.prev_record:
                prev_status = entry.prev_record.history_object.status
                prev_comment = entry.prev_record.history_object.comments
            else:
                prev_status = ""
                prev_comment = ""

            # Добавить данные в список истории
            history_entries.append({
                'task_id': task.id,
                'timestamp': entry.history_date,
                'prev_status': prev_status,
                'status_change': status_change,
                'prev_comment': prev_comment,
                'comment_change': comment_change,
            })

    return render(request, 'task_history.html', {'history_entries': history_entries, 'tasks': tasks, 'user': user})

def generate_report(request):
    if request.method == 'POST':
        report_type = request.POST.get('report_type')

        if report_type == 'completed_tasks':
            completed_tasks = Task.objects.filter(status='завершено')
            report_text = "Отчет по выполненным задачам:\n\n"
            for task in completed_tasks:
                report_text += f"Задача: {task.id}\n"
                report_text += f"Тип задачи: {task.task_type}\n"
                report_text += f"Описание: {task.description}\n"
                report_text += f"Важность: {task.importance}\n"
                report_text += f"Регион: {task.region}\n"
                report_text += f"Пользователь: {task.user.username}\n"
                report_text += f"Статус: {task.status}\n"
                report_text += "\n"

            subject = 'Отчет по выполненным задачам'
            message = report_text
            send_email(subject, message)

        elif report_type == 'pending_tasks':
            completed_tasks = Task.objects.filter(Q(status='в ожидании') | Q(status='в процессе'))
            report_text = "Отчет по выполненным задачам:\n\n"
            for task in completed_tasks:
                report_text += f"Задача: {task.id}\n"
                report_text += f"Тип задачи: {task.task_type}\n"
                report_text += f"Описание: {task.description}\n"
                report_text += f"Важность: {task.importance}\n"
                report_text += f"Регион: {task.region}\n"
                report_text += f"Пользователь: {task.user.username}\n"
                report_text += f"Статус: {task.status}\n"
                report_text += "\n"

            subject = 'Отчет по выполненным задачам'
            message = report_text
            send_email(subject, message)

        elif report_type == 'task_completion_percentage':
            all_tasks = Task.objects.all()
            completed_tasks = all_tasks.filter(status='завершено').count()
            total_tasks = all_tasks.count()
            if total_tasks > 0:
                completion_percentage = (completed_tasks / total_tasks) * 100
            else:
                completion_percentage = 0

            report_text = f"Доска отчетности: % выполнения задач\n\n"
            report_text += f"Процент выполнения: {completion_percentage:.2f}%\n"

            subject = 'Доска отчетности: % выполнения задач'
            message = report_text
            send_email(subject, message)

        elif report_type == 'user_task_completion_percentage':
            user_task_counts = Task.objects.values('user__username').annotate(task_count=Count('id'))

            report_text = "Доска отчетности: Кол-во задач каждого пользователя\n\n"
            for user_task_count in user_task_counts:
                report_text += f"Пользователь: {user_task_count['user__username']}\n"
                report_text += f"Количество задач: {user_task_count['task_count']}\n"
                report_text += "\n"

            subject = 'Доска отчетности: Кол-во задач каждого пользователя'
            message = report_text
            send_email(subject, message)

    return render(request, 'report_generation.html')


def check_email(request):
    if request.method == 'POST':
        mail_server = 'imap.gmail.com'
        email_address = EMAIL_HOST_USER
        email_password = EMAIL_HOST_PASSWORD

        mail = imaplib.IMAP4_SSL(mail_server)
        mail.login(email_address, email_password)
        mail.select('inbox')
        status, email_ids = mail.search(None, 'UNSEEN')

        new_tasks = []

        for email_id in email_ids[0].split():
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])

            subject = msg['Subject']
            decoded_subject, encoding = decode_header(subject)[0]
            subject = decoded_subject.decode(encoding)
            if subject == 'Новая задача':
                if msg.get_content_maintype() == 'multipart':
                    for part in msg.walk():
                        if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                            continue
                        filename = part.get_filename()
                    else:
                        filename = None
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            email_body = part.get_payload(decode=True).decode(encoding)
                            break
                else:
                    email_body = msg.get_payload(decode=True).decode(encoding)
                data_lines = email_body.split('\n')

                task_type = ''
                description = ''
                importance = ''
                region = ''

                for line in data_lines:
                    parts = line.split(':')
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        if key == 'Тип задачи':
                            task_type = value
                        elif key == 'Описание':
                            description = value
                        elif key == 'Важность':
                            importance = value
                        elif key == 'Регион':
                            region = value

                task = Task(
                    task_type=task_type,
                    description=description,
                    file=filename,
                    importance=importance,
                    region=region,
                    user=request.user,
                )
                task.save()
                new_tasks.append(task)
                subject = 'Новая задача создана'
                message = f'Новая задача с номером {task.id} создана.'
                send_email(subject, message)

        mail.logout()

        context = {'new_tasks': new_tasks}
        return render(request, 'check_email.html', context)

    return render(request, 'check_email.html')
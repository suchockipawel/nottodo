from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import NotToDo, SharedNotToDo, Comment
from .forms import NotToDoForm, ShareNotToDoForm, CommentForm, CustomChangeEmailForm
from django.urls import reverse
from django.utils.http import urlencode
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
import pytz

@login_required
def add_nottodo(request):
    if request.method == 'POST':
        form = NotToDoForm(request.POST)
        if form.is_valid():
            nottodo = form.save(commit=False)
            nottodo.user = request.user
            nottodo.save()

            '''email'''

            messages.success(request, 'Your NotToDo has been added and a reminder email will be sent to your registered email address.')
            return redirect('list_nottodos')
        else:
            print("Form errors:", form.errors)
    else:
        form = NotToDoForm()
    return render(request, 'add_nottodo.html', {'form': form})

@login_required
def list_nottodos(request):
    context_filter = request.GET.get('context', 'All')
    if context_filter == 'All':
        nottodos = NotToDo.objects.filter(user=request.user).order_by('scheduled_start_time')
    else:
        nottodos = NotToDo.objects.filter(user=request.user, context=context_filter).order_by('scheduled_start_time')
    return render(request, 'list_nottodos.html', {'nottodos': nottodos, 'context_filter': context_filter})

@login_required
def update_nottodo(request, pk):
    nottodo = get_object_or_404(NotToDo, pk=pk, user=request.user)
    if request.method == 'POST':
        form = NotToDoForm(request.POST, instance=nottodo)
        if form.is_valid():
            form.save()
            return redirect('list_nottodos')
    else:
        form = NotToDoForm(instance=nottodo)
    return render(request, 'update_nottodo.html', {'form': form})

@login_required
def delete_nottodo(request, pk):
    nottodo = get_object_or_404(NotToDo, pk=pk, user=request.user)
    if request.method == 'POST':
        nottodo.delete()
        return redirect('list_nottodos')
    return render(request, 'delete_nottodo.html', {'nottodo': nottodo})

@login_required
def share_nottodo(request, pk):
    nottodo = get_object_or_404(NotToDo, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ShareNotToDoForm(request.POST)
        if form.is_valid():
            shared_nottodo = form.save(commit=False)
            shared_nottodo.nottodo = nottodo
            shared_nottodo.save()
            return redirect('list_nottodos')
    else:
        form = ShareNotToDoForm()
    
    share_url = request.build_absolute_uri(reverse('view_nottodo', args=[nottodo.pk]))
    share_text = f"Check out this Not To Do: {nottodo.title}"
    share_email_subject = "Check out this Not To Do"
    share_email_body = f"{share_text}\n\n{share_url}"

    context = {
        'form': form,
        'nottodo': nottodo,
        'share_url': share_url,
        'share_text': share_text,
        'share_email_subject': share_email_subject,
        'share_email_body': share_email_body,
    }
    return render(request, 'share_nottodo.html', context)

@login_required
def list_shared_nottodos(request):
    shared_nottodos = SharedNotToDo.objects.filter(shared_with=request.user).prefetch_related('comments')
    return render(request, 'list_shared_nottodos.html', {'shared_nottodos': shared_nottodos})

@login_required
def add_comment(request, shared_nottodo_id):
    shared_nottodo = get_object_or_404(SharedNotToDo, pk=shared_nottodo_id, shared_with=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.shared_nottodo = shared_nottodo
            comment.user = request.user
            comment.save()
            return redirect('list_shared_nottodos')
        else:
            print("Form errors:", form.errors)
    else:
        form = CommentForm()
    return render(request, 'add_comment.html', {'form': form, 'shared_nottodo': shared_nottodo})

def home(request):
    return render(request, 'home.html')

@login_required
def change_email(request):
    if request.method == 'POST':
        form = CustomChangeEmailForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('account_email')
    else:
        form = CustomChangeEmailForm(user=request.user)
    return render(request, 'account/change_email.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('account_login')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'account/change_password.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def view_nottodo(request, pk):
    nottodo = get_object_or_404(NotToDo, pk=pk, user=request.user)
    return render(request, 'view_nottodo.html', {'nottodo': nottodo})

@login_required
def copy_nottodo(request, pk):
    try:
        original_nottodo = NotToDo.objects.get(pk=pk, user=request.user)
    except NotToDo.DoesNotExist:
        try:
            shared_nottodo = SharedNotToDo.objects.get(nottodo__pk=pk, shared_with=request.user)
            original_nottodo = shared_nottodo.nottodo
        except SharedNotToDo.DoesNotExist:
            return render(request, 'error.html', {'message': 'The Not To Do item you are trying to copy does not exist.'})
    copied_nottodo = NotToDo.objects.create(
        user=request.user,
        title=f"Copy of {original_nottodo.title}",
        description=original_nottodo.description,
        context=original_nottodo.context,
        scheduled_start_time=original_nottodo.scheduled_start_time,
        scheduled_end_time=original_nottodo.scheduled_end_time,
        repeat=original_nottodo.repeat,
    )
    return redirect('list_nottodos')

@login_required
def unshare_nottodo(request, pk):
    shared_nottodo = get_object_or_404(SharedNotToDo, pk=pk, shared_with=request.user)
    shared_nottodo.delete()
    return redirect('list_shared_nottodos')

@login_required
def nottodo_events(request):
    user_timezone = pytz.timezone('Europe/Brussels')  # THis was changed 
    nottodos = NotToDo.objects.filter(user=request.user)
    events = []

    for nottodo in nottodos:
        start = nottodo.scheduled_start_time.astimezone(user_timezone)
        end = nottodo.scheduled_end_time.astimezone(user_timezone) if nottodo.scheduled_end_time else None

        if nottodo.repeat == 'Daily':
            current_start = start
            while current_start <= end:
                events.append({
                    'title': nottodo.title,
                    'start': current_start.isoformat(),
                    'end': (current_start + timedelta(hours=1)).isoformat(),
                    'description': nottodo.description,
                    'id': nottodo.id,
                    'context': nottodo.context,
                })
                current_start += timedelta(days=1)
        elif nottodo.repeat == 'Weekly':
            current_start = start
            while current_start <= end:
                events.append({
                    'title': nottodo.title,
                    'start': current_start.isoformat(),
                    'end': (current_start + timedelta(hours=1)).isoformat(),
                    'description': nottodo.description,
                    'id': nottodo.id,
                    'context': nottodo.context,
                })
                current_start += timedelta(weeks=1)
        elif nottodo.repeat == 'Monthly':
            current_start = start
            while current_start <= end + relativedelta(years=1): 
                events.append({
                    'title': nottodo.title,
                    'start': current_start.isoformat(),
                    'end': (current_start + timedelta(hours=1)).isoformat(),
                    'description': nottodo.description,
                    'id': nottodo.id,
                    'context': nottodo.context,
                })
                current_start += relativedelta(months=1)
        else:
            events.append({
                'title': nottodo.title,
                'start': start.isoformat(),
                'end': end.isoformat() if end else None,
                'description': nottodo.description,
                'id': nottodo.id,
                'context': nottodo.context,
            })

    return JsonResponse(events, safe=False)



@login_required
def check_reminders(request):
    now = timezone.now()
    has_reminders = NotToDo.objects.filter(user=request.user, scheduled_start_time__gt=now).exists()
    return JsonResponse({'has_reminders': has_reminders})
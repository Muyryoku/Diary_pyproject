import datetime
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .forms import TaskForm
from .models import Note
from .models import Task
from .serializers import NoteSerializer, UserSerializer, ProfileSerializer
from django.contrib.auth.decorators import login_required
from .models import Task

@login_required
def tasks_view(request):
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/tasks.html', {
        'tasks': tasks
    })



@login_required
def home_view(request):
    tasks = Task.objects.filter(user=request.user)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(completed=True).count()
    progress = (completed_tasks / total_tasks * 100) if total_tasks else 0

    temperature, weather_description = get_weather()
    weather_info = f"{temperature}°C, {weather_description}" if temperature else f"Ошибка: {weather_description}"

    user_notes = Note.objects.filter(user=request.user)
    form = TaskForm()

    context = {
        'now': datetime.datetime.now(),
        'completed_tasks': completed_tasks,
        'total_tasks': total_tasks,
        'progress_percent': progress,
        'weather_info': weather_info,
        'form': form,
        'tasks': tasks,
        'user_notes': user_notes,
    }
    return render(request, 'main/home.html', context)


from django.shortcuts import render, redirect
from .forms import NoteForm

def create_note_view(request):
    next_param = request.GET.get('next', '')  # ⬅ переместили сюда

    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
    else:
        form = NoteForm()

    return render(request, 'main/create_note.html', {
        'form': form,
        'next': next_param,
    })

# === Создание задачи ===
@login_required
def create_task_view(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('home')
    else:
        form = TaskForm()
    return render(request, 'main/create_task.html', {'form': form})

@login_required
def notes_view(request):
    user_notes = Note.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/notes.html', {
        'user_notes': user_notes
    })

# === Страница "О проекте" ===
def about_view(request):
    return render(request, 'main/about.html')

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from .forms import RegisterForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # 🔁 уже вошел — возвращаем

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)  # 🔐 автоматический вход
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'main/register.html', {'form': form})


# === Профиль пользователя ===
@login_required
def profile_view(request):
    return render(request, 'main/profile.html', {'user': request.user})

# === Вспомогательная функция погоды ===
def get_weather():
    api_key = settings.OPENWEATHER_API_KEY
    city = 'Almaty'
    url = f"https://api.openweathermap.org/data/2.5/weather?q=almaty&appid=4888ee202e791818ba39b78993ad14af&units=metric&lang=ru"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            temperature = data['main']['temp']
            weather_description = data['weather'][0]['description']
            return temperature, weather_description
        else:
            return None, "Ошибка получения данных о погоде"
    except requests.exceptions.RequestException as e:
        return None, f"Ошибка: {str(e)}"

# === API (DRF) ===
class LoginView(TokenObtainPairView):
    permission_classes = [IsAuthenticated]

class RegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]


@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.completed = not task.completed
    task.save()
    return redirect('home')

@login_required
def edit_task_view(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TaskForm(instance=task)
    return render(request, 'main/edit_task.html', {'form': form})


@login_required
def delete_task_view(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('home')
    return render(request, 'main/delete_task.html', {'task': task})

@login_required
def edit_note_view(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = NoteForm(instance=note)
    return render(request, 'main/edit_note.html', {'form': form})


@login_required
def delete_note_view(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    if request.method == 'POST':
        note.delete()
        return redirect('home')
    return render(request, 'main/delete_note.html', {'note': note})

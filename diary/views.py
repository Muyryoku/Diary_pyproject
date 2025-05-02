from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Task, Note
from .forms import TaskForm, NoteForm
from .serializers import NoteSerializer, UserSerializer, ProfileSerializer
from django.conf import settings
import datetime
import requests

@login_required
def home_view(request):
    tasks = Task.objects.filter(user=request.user)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(completed=True).count()
    progress = (completed_tasks / total_tasks * 100) if total_tasks else 0

    temperature, weather_description = get_weather()
    weather_info = f"{temperature}°C, {weather_description}" if temperature else f"Ошибка: {weather_description}"

    if request.method == 'POST':
        if 'mark_completed' in request.POST:
            task_id = request.POST.get('task_id')
            task = get_object_or_404(Task, id=task_id, user=request.user)
            task.is_completed = not task.is_completed
            task.save()
            return redirect('home')

    user_notes = Note.objects.filter(user=request.user)
    form = TaskForm()

    context = {
        'now': datetime.datetime.now(),
        'completed_tasks': completed_tasks,
        'total_tasks': total_tasks,
        'progress': progress,
        'weather_info': weather_info,
        'form': form,
        'tasks': tasks,
        'user_notes': user_notes,
    }
    return render(request, 'main/home.html', context)

# === Создание заметки ===
@login_required
def create_note_view(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            return redirect('home')
    else:
        form = NoteForm()
    return render(request, 'main/create_note.html', {'form': form})

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

# === Отдельная страница заметок ===
@login_required
def notes_view(request):
    notes = Note.objects.filter(user=request.user)
    return render(request, 'main/notes.html', {'notes': notes})

# === Страница "О проекте" ===
def about_view(request):
    return render(request, 'main/about.html')

# === Регистрация через форму ===
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'main/register.html', {'form': form})

# === Профиль пользователя ===
@login_required
def profile_view(request):
    return render(request, 'main/profile.html', {'user': request.user})

# === Вспомогательная функция погоды ===
def get_weather():
    api_key = settings.OPENWEATHER_API_KEY
    city = 'Almaty'
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
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


def update_task_status():
    return None
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView
from diary.views import (
    home_view,
    about_view,
    notes_view,
    profile_view,
    register_view,
    create_note_view,
    create_task_view,
    update_task_status,
    NoteViewSet, edit_task_view, delete_task_view, edit_note_view, delete_note_view, tasks_view
)

schema_view = get_schema_view(
    openapi.Info(
        title="Diary API",
        default_version='v1',
        description="Документация API проекта Diary",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

router = DefaultRouter()
router.register(r'notes', NoteViewSet)

urlpatterns = [
    path('', home_view, name='home'),
    path('about/', about_view, name='about'),
    path('notes/', notes_view, name='notes'),
    path('tasks/', tasks_view, name='tasks'),
    path('profile/', profile_view, name='profile'),
    path('register/', register_view, name='register'),
    path('create-note/', create_note_view, name='create_note'),
    path('create-task/', create_task_view, name='create_task'),
    path('update-task-status/<int:task_id>/', update_task_status, name='update_task_status'),
    path('edit-task/<int:task_id>/', edit_task_view, name='edit_task'),
    path('delete-task/<int:task_id>/', delete_task_view, name='delete_task'),
    path('edit-note/<int:note_id>/', edit_note_view, name='edit_note'),
    path('delete-note/<int:note_id>/', delete_note_view, name='delete_note'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('api/jwt-login/', TokenObtainPairView.as_view(), name='jwt-login'),
    path('api/', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
]

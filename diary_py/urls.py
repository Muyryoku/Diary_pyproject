from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from diary.views import NoteViewSet

router = DefaultRouter()
router.register(r'notes', NoteViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

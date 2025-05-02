from django import forms
from .models import Task, Note

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title']

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content']

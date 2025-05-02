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

from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@gmail.com'):
            raise forms.ValidationError("Регистрация разрешена только с Gmail-адресом.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get("password")
        pw2 = cleaned_data.get("confirm_password")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Пароли не совпадают.")

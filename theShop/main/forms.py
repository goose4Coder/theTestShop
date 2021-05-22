from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from captcha.fields import CaptchaField


class CustomUserForm(UserCreationForm):
    username=forms.CharField(max_length=30,label="Username",widget=forms.TextInput())
    first_name=forms.CharField(max_length=30,label="First name",widget=forms.TextInput())
    last_name=forms.CharField(max_length=30,label="Last name",widget=forms.TextInput())
    password1=forms.CharField(max_length=30,label="Password",widget=forms.PasswordInput())
    password2=forms.CharField(max_length=30,label="Confirm password",widget=forms.PasswordInput())
    email=forms.EmailField(max_length=65,label="email",widget=forms.EmailInput())
    captcha=CaptchaField()

    class Meta:
        model = User
        fields = ('username', 'first_name' , 'last_name', 'password1','password2','email')
class CustomLoginForm(AuthenticationForm):
    username=forms.CharField(max_length=30,label="Username",widget=forms.TextInput())
    password=forms.CharField(max_length=30,label="password",widget=forms.PasswordInput())
    captcha=CaptchaField()
    class Meta:
        model = User
        fields = ('username', 'password')

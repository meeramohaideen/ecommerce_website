from django import forms
from django.contrib.auth.models import  User
# from .models import UserRegister



class UserLoginForm(forms.ModelForm):

    #modifying password input - enhancing
    password = forms.CharField(widget=forms.PasswordInput())
    #creating meta class, to know which model this class belogs to
    class Meta:
        model=User
        fields=('username','email','password')


# class UserRegisterForm(forms.ModelForm):

#     class Meta:
#         model=UserRegister
#         fields=('date_of_birth','mobile_number')

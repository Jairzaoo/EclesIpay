from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Paroquia

class RegistroForm(UserCreationForm):
    nome = forms.CharField(max_length=150)
    data_nascimento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    telefone = forms.CharField(max_length=20)
    paroquia = forms.ModelChoiceField(queryset=Paroquia.objects.all())

    class Meta:
        model = Usuario
        fields = ('email', 'nome', 'data_nascimento', 'telefone', 'paroquia', 'password1', 'password2')
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Paroquia

class RegistroForm(UserCreationForm):
    nome = forms.CharField(max_length=150)
    data_nascimento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    telefone = forms.CharField(max_length=20)
    cpf = forms.CharField(max_length=11)
    paroquia = forms.ModelChoiceField(queryset=Paroquia.objects.all())

    class Meta:
        model = Usuario
        fields = ('email', 'nome', 'data_nascimento', 'telefone', 'cpf', 'paroquia', 'password1', 'password2')

class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'telefone', 'data_nascimento', 'cpf']

class ParoquiaForm(forms.ModelForm):
    class Meta:
        model = Paroquia
        fields = ['nome']  # Include all fields you want to edit
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'})
        }
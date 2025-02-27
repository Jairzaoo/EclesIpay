# dizimo/views.py
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegistroForm
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.tokens import default_token_generator
from .models import Paroquia
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                user.send_confirmation_email(request)
                return redirect('email_confirmation_sent')
            except Exception as e:
                messages.error(request, f"Erro ao enviar e-mail de confirmação: {str(e)}")
        else:
            messages.error(request, "Por favor corrija os erros abaixo")
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})

@login_required
def home(request):
    paroquias = Paroquia.objects.all()
    return render(request, 'home.html', {'paroquias': paroquias})



def confirmar_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.email_confirmado = True
        user.save()
        login(request, user)
        return redirect('email_confirmed')
    else:
        return HttpResponse('Link de confirmação inválido ou expirado!')

@csrf_exempt
@require_POST
def atualizar_paroquia(request):
    if request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            paroquia_id = data.get('paroquia_id')
            
            if not paroquia_id:
                return JsonResponse({'status': 'error', 'message': 'ID da paróquia não fornecido'})
            
            paroquia = Paroquia.objects.get(id=paroquia_id)
            request.user.paroquia = paroquia
            request.user.save()
            
            return JsonResponse({
                'status': 'success',
                'paroquia_nome': paroquia.nome
            })
            
        except Paroquia.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Paróquia não encontrada'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Usuário não autenticado'})
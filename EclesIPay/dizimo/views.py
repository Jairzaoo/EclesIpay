# dizimo/views.py
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import RegistroForm, EditarPerfilForm, ParoquiaForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.tokens import default_token_generator
from .models import Paroquia
from django.urls import reverse
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.views import LoginView
from django.views import View
from .abacatepay_service import AbacatePayService
import requests
from collections import defaultdict
from datetime import datetime, date
from django.db.models import  Sum, Count,Q
from collections import defaultdict
from decouple import config


User = get_user_model()

class CustomRegistroView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        form = RegistroForm()
        return render(request, 'registro.html', {'form': form})

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:  # Fixed this line
            return redirect('home')
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

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@csrf_exempt
@require_POST
@login_required
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

@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('home')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = EditarPerfilForm(instance=request.user)
    return render(request, 'editar_perfil.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

@login_required
def fazer_oferta(request):
    if request.method == 'POST':
        value = request.POST.get('value')
        payer_name = request.user.nome
        payer_cpf = request.user.cpf
        payer_email = request.user.email
        payer_telefone = request.user.telefone
        paroquia = request.user.paroquia

        
        abacatepay_service = AbacatePayService(api_key=config('ABACATEPAY_API_KEY'))
        payment_response = abacatepay_service.create_payment(
            amount=int(float(value) * 100),
            payer_name=payer_name,
            payer_cpf=payer_cpf,
            payer_email=payer_email,
            payer_telefone=payer_telefone,
            paroquia_nome=paroquia.nome,
            paroquia_id=paroquia.id
        )
        print(payment_response)
        if payment_response.get('error') is None and payment_response.get('data'):
            payment_url = payment_response['data']['url']
            return redirect(payment_url)
        else:
            error_message = payment_response.get('error') or 'Erro desconhecido na API'
            messages.error(request, f'Erro ao gerar cobrança: {error_message}')

    return render(request, 'fazer_oferta.html')

@login_required
def pagamento_efetuado(request):
    messages.success(request, 'Pagamento realizado com sucesso!')
    return redirect('fazer_oferta')

@login_required
def historico_contribuicao(request):
    try:
        url = "https://api.abacatepay.com/v1/billing/list"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {config('ABACATEPAY_API_KEY')}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        contributions = response.json().get('data', [])
        user_email = request.user.email

        paid_contributions = []
        total_amount = 0
        parishes = defaultdict(lambda: {'total': 0, 'count': 0})

        for contribution in contributions:
            customer_data = contribution.get('customer', {}).get('metadata', {})

            if customer_data.get('email') == user_email and contribution.get('status') == 'PAID':
                amount = contribution.get('amount', 0) / 100
                created_at = datetime.strptime(
                    contribution['createdAt'],
                    '%Y-%m-%dT%H:%M:%S.%fZ'
                )
                parish_id = contribution.get('products', [{}])[0].get('externalId')
                parish = Paroquia.objects.filter(id=parish_id).first()
                parish_name = parish.nome if parish else 'Não informada'

                paid_contributions.append({
                    'date': created_at,
                    'amount': amount,
                    'parish': parish_name,
                    'methods': ', '.join(contribution.get('methods', [])),
                    'payment_url': contribution.get('url', ''),
                    'id': contribution.get('id', '')
                })

                total_amount += amount
                parishes[parish_name]['total'] += amount
                parishes[parish_name]['count'] += 1

        # Group by month and parish
        grouped_contributions = defaultdict(lambda: defaultdict(list))
        for contrib in paid_contributions:
            month_key = contrib['date'].strftime('%Y-%m')
            grouped_contributions[month_key][contrib['parish']].append(contrib)

        # Debug prints
        print("Grouped Contributions:", grouped_contributions)
        print("Total Contributions:", len(paid_contributions))
        print("Total Amount:", total_amount)
        print("Parishes:", parishes)

        return render(request, 'historico_contribuicao.html', {
            'grouped_contributions': dict(grouped_contributions),
            'total_contributions': len(paid_contributions),
            'total_amount': total_amount,
            'parishes': dict(parishes)
        })

    except requests.exceptions.RequestException as e:
        messages.error(request, f'Erro ao conectar com o serviço de pagamentos: {str(e)}')
    except Exception as e:
        messages.error(request, f'Erro inesperado: {str(e)}')

    return redirect('home')

@user_passes_test(lambda u: u.is_superuser)
def add_paroquia(request):
    if request.method == 'POST':
        form = ParoquiaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('paroquia-list')
    else:
        form = ParoquiaForm()

    return render(request, 'admin/add_paroquia.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def admin_contribuicoes(request):
    try:
        url = "https://api.abacatepay.com/v1/billing/list"
        headers = {"accept": "application/json", "authorization": f"Bearer {config('ABACATEPAY_API_KEY')}"}
        params = {}

        
        selected_paroquia_name = request.GET.get('paroquia')
        parish_filter = None

        if selected_paroquia_name:
            parish_filter = Paroquia.objects.filter(nome=selected_paroquia_name).first()
            if parish_filter:
                params['products[0].externalId'] = parish_filter.id

        
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

       
        print(f"Date filter - start_date: {start_date}, end_date: {end_date}")

        
        if start_date:
            
            params['createdAt.gte'] = start_date

            print(f"Using start date parameter: {params['createdAt.gte']}")

        if end_date:
            # Approach 3: Date only for end date too
            params['createdAt.lte'] = end_date
            print(f"Using end date parameter: {params['createdAt.lte']}")

        # 3. AMOUNT FILTER
        amount_filter = request.GET.get('amount')
        print(f"Amount filter: {amount_filter}")

        if amount_filter:
            
            if amount_filter == '<50':
                params['amount.lte'] = 5000  # Convert to cents (API might expect cents)
                print(f"Setting API amount filter: amount.lte={params['amount.lte']}")
            elif amount_filter == '50-200':
                params['amount.gte'] = 5000  # Convert to cents
                params['amount.lte'] = 20000  # Convert to cents
                print(f"Setting API amount filter: amount.gte={params['amount.gte']}, amount.lte={params['amount.lte']}")
            elif amount_filter == '>200':
                params['amount.gte'] = 20000  # Convert to cents
                print(f"Setting API amount filter: amount.gte={params['amount.gte']}")

        
        print(f"API request parameters: {params}")
        print(f"API URL: {url}")
        print(f"API Headers: {headers}")

        # API Call
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        # Get response data
        api_response = response.json()
        contributions = api_response.get('data', [])

        # Debug print to show API response
        print(f"API response status: {response.status_code}")
        print(f"Number of contributions returned: {len(contributions)}")

        # Print the first contribution to see its structure
        if contributions:
            print(f"First contribution date: {contributions[0].get('createdAt')}")
            print(f"Sample contribution: {contributions[0]}")
        else:
            print("No contributions returned")

        # 4. AGE GROUP FILTER
        age_group = request.GET.get('age_group')
        if age_group:
            user_emails = {c.get('customer', {}).get('metadata', {}).get('email') for c in contributions}
            users = User.objects.filter(email__in=user_emails).only('email', 'data_nascimento')
            email_to_birthdate = {user.email: user.data_nascimento for user in users}

            age_filtered_contributions = []
            today = date.today()

            for contrib in contributions:
                email = contrib.get('customer', {}).get('metadata', {}).get('email')
                birthdate = email_to_birthdate.get(email)
                if not birthdate:
                    continue

                age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

                if ((age_group == '<20' and age < 20) or
                    (age_group == '20-40' and 20 <= age <= 40) or
                    (age_group == '40-60' and 40 < age <= 60) or
                    (age_group == '>60' and age > 60)):
                    age_filtered_contributions.append(contrib)

            print(f"Age filtering: {len(contributions)} -> {len(age_filtered_contributions)}")
            contributions = age_filtered_contributions

        # Manual date filtering in case API filtering doesn't work
        if start_date or end_date:
            print("Applying manual date filtering...")
            filtered_contributions = []
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

            for contrib in contributions:
                created_at_str = contrib.get('createdAt')
                if not created_at_str:
                    continue

                try:
                    # Parse the API date format
                    created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M:%S.%fZ')

                    # Apply date filters
                    if start_date_obj and created_at < start_date_obj:
                        continue
                    if end_date_obj and created_at > end_date_obj.replace(hour=23, minute=59, second=59):
                        continue

                    filtered_contributions.append(contrib)
                except ValueError as e:
                    print(f"Error parsing date {created_at_str}: {e}")

            print(f"Manual date filtering: {len(contributions)} -> {len(filtered_contributions)}")
            contributions = filtered_contributions

        # Manual amount filtering in case API filtering doesn't work
        if amount_filter:
            print("Applying manual amount filtering...")
            filtered_contributions = []

            for contrib in contributions:
                amount_cents = contrib.get('amount', 0)  # Amount in cents
                amount_reais = amount_cents / 100  # Convert to Reais

                # Apply amount filters
                if amount_filter == '<50' and amount_reais <= 50:
                    filtered_contributions.append(contrib)
                elif amount_filter == '50-200' and 50 <= amount_reais <= 200:
                    filtered_contributions.append(contrib)
                elif amount_filter == '>200' and amount_reais > 200:
                    filtered_contributions.append(contrib)
                elif not amount_filter:  # No filter, include all
                    filtered_contributions.append(contrib)

            print(f"Manual amount filtering: {len(contributions)} -> {len(filtered_contributions)}")
            contributions = filtered_contributions

        # Process contributions
        totals_by_paroquia = defaultdict(lambda: {'total': 0, 'count': 0})
        for contrib in contributions:
            if contrib.get('status') == 'PAID':
                parish_id = contrib.get('products', [{}])[0].get('externalId')
                parish = Paroquia.objects.filter(id=parish_id).first()

                amount = contrib.get('amount', 0) / 100  # Convert to Reais

                # If parish filter is active
                if parish_filter:
                    if parish and parish.id == parish_filter.id:
                        parish_name = parish.nome
                        totals_by_paroquia[parish_name]['total'] += amount
                        totals_by_paroquia[parish_name]['count'] += 1
                else:
                    parish_name = parish.nome if parish else 'Não informada'
                    totals_by_paroquia[parish_name]['total'] += amount
                    totals_by_paroquia[parish_name]['count'] += 1

        overall_count = sum(data['count'] for data in totals_by_paroquia.values())

        return render(request, 'admin_contribuicoes.html', {
            'totals_by_paroquia': dict(totals_by_paroquia),
            'overall_count': overall_count,
            'all_paroquias': Paroquia.objects.values_list('nome', flat=True).distinct(),
            'selected_paroquia': selected_paroquia_name,
            'age_group': age_group,
            'amount': amount_filter,
            'start_date': start_date,
            'end_date': end_date
        })

    except requests.exceptions.RequestException as e:
        messages.error(request, f'Erro na API: {str(e)}')
    except Exception as e:
        messages.error(request, f'Erro inesperado: {str(e)}')

    return redirect('home')

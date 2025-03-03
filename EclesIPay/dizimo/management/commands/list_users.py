from django.core.management.base import BaseCommand
from dizimo.models import Usuario

class Command(BaseCommand):
    help = 'List all users in the database'

    def handle(self, *args, **kwargs):
        users = Usuario.objects.all()
        for user in users:
            self.stdout.write(f'ID: {user.id}')
            self.stdout.write(f'Nome: {user.nome}')
            self.stdout.write(f'Email: {user.email}')
            self.stdout.write(f'Data de Nascimento: {user.data_nascimento}')
            self.stdout.write(f'Telefone: {user.telefone}')
            self.stdout.write(f'CPF: {user.cpf}')
            self.stdout.write(f'Paróquia: {user.paroquia.nome if user.paroquia else "Nenhuma"}')
            self.stdout.write(f'Email Confirmado: {user.email_confirmado}')
            self.stdout.write(f'Data de Cadastro: {user.data_cadastro}')
            self.stdout.write(f'Ativo: {user.is_active}')
            self.stdout.write(f'Staff: {user.is_staff}')
            self.stdout.write(f'Superuser: {user.is_superuser}')
            self.stdout.write('---')

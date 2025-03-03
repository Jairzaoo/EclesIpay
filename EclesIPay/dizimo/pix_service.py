import requests
import json

class PixService:
    def __init__(self, client_id, client_secret, certificate_path, sandbox=True):
        self.client_id = client_id
        self.client_secret = client_secret
        self.certificate_path = certificate_path
        self.sandbox = sandbox
        self.base_url = 'https://api.bcb.gov.br/pix' if not sandbox else 'https://api-pix-h.bcb.gov.br'
        self.token = self.get_access_token()

    def get_access_token(self):
        url = f'{self.base_url}/oauth/token'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            'grant_type': 'client_credentials',
        }
        response = requests.post(url, headers=headers, auth=(self.client_id, self.client_secret), data=data, cert=self.certificate_path)
        response_data = response.json()
        return response_data['access_token']

    def create_pix_charge(self, txid, value, payer_name, payer_cpf, payer_email):
        url = f'{self.base_url}/v2/cob/{txid}'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        data = {
            'calendario': {
                'expiracao': 3600
            },
            'devedor': {
                'cpf': payer_cpf,
                'nome': payer_name
            },
            'valor': {
                'original': f'{value:.2f}'
            },
            'chave': 'YOUR_PIX_KEY',
            'solicitacaoPagador': 'Contribuição para a igreja',
            'infoAdicionais': [
                {
                    'nome': 'Email',
                    'valor': payer_email
                }
            ]
        }
        response = requests.put(url, headers=headers, data=json.dumps(data), cert=self.certificate_path)
        return response.json()

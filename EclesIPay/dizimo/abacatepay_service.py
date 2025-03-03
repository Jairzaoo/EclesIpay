import requests
import json

class AbacatePayService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.abacatepay.com/v1'

    def create_payment(self, amount, payer_name, payer_cpf, payer_email, payer_telefone, paroquia_nome, paroquia_id):
        url = f'{self.base_url}/billing/create'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        data = {
            "frequency": "ONE_TIME",
            "methods": ["PIX"],
            "products": [
                {
                    "name": paroquia_nome,
                    "description": paroquia_nome,
                    "quantity": 1,
                    "price": amount,
                    "externalId": paroquia_id
                }
            ],
            "returnUrl": "http://eclesipay.run.place/fazer-oferta/",
            "completionUrl": "http://eclesipay.run.place/pagamentoefetuado/",
            #"webhook": "webh_dev_B6ArZrLxKMSfdgcDenHcKJ05",
            "customer": {
                "name": payer_name,
                "cellphone": payer_telefone,
                "email": payer_email,
                "taxId": payer_cpf
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return response.json()

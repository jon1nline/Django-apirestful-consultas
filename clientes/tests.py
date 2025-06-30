from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone
from datetime import  datetime, timedelta
from .models import PagamentoConsultas, CadastroClientes
from consultas.models import AgendamentosConsultas
from profissionais.models import Profissionais

import json

User = get_user_model()

class CadastroClientesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.base_url = '/clients/cadastro/'
        self.valid_payload = {
            "nome_social": "cliente teste",
            "cpf": "11122233344",
            "email": "user@teste.com",
            "contato": "11222223333",
            "logradouro": "rua teste",
            "numero": "33",
            "complemento": "casa 2",
            "bairro": "saude",
            "cep": "1122333"
        }

        # 1. Cria o usuário de teste
        self.user = User.objects.create_user( 
            email='test@example.com',
            password='testpass123',
            nome_social='Usuário Teste'
        )
        
        token = AccessToken.for_user(self.user)
        token['id'] = self.user.id  #adiciona o id pra criar o token
        
        self.client.cookies['access_token'] = str(token)

    def test_listar_clientes_sem_autenticacao(self):
        self.client.cookies['access_token'] = None 
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_listar_clientes_autenticado(self):

        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_criar_cliente_sem_autenticacao(self):
        self.client.cookies['access_token'] = None 
        response = self.client.post(self.base_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_criar_cliente_autenticado(self):
        response = self.client.post(self.base_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_criar_cliente_cpf_invalidos(self):
        invalid_payload = {
            "nome_social": "cliente teste",
            "cpf": "", #CPF Vazio
            "email": "user@teste.com",
            "contato": "11222223333",
            "logradouro": "rua teste",
            "numero": "33",
            "complemento": "casa 2",
            "bairro": "saude",
            "cep": "1122333"
        }
        response = self.client.post(self.base_url, invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cpf', response.data)  

    def test_criar_cliente_email_invalidos(self):
        invalid_payload = {
            "nome_social": "cliente teste",
            "cpf": "11122233344",
            "email": "",
            "contato": "11222223333",
            "logradouro": "rua teste",
            "numero": "33",
            "complemento": "casa 2",
            "bairro": "saude",
            "cep": "1122333"
        }
        response = self.client.post(self.base_url, invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)      


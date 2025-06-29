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

class GerenciarPagamentoTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            'status_pagamento': 'pago'
        }
        self.invalid_payload = {
            'status_pagamento': 'invalido'
        }

        self.user = User.objects.create_user( 
            email='test@example.com',
            password='testpass123',
            nome_social='Usuário Teste'
        )    
        token = AccessToken.for_user(self.user)
        token['id'] = self.user.id  #adiciona o id pra criar o token
        self.client.cookies['access_token'] = str(token)

        #cria o cliente para testes
        self.cliente = CadastroClientes.objects.create(
            nome_social = 'cliente primario',
            cpf = '12345678900',
            email = 'email@cliente.com',
            contato = '11222223333',
            logradouro = 'alameda dos clientes',
            numero = '11',
            complemento = 'apartamento 02',
            bairro = 'saude',
            cep = '11222333',
        )
        
        #cria o profissional para realizar os testes
        self.profissional = Profissionais.objects.create(
            nome_social="Dr. Teste",
            profissao="Médico",
            endereco="alameda dos testes",
            contato="99888887777",
            ativo=True
        )

        #cria a consulta.
        self.consulta = AgendamentosConsultas.objects.create(
            profissional=  self.profissional,
            data_consulta = timezone.now() + timedelta(days=1),
            cliente = self.cliente,
            status_consulta= 'agendada',
        )
        self.pagamento = PagamentoConsultas.objects.create(
            consulta=self.consulta,
            cliente = self.cliente,
            metodo_de_pagamento = 'pix',
            preco_consulta = '80.00',
            status_pagamento='pendente' 
        )

        self.base_url = f'/clients/consultas/{self.pagamento.id}/'

    def test_patch_pagamento_nao_autenticado(self):
        self.client.cookies['access_token'] = None
        response = self.client.patch(self.base_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_pagamento_authenticated(self):
        response = self.client.patch(self.base_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status_pagamento'], 'pago')

    def test_patch_pagamento_dados_invalidos(self):
        response = self.client.patch(self.base_url, self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_pagamento_nao_encontrado(self):
        self.client.force_authenticate(user=self.user)
        invalid_url = f'{self.base_url}999/'
        response = self.client.patch(invalid_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)    
   
    def test_patch_pagamento_pago_updates_consulta(self):
        self.assertEqual(self.consulta.status_consulta, 'agendada') 
        response = self.client.patch(self.base_url, self.valid_payload, format='json')
        
        self.consulta.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.consulta.status_consulta, 'confirmada')
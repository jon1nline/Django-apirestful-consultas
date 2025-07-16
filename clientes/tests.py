from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone
from .models import PagamentoConsultas, CadastroClientes
from consultas.models import AgendamentosConsultas
from profissionais.models import Profissionais
from unittest.mock import patch, MagicMock
import json

import json

User = get_user_model()

class CadastroClientesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.base_url = '/clients/cadastro/'
        self.valid_payload = {
            "nome_social": "cliente teste",
            "cpf": "13678982000",
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

    @patch('clientes.views.requests.post')
    def test_cria_cliente_e_registra_no_asaas_com_sucesso(self, mock_requests_post):
        """
        Testa o "caminho feliz": o cliente é criado localmente e o ID do Asaas
        é salvo corretamente após o registro bem-sucedido na plataforma externa.
        """
        # 1. Configuração do Mock para simular SUCESSO na API do Asaas
        asaas_id_esperado = "cus_000000000001"
        mock_response = MagicMock()
        mock_response.status_code = 200 # Sucesso
        mock_response.json.return_value = {"id": asaas_id_esperado, "object": "customer"}
        mock_requests_post.return_value = mock_response

        # 2. Faz a requisição POST para a sua API
        response = self.client.post(self.base_url, self.valid_payload, format='json')

        # 3. Verifica se a criação local foi bem-sucedida (HTTP 201 CREATED)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CadastroClientes.objects.count(), 1)

        # 4. VERIFICAÇÃO CRUCIAL: Garante que o ID do Asaas foi salvo
        cliente_criado = CadastroClientes.objects.get()
        self.assertEqual(cliente_criado.nome_social, self.valid_payload['nome_social'])
        self.assertEqual(cliente_criado.asaas_customer_id, asaas_id_esperado)
        
        # 5. Verifica se a chamada mockada ao Asaas foi realmente feita
        mock_requests_post.assert_called_once()
        print("\n[SUCESSO] Teste 'test_cria_cliente_e_registra_no_asaas_com_sucesso' passou.")

    @patch('clientes.views.requests.post')
    def test_cria_cliente_localmente_mesmo_com_falha_no_asaas(self, mock_requests_post):
        """
        Testa o cenário de falha: o cliente é criado localmente com sucesso,
        mesmo quando a comunicação com a API do Asaas retorna um erro.
        """
        # 1. Configuração do Mock para simular FALHA na API do Asaas
        mock_response = MagicMock()
        mock_response.status_code = 400 # Bad Request
        mock_response.text = '{"errors": [{"description": "CPF inválido"}]}'
        mock_response.json.return_value = {"errors": [{"description": "CPF inválido"}]}
        mock_requests_post.return_value = mock_response

        # 2. Faz a requisição POST para a sua API
        response = self.client.post(self.base_url, self.valid_payload, format='json')

        # 3. VERIFICAÇÃO CRUCIAL: A criação local DEVE ter sucesso (HTTP 201)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CadastroClientes.objects.count(), 1, "O cliente deveria ter sido criado no banco de dados local.")

        # 4. VERIFICAÇÃO CRUCIAL: Garante que o campo 'asaas_customer_id' está vazio
        cliente_criado = CadastroClientes.objects.get()
        self.assertEqual(cliente_criado.nome_social, self.valid_payload['nome_social'])
        self.assertIsNone(cliente_criado.asaas_customer_id, "O ID do Asaas não deveria ter sido salvo.")
        
        # 5. Verifica se a chamada ao Asaas foi tentada
        mock_requests_post.assert_called_once()
        print("\n[SUCESSO] Teste 'test_cria_cliente_localmente_mesmo_com_falha_no_asaas' passou.")

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

    @patch('clientes.views.CadastroClientesCreate.registrar_cliente_no_asaas')
    def test_criar_cliente_erro_asaas(self, mock_asaas):
        """Testa criação de cliente quando o Asaas retorna erro"""
        # Configura o mock para simular erro
        mock_asaas.return_value = None

        response = self.client.post(
            self.base_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        # Ainda deve criar o cliente localmente
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CadastroClientes.objects.count(), 1)
        
        # Verifica que o ID do Asaas não foi salvo
        cliente = CadastroClientes.objects.first()
        self.assertIsNone(cliente.asaas_customer_id)

    




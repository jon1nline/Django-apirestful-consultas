from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone
from datetime import  timedelta
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
    
    @patch('clientes.views.asaas_token', 'mock_token_de_teste')
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

    @patch('clientes.views.asaas_token', 'mock_token_de_teste')
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


@patch('clientes.views.webhook_token', 'meu-token-secreto-de-teste')
class GerenciarPagamentoWebhookTests(TestCase):

    def setUp(self):
        """
        Configuração executada antes de cada teste.
        """
        self.client = APIClient()
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

        self.consulta = AgendamentosConsultas.objects.create(
            profissional=self.profissional,
            data_consulta=timezone.now() + timedelta(days=1),
            cliente_id =self.cliente.id,
            status_consulta = 'agendada',
            consulta_ativa=True
        )

         # Criação de dados pagamentos para realizar os testes
        self.pagamento = PagamentoConsultas.objects.create(
            consulta_id=self.consulta.id,
            preco_consulta=100.00,
            cliente_id=self.cliente.id,
            metodo_de_pagamento='credit_card',
            status_pagamento='pendente', # Status inicial
            asaas_payment_id='pay_1234567890' # ID que esperamos receber do Asaas
        )


        self.base_url = '/clients/consultas/gerenciarpagamento/'
        
       
        
        # Payload base para o webhook do Asaas
        self.base_payload = {
            "event": "PAYMENT_CONFIRMED",
            "payment": {
                "id": "pay_1234567890",
                "customer": "cus_0987654321",
                "value": 100.00,
                "netValue": 99.00,
                "billingType": "CREDIT_CARD",
            }
        }
        
        # Configura o header com o token CORRETO para os testes de "caminho feliz"
        self.valid_headers = {
        'HTTP_ASAAS_ACCESS_TOKEN': 'meu-token-secreto-de-teste'
        }

    def test_webhook_falha_com_token_invalido(self):
        """
        Verifica se a view retorna 401 UNAUTHORIZED se o token do webhook for inválido.
        """
        headers = {'HTTP_ASAAS_ACCESS_TOKEN': 'token-errado'}
        response = self.client.post(self.base_url, self.base_payload, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_webhook_falha_sem_token(self):
        """
        Verifica se a view retorna 401 UNAUTHORIZED se o token do webhook estiver ausente.
        """
        response = self.client.post(self.base_url, self.base_payload, format='json') # Sem header de token
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    # --- Testes de Lógica e Filtragem de Eventos ---

    def test_ignora_evento_nao_relevante(self):
        """
        Verifica se a view ignora eventos que não são de confirmação de pagamento
        e retorna 200 OK sem alterar o banco de dados.
        """
        payload = self.base_payload.copy()
        payload['event'] = 'PAYMENT_CREATED' # Um evento que deve ser ignorado

        response = self.client.post(self.base_url, payload, format='json', **self.valid_headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica se nada mudou no banco de dados
        self.pagamento.refresh_from_db()
        self.assertEqual(self.pagamento.status_pagamento, 'pendente')
        self.consulta.refresh_from_db()
        self.assertEqual(self.consulta.status_consulta, 'agendada')

    def test_falha_se_id_do_pagamento_estiver_ausente_no_payload(self):
        """
        Verifica se a view retorna 400 BAD REQUEST se o ID do pagamento não vier no payload.
        """
        payload = self.base_payload.copy()
        del payload['payment']['id'] # Remove o ID do payload

        response = self.client.post(self.base_url, payload, format='json', **self.valid_headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ignora_pagamento_nao_encontrado_no_banco_de_dados(self):
        """
        Verifica se a view retorna 200 OK (para o Asaas não reenviar) quando o ID do
        pagamento recebido não corresponde a nenhum registro local.
        """
        payload = self.base_payload.copy()
        payload['payment']['id'] = 'pay_nao_existe' # ID que não está no nosso DB

        response = self.client.post(self.base_url, payload, format='json', **self.valid_headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'Pagamento não encontrado, ignorando')

    # --- Teste do Caminho Feliz (Happy Path) ---

    def test_processa_pagamento_confirmado_com_sucesso(self):
        """
        Testa o cenário ideal: um webhook válido para um pagamento existente
        atualiza o status do pagamento e da consulta.
        """
        # Garante que os status iniciais estão corretos
        self.assertEqual(self.pagamento.status_pagamento, 'pendente')
        self.assertEqual(self.consulta.status_consulta, 'agendada')
        
        # Envia o webhook
        response = self.client.post(self.base_url, self.base_payload, format='json', **self.valid_headers)
        
        # Verifica a resposta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'Webhook processado com sucesso')
        
        # VERIFICAÇÃO CRUCIAL: Confere se o banco de dados foi atualizado
        self.pagamento.refresh_from_db()
        self.consulta.refresh_from_db()
        
        self.assertEqual(self.pagamento.status_pagamento, 'pago')
        self.assertEqual(self.consulta.status_consulta, 'confirmada')

    def test_processa_evento_payment_received_com_sucesso(self):
        """
        Garante que o evento 'PAYMENT_RECEIVED' também é processado corretamente.
        """
        payload = self.base_payload.copy()
        payload['event'] = 'PAYMENT_RECEIVED' # Testa o outro tipo de evento válido

        response = self.client.post(self.base_url, payload, format='json', **self.valid_headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.pagamento.refresh_from_db()
        self.consulta.refresh_from_db()
        
        self.assertEqual(self.pagamento.status_pagamento, 'pago')
        self.assertEqual(self.consulta.status_consulta, 'confirmada')
import json
import jwt  
from django.conf import settings  
from django.test import TestCase
from rest_framework.test import APIClient
from datetime import  datetime, timedelta
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import AgendamentosConsultas
from profissionais.models import Profissionais
from clientes.models import CadastroClientes

import json

User = get_user_model()  # Isso pegará seu CustomUser

class CadastroConsultasTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # 1. Cria o usuário de teste
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
        self.url = '/consultas/'
        self.valid_payload = {
            'profissional': self.profissional.id,
            'data_consulta': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M'),
            'cliente': self.cliente.id,
            'status_consulta':'agendada',
            'metodo_pagamento': 'pix'
        }


    def test_criar_consulta_sucesso(self):
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(AgendamentosConsultas.objects.count(), 1)

    def test_criar_consulta_data_passado(self):
        payload = self.valid_payload.copy()
        payload['data_consulta'] = (timezone.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M')
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Não é possível agendar consultas em datas ou horários passados', str(response.data))

    def test_criar_consulta_conflito_horario(self):
        # Cria primeira consulta
        self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        # Tenta criar segunda consulta no mesmo horário
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 409)
        self.assertTrue(response.data['conflito'])

    def test_criar_consulta_substituir_existente(self):
        # Cria primeira consulta
        self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        # Tenta criar segunda consulta com substituição
        payload = self.valid_payload.copy()
        payload['substituir'] = 'true'
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        # Verifica se a consulta anterior foi desativada
        self.assertEqual(AgendamentosConsultas.objects.filter(consulta_ativa=True).count(), 1)

    def test_criar_consulta_profissional_inexistente(self):
        payload = self.valid_payload.copy()
        payload['profissional'] = 9999 
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('object does not exist', str(response.data))

    def test_criar_consulta_dados_invalidos(self):
        payload = {
        'profissional': self.profissional.id,
        'data_consulta': 'data-invalida',
        'cliente': self.cliente.id,
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Formato de data inválido', str(response.data))

class EditarConsultasTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

         # 1. Cria o usuário de teste
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
        self.url = f'/consultas/{self.consulta.id}/'
        
        

    def test_editar_cliente_com_sucesso(self):

        dados_consulta = {
        'profissional': self.consulta.profissional.id,
        'data_consulta': self.consulta.data_consulta.isoformat(),
        'consulta_ativa': self.consulta.consulta_ativa,
        'status_consulta': self.consulta.status_consulta
    }
        payload = {
            "nome_social": "string",
            "cpf": "string",
            "email": "user@example.com",
            "contato": "string",
            "logradouro": "string",
            "numero": "strin",
            "complemento": "string",
            "bairro": "string",
            "cep": "string"
        }
        response = self.client.post(
            '/clients/cadastro/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201) #confirma que o novo cliente foi criado.
        new_client_id = response.json()['id']
        
        update_payload = {
        'cliente': new_client_id  
    }
        response = self.client.patch(
            self.url,
            data=json.dumps(update_payload),
            content_type='application/json'
        )
    
        self.assertEqual(response.status_code, 200)
        self.consulta.refresh_from_db()
    
    # Compara se o id está igual depois da edição
        self.assertEqual(self.consulta.cliente.id, new_client_id)

    def test_editar_consulta_inexistente(self):
        url = '/api/consultas/9999/'  # ID inexistente
        response = self.client.patch(
            url,
            data=json.dumps({'nome_paciente': 'Teste'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_editar_data_consulta(self):
        nova_data = (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M')
        payload = {
            'data_consulta': nova_data
        }
        response = self.client.patch(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.consulta.refresh_from_db()
        self.assertEqual(self.consulta.data_consulta.strftime('%Y-%m-%d %H:%M'), nova_data)

    def test_editar_data_para_passado(self):
        payload = {
            'data_consulta': (timezone.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M')
        }
        response = self.client.patch(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Não é possível alterar a consulta com data ou horário passado.', str(response.data))

class ConsultasPorProfissionalTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()


        self.user = User.objects.create_user( 
            email='test@example.com',
            password='testpass123',
            nome_social='Usuário Teste'
        )
        
           
        token = AccessToken.for_user(self.user)
        token['id'] = self.user.id  #adiciona o id pra criar o token
        
        self.client.cookies['access_token'] = str(token)

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

        self.profissional = Profissionais.objects.create(
            nome_social="Dr. Ativo",
            profissao="Médico",
            endereco="Rua dos ativos",
            contato="99888887777",
            ativo=True
        )
        self.profissional_inativo = Profissionais.objects.create(
            nome_social="Dr. Passivo",
            profissao="Médico",
            endereco="Rua dos passivos",
            contato="99888887777",
            ativo=False
        )
        
        # Cria consultas para teste
        AgendamentosConsultas.objects.create(
            profissional=self.profissional,
            data_consulta=timezone.now() + timedelta(days=1),
            cliente = self.cliente,
            status_consulta = 'agendada',
            consulta_ativa=True
        )
        AgendamentosConsultas.objects.create(
            profissional=self.profissional,
            data_consulta=timezone.now() + timedelta(days=2),
            cliente = self.cliente,
            status_consulta = 'confirmada',
            consulta_ativa=True
        )
        # Consulta inativa não deve aparecer
        AgendamentosConsultas.objects.create(
            profissional=self.profissional,
            data_consulta=timezone.now() + timedelta(days=3),
            cliente = self.cliente,
            status_consulta = 'cancelada',
            consulta_ativa=False,
        )
        

    def test_listar_consultas_profissional(self):
        url = f'/consultas/profissional/{self.profissional.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_listar_consultas_profissional_inexistente(self):
        url = '/consultas/profissional/9999/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_listar_consultas_profissional_inativo(self):
        url = f'/consultas/profissional/{self.profissional_inativo.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_ordenacao_consultas_por_data(self):
        url = f'/consultas/profissional/{self.profissional.id}/'
        response = self.client.get(url)
        datas = [item['data_consulta'] for item in response.data]
        self.assertTrue(datas == sorted(datas))        
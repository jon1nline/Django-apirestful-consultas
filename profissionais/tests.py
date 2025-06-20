from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone
from datetime import timedelta
import json
from .models import Profissionais

User = get_user_model()

class ProfissionaisAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Cria usuário para autenticação JWT
        self.user = User.objects.create_user( 
            email='test@example.com',
            password='testpass123',
            nome_social='Usuário Administrador'
        )
        
           
        token = AccessToken.for_user(self.user)
        token['id'] = self.user.id  #adiciona o id pra criar o token
        
        self.client.cookies['access_token'] = str(token)
        
        # Cria profissional de teste
        self.profissional = Profissionais.objects.create(
            nome_social="Dr. Teste",
            profissao="Médico",
            endereco="alameda dos testes",
            contato="99888887777",
            ativo=True
        )
        
        self.valid_payload = {
            'nome_social': 'Dr. Novo',
            'profissao': 'Médico',
            'endereco': 'alameda das mudanças, 32',
            'contato': '11222223333',
            'ativo': True
        }
        
        self.base_url = '/profissionais/'  # Ajuste para sua URL base

    def test_criar_profissional(self):
        response = self.client.post(
            self.base_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profissionais.objects.count(), 2)

    def test_editar_profissional(self):
        url = f'{self.base_url}{self.profissional.id}/'
        payload = {
            'profissao': 'Medico Neurologista'
        }
        response = self.client.patch(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profissional.refresh_from_db()
        self.assertEqual(self.profissional.profissao, 'Medico Neurologista')

    def test_desativar_profissional_sem_consultas(self):
        url = f'{self.base_url}{self.profissional.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profissional.refresh_from_db()
        self.assertFalse(self.profissional.ativo)

    def test_tentar_desativar_profissional_com_consultas(self):
        # Cria uma consulta futura para o profissional
        from consultas.models import AgendamentosConsultas
        AgendamentosConsultas.objects.create(
            profissional=self.profissional,
            data_consulta=timezone.now() + timedelta(days=1),
            nome_social_cliente="Paciente Teste",
            consulta_ativa=True
        )
        
        url = f'{self.base_url}{self.profissional.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.profissional.refresh_from_db()
        self.assertTrue(self.profissional.ativo)
        self.assertIn('consultas futuras', response.data['error'])

    def test_listar_profissionais(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Verifica se retorna o profissional criado no setUp

    def test_acesso_nao_autorizado(self):
        # Remove a autenticação para testar acesso não autorizado
        for cookie in list(self.client.cookies.keys()):
            del self.client.cookies[cookie]  #remove os cookies de token 
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
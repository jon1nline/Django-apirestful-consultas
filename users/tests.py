from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import User
import json

class RegistroUsuarioTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.base_url = '/users/register/'
        self.valid_payload = {
            'email': 'teste@example.com',
            'password': 'senhasegura123',
            'nome_social': 'Usuário Teste'
        }

    def test_registro_usuario_valido(self):
        response = self.client.post(
            self.base_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'teste@example.com')

    def test_registro_email_duplicado(self):
        # Cria primeiro usuário
        User.objects.create_user(
            email='teste@example.com',
            password='senha123'
        )
        
        response = self.client.post(
            self.base_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.json())

    def test_registro_sem_senha(self):
        invalid_payload = {
            'email': 'teste@example.com',
            'nome_social': 'Usuário Teste'
        }
        
        response = self.client.post(
            self.base_url,
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.json())
        
    def test_registro_email_invalido(self):
        invalid_payload = {
            'email': 'nao-um-email',
            'password': 'senhaValida123',
            'nome_social': 'Fulano'
        }
        response = self.client.post(self.base_url, invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
  

class LoginUsuarioTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.base_url = '/users/login/'
        self.user = User.objects.create_user(
            email='usuario@teste.com',
            password='senhacorreta123',
            nome_social='Usuário Teste'
        )
        
        self.valid_payload = {
            'email': 'usuario@teste.com',
            'password': 'senhacorreta123'
        }
        
        self.invalid_payload = {
            'email': 'usuario@teste.com',
            'password': 'senhaincorreta'
        }

    def test_login_valido(self):
        response = self.client.post(
            self.base_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.json())
        
        # Verifica se os cookies foram setados
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
        self.assertTrue(response.cookies['access_token'].value)
        self.assertTrue(response.cookies['refresh_token'].value)

    def test_login_senha_incorreta(self):
        response = self.client.post(
            self.base_url,
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['detail'], 'e-mail ou senha invalidos')

    def test_login_usuario_inexistente(self):
        payload = {
            'email': 'naoexiste@teste.com',
            'password': 'qualquersenha'
        }
        
        response = self.client.post(
            self.base_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['detail'], 'e-mail ou senha invalidos')

    def test_login_sem_email(self):
        payload = {
            'password': 'senhacorreta123'
        }
        
        response = self.client.post(
            self.base_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.json())

    def test_login_sem_senha(self):
        payload = {
            'email': 'naoexiste@teste.com'
        }
        
        response = self.client.post(
            self.base_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.json())

    def test_login_email_invalido(self):
        data = {
            'email': 'nao-e-um-email',
            'password': 'qualquer'
        }
        response = self.client.post(self.base_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)                        
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from .views import CadastroConsultas 
from .models import AgendamentosConsultas
from profissionais.models import Profissionais

class ProfissionalAPITestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = CadastroConsultas.as_view()
        self.url = '/consultas/'
        self.profissional = Profissionais.objects.create(
            nome_social="Dr. Smith",
            profissao="Cardiologia",
            endereco="rua dos testes",
            contato="21999999999"
        )
        
    def teste_criar_consultas(self):
        """teste para criar consultas"""
        data = {'dataConsulta': '2025-06-11',
                'comparecimento':'false',
                'profissional': self.profissional.id,
                'nome_social_cliente':'estou enfermo'
                }  
        request = self.factory.post(
            self.url, 
            data=data, 
            format='json' 
        )
               
        response = self.view(request)
        #realiza 3 checks para saber se está tudo ok com o post.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AgendamentosConsultas.objects.count(), 1)
        self.assertEqual(AgendamentosConsultas.objects.get().nome_social_cliente, 'estou enfermo') 
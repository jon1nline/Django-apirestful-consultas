from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from .views import CadastroProfissionais  # Import your actual view
from .models import de_Saude  # Import your model if needed

class ProfissionalAPITestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = CadastroProfissionais.as_view()
        self.url = '/profissionais/'
        
    def teste_criar_profissional(self):
        """teste para criar profissional"""
        data = {'nome_social': 'enfermeiro dos testes',
                'profissao':'enfermeiro',
                'endereco':'rua da enfermagem',
                'contato':'99999999999'
                }  
        request = self.factory.post(
            self.url, 
            data=data, 
            format='json' 
        )
               
        response = self.view(request)
        #realiza 3 checks para saber se está tudo ok com o post.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(de_Saude.objects.count(), 1)
        self.assertEqual(de_Saude.objects.get().nome_social, 'enfermeiro dos testes')
        
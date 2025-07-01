from django.shortcuts import render
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Profissionais
from .serializers import SerializerProfissionais
from consultas.views import check_login
from consultas.models import AgendamentosConsultas
import logging, sys

class CadastroProfissionais(generics.ListCreateAPIView):
    queryset = Profissionais.objects.all()
    serializer_class = SerializerProfissionais
    
    def list(self, request, *args, **kwargs):
        #verifica se o usuario está autenticado para exibir os profissionais.
        payload, error = check_login(request)
        if error:
            logging.debug('usuário não conectado tentou listar os profissionais.')
            return error
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        #só criar o novo profissional se o usuário estiver logado.
        payload, error = check_login(request)
        if error:
            logging.debug('usuário não conectado tentou criar novos profissionais.')
            return error   
             
        logging.debug(f'profissional {request.data.get("nome_social")} cadastrado.')
        return super().create(request, *args, **kwargs)
        
       

class EditarExcluirProfissionais(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profissionais.objects.all()
    http_method_names = ['patch', 'delete']  
    serializer_class = SerializerProfissionais
   
    
    def patch(self, request, *args, **kwargs): #edita o profissional de saúde
        
        payload, error = check_login(request)
        if error:
            logging.debug('usuário não conectado tentou editar os profissionais.')
            return error
        

        try:
            instance = self.get_queryset().get(pk=kwargs.get('pk'))
        except Profissionais.DoesNotExist:
            logging.debug('O profissional não foi encontrado para edição.')
            return Response(
                {'error': 'Profissional não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        logging.debug(f'O profissional {kwargs.get('pk')} foi editado com sucesso.')
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        #deleta o profissional
        payload, error = check_login(request)
        if error:
            logging.debug('usuário não conectado tentou excluir um profissional.')
            return error
        
        try:
            profissional = self.get_object()
        except Profissionais.DoesNotExist:
            logging.debug('O profissional mencionado para exclusão não existe.')
            return Response(
                {'error': 'Profissional não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        consultas_futuras = AgendamentosConsultas.objects.filter(
        profissional=profissional,
        data_consulta__gte=timezone.now(),
        consulta_ativa=True,  # Pesquisa consultas futuras para esse profissional.
        ).exists()
        if consultas_futuras:
            logging.debug(f'Não foi possivel excluir o profissional {request.data.get('nome_social')}, Ele possui consultas futuras.')
            return Response(
            {'error': 'Não é possível excluir/desativar o profissional pois há consultas futuras agendadas.'},
            status=status.HTTP_400_BAD_REQUEST
        )

         # inativa o profissional caso não haja consultas futuras.
        profissional.ativo = False
        profissional.save() 
        logging.debug(f'O profissional {request.data.get('nome_social')} foi desativado.')
        return Response(
        {'message': 'Profissional desativado com sucesso.'},
        status=status.HTTP_200_OK
    )
    
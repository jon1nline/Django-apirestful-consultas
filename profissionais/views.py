from django.shortcuts import render
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Profissionais
from .serializers import SerializerProfissionais
from consultas.views import check_login
from consultas.models import AgendamentosConsultas

class CadastroProfissionais(generics.ListCreateAPIView):
    queryset = Profissionais.objects.all()
    serializer_class = SerializerProfissionais
    
    def list(self, request, *args, **kwargs):
        #verifica se o usuario está autenticado para exibir os profissionais.
        payload, error = check_login(request)
        if error:
            return error
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        #só criar o novo profissional se o usuário estiver logado.
        payload, error = check_login(request)
        if error:
            return error        
        return super().create(request, *args, **kwargs)

class EditarExcluirProfissionais(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profissionais.objects.all()
    http_method_names = ['patch', 'delete']  
    serializer_class = SerializerProfissionais
   
    
    def patch(self, request, *args, **kwargs): #edita o profissional de saúde
        
        payload, error = check_login(request)
        if error:
            return error
        

        try:
            instance = self.get_queryset().get(pk=kwargs.get('pk'))
        except Profissionais.DoesNotExist:
            return Response(
                {'error': 'Profissional não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        #deleta o profissional
        payload, error = check_login(request)
        if error:
            return error
        
        try:
            profissional = self.get_object()
        except Profissionais.DoesNotExist:
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
            return Response(
            {'error': 'Não é possível excluir/desativar o profissional pois há consultas futuras agendadas.'},
            status=status.HTTP_400_BAD_REQUEST
        )

         # inativa o profissional caso não haja consultas futuras.
        profissional.ativo = False
        profissional.save() 

        return Response(
        {'message': 'Profissional desativado com sucesso.'},
        status=status.HTTP_200_OK
    )
    
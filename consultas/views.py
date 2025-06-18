from django.shortcuts import render
from rest_framework import generics, status
from .models import AgendamentosConsultas
from .serializers import SerializerConsultas
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from users.utils.jwt_utils import verificar_token_cookies

#verifica se o usuário autenticou antes de proceder
def check_login( request):
    payload, error_response = verificar_token_cookies(request)
    if error_response:
        return None, error_response
    return payload, None

class CadastroConsultas(generics.ListCreateAPIView):
    queryset = AgendamentosConsultas.objects.all()
    serializer_class = SerializerConsultas
    http_method_names = ['post'] 

    
    def create(self, request, *args, **kwargs):
        #só cria consultas se o usuário estiver logado na conta.
        payload, error = check_login(request)
        if error:
            return error        
        return super().create(request, *args, **kwargs)

    

class EditarConsultas(generics.RetrieveUpdateDestroyAPIView):
    queryset = AgendamentosConsultas.objects.all()
    http_method_names = ['patch','get']  
    serializer_class = SerializerConsultas
    
    def retrieve(self, request, *args, **kwargs): #exibe consulta por id
        payload, error = check_login(request)
        if error:
            return error
        
        try:
            instance = self.get_queryset().get(pk=kwargs.get('pk'))
        except AgendamentosConsultas.DoesNotExist:
            return Response(
                {'error': 'Consulta não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        return super().retrieve(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs): #editar consultas
        
        payload, error = check_login(request)
        if error:
            return error
        

        try:
            instance = self.get_queryset().get(pk=kwargs.get('pk'))
        except AgendamentosConsultas.DoesNotExist:
            return Response(
                {'error': 'Consulta não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    

class ConsultasPorProfissional(generics.ListAPIView):
    serializer_class = SerializerConsultas

    def get_queryset(self):
        profissional_id = self.kwargs['profissional_id']
        return AgendamentosConsultas.objects.filter(profissional_id=profissional_id)

    def list(self, request, *args, **kwargs):
        
        # 1. check de token 
        payload, error = check_login(request)
        if error:
            return error

        queryset = self.filter_queryset(self.get_queryset())

        # 3. Check de existencia do profissional
        if not queryset.exists():
            return Response(
                {'error': 'Profissional não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 4. filtro paginado.
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
   
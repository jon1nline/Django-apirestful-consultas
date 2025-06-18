from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Profissionais
from .serializers import SerializerProfissionais
from consultas.views import check_login

class CadastroProfissionais(generics.ListCreateAPIView):
    queryset = Profissionais.objects.all()
    serializer_class = SerializerProfissionais

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
            instance = self.get_object()
        except Profissionais.DoesNotExist:
            return Response(
                {'error': 'Profissional não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        self.perform_destroy(instance)
        return Response(
            {'message': 'Profissional deletado com sucesso'},
            status=status.HTTP_204_NO_CONTENT
        )
    
from django.shortcuts import render
from .models import CadastroClientes, PagamentoConsultas
from .serializers import SerializerCadastroClientes, SerializerPagamentos
from consultas.views import check_login
from rest_framework import generics, status
from rest_framework.response import Response
from consultas.models import AgendamentosConsultas


class CadastroClientes(generics.ListCreateAPIView):
    queryset = CadastroClientes.objects.all()
    serializer_class = SerializerCadastroClientes
    
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
    

class GerenciarPagamento(generics.UpdateAPIView):
    queryset = PagamentoConsultas.objects.all()
    serializer_class = SerializerPagamentos 
    http_method_names = ['patch']
     

    def patch(self, request, *args, **kwargs): #editar consultas
        status_pagamento = request.data.get('status_pagamento')
        Payload, error = check_login(request)
        
        if error:
            return error
        
        try:
            instance = self.get_queryset().get(pk=kwargs.get('pk'))
        except PagamentoConsultas.DoesNotExist:
            return Response(
                {'error': 'linha de pagamento não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if 'status_pagamento' in request.data and status_pagamento not in ['pendente','pago']:
            return Response(
                        {"erro": "O status de pagamento informado é invalido."},
                        status=status.HTTP_400_BAD_REQUEST
            )
        if 'status_pagamento' in request.data and (status_pagamento == 'pago'):
            try:
                # pega a id da consulta
                agendamento = instance.consulta

                if agendamento:
                    #se o agendamento existir, ele faz o update para confirmada
                    agendamento.status_consulta = 'confirmada'
                    agendamento.save()  
            except AgendamentosConsultas.DoesNotExist:
                #caso a consulta nãoo seja encontrada ele não faz alteração
                pass
            


        instance = self.get_queryset().get(pk=kwargs.get('pk'))
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)

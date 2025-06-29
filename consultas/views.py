from django.shortcuts import render
from django.utils import timezone
from rest_framework import generics, status
from .models import AgendamentosConsultas
from profissionais.models import Profissionais
from clientes.models import PagamentoConsultas, CadastroClientes
from .serializers import SerializerConsultas
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from users.utils.jwt_utils import verificar_token_cookies
from datetime import datetime

#verifica se o usuário fez login antes de proceder
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

        data_agendamento = request.data.get('data_consulta') 
        profissional_id = request.data.get('profissional') 
        cliente_id = request.data.get('cliente')

        if not cliente_id:
            return Response(
                        {"erro": "O cliente não foi encontrado nos registros."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        if not profissional_id:
            return Response(
                        {"erro": "O profissional não foi encontrado nos registros."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        #verifica se a data não está no passado 
        if data_agendamento:
            try:
                # Converte a string da data para um objeto datetime (ajuste conforme o formato da sua data)
                agendamento_dt = timezone.make_aware(datetime.strptime(data_agendamento, '%Y-%m-%d %H:%M')) 
                
                if agendamento_dt <= timezone.now():
                    return Response(
                        {"erro": "Não é possível agendar consultas em datas ou horários passados."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {"erro": "Formato de data inválido."},
                    status=status.HTTP_400_BAD_REQUEST
                ) 

            #verifica se não existe conflito na agenda

            conflito = AgendamentosConsultas.objects.filter(
                data_consulta=agendamento_dt,
                profissional_id=profissional_id,
                consulta_ativa=True,
            ).exists()   
            if conflito:
                # Verifica se o usuário enviou a flag para substituir
                substituir = str(request.data.get('substituir', '')).lower() == 'true'
                
                if not substituir:
                    return Response(
                        {
                            "erro": "Este profissional já possui uma consulta agendada para este horário.",
                            "detalhes": {
                                "data_hora_conflitante": data_agendamento,
                                "profissional_id": profissional_id,
                                "substituir": "Se desejar substituir a consulta existente, envie o parâmetro 'substituir=true'"
                            },
                            "conflito": True
                        },
                        status=status.HTTP_409_CONFLICT
                    )
                else:
                    # inativa a consulta existente antes de criar a nova
                     AgendamentosConsultas.objects.filter(
                        data_consulta=agendamento_dt,
                        profissional_id=profissional_id,
                        consulta_ativa=True
                    ).update(consulta_ativa=False,status_consulta='canceled')
             
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            nova_consulta_id = response.data['id']
            
            try:
                nova_consulta_instance = AgendamentosConsultas.objects.get(id=nova_consulta_id)
            except AgendamentosConsultas.DoesNotExist:
                # Se a consulta não for encontrada, ele irá apresentar o erro.
                return Response(
                    {"erro": "Falha ao encontrar a consulta recém-criada para gerar o pagamento."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Get additional data for the payment from the request
            metodo_pagamento = 'pix' # Provide a default
            preco_consulta = None

            try: 
                cliente_instance = CadastroClientes.objects.get(id=cliente_id)

            except CadastroClientes.DoesNotExist:
                return Response(
                    {"erro": "O cliente associado não foi encontrado."},
                    status=status.HTTP_404_NOT_FOUND    
                )
            try:
                profissional = Profissionais.objects.get(id=profissional_id)
                preco_consulta = profissional.preco_consulta
            except Profissionais.DoesNotExist:
                return Response(
                    {"erro": "O profissional associado não foi encontrado para determinar o preço."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if preco_consulta is None or preco_consulta < 0:
                 return Response(
                    {"erro": "O profissional não tem um preço de consulta válido configurado."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        

            # Create the PagamentoDeConsulta instance
            PagamentoConsultas.objects.create(
                cliente=cliente_instance,
                consulta=nova_consulta_instance,
                metodo_de_pagamento=metodo_pagamento,
                preco_consulta=preco_consulta,
                status_pagamento='pendente'  # Set the initial status
            )
        return response

    

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
        data_agendamento = request.data.get('data_consulta')
        status_consulta = request.data.get('status_consulta')
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
        if data_agendamento:
            try:
                # Converte a string da data para um objeto datetime (ajuste conforme o formato da sua data)
                agendamento_dt = timezone.make_aware(datetime.strptime(data_agendamento, '%Y-%m-%d %H:%M')) 
                
                if agendamento_dt <= timezone.now():
                    return Response(
                        {"erro": "Não é possível alterar a consulta com data ou horário passado."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {"erro": "Formato de data inválido."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if 'status_consulta' in request.data and status_consulta not in ['cancelada', 'agendada', 'confirmada', 'completa']:
            return Response(
                        {"erro": "O status da consulta informado não existe."},
                        status=status.HTTP_400_BAD_REQUEST
            )
        
        #logica para desativar a consulta completamente se for marcada como cancelada.
        if 'status_consulta' in request.data and (status_consulta == 'cancelada'):
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(consulta_ativa=False)
        else:
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(consulta_ativa=True)


        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    

class ConsultasPorProfissional(generics.ListAPIView):
    serializer_class = SerializerConsultas

    def get_queryset(self):
        profissional_id = self.kwargs['profissional_id']
        return AgendamentosConsultas.objects.filter(
            profissional_id=profissional_id,
            consulta_ativa=True  
        ).order_by('data_consulta')

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

        # 4. filtro paginado das consultas.
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
   
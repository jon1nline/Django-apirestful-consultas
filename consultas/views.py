from django.shortcuts import render
from django.utils import timezone
from django.conf import settings
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
import os, requests, json

asaas_token = settings.ASAAS_ACCESS_TOKEN
url_asaas = "https://api-sandbox.asaas.com/v3/payments"

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
            print(f'O cliente {cliente_id} não foi encontrado nos registros')
            return Response(
                        {"erro": "O cliente não foi encontrado nos registros."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        if not profissional_id:
            print(f'O profissional {profissional_id} não foi encontrado nos registros')
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
                    print('O agendamento da consulta não foi possivel. Data ou Horário está no passado')
                    return Response(
                        {"erro": "Não é possível agendar consultas em datas ou horários passados."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                print('Formato da data está errado. Não foi possível agendar a consulta.')
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
                    print(f'O profissional {profissional_id} Possui outra consulta para o horário e data mencionados.')
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
                     print('A consulta médica foi substituida.') 
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
                print(f'A consulta {nova_consulta_id} não foi encontrada para gerar o pagamento.')
                return Response(
                    {"erro": "Falha ao encontrar a consulta recém-criada para gerar o pagamento."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Get additional data for the payment from the request
            metodo_pagamento = request.data.get('metodo_pagamento') 
            preco_consulta = None
            if not metodo_pagamento:
                print('metodo de pagamento não encontrado.')
                return Response(
                    {"erro": "Inclua o campo 'metodo_pagamento':'pix,boleto ou credit_card'"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            metodos_validos = ['pix', 'boleto', 'credit_card'] # Exemplo
            if metodo_pagamento not in metodos_validos:
                print('o metodo de pagamento digitado é inválido.')
                return Response(
                    {"erro": f"Método de pagamento '{metodo_pagamento}' é inválido."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try: 
                cliente_instance = CadastroClientes.objects.get(id=cliente_id)

            except CadastroClientes.DoesNotExist:
                print(f'A cliente {cliente_instance} não foi encontrado e o pagamento não foi gerado.')
                return Response(
                    {"erro": "O cliente associado não foi encontrado."},
                    status=status.HTTP_404_NOT_FOUND    
                )
            try:
                profissional = Profissionais.objects.get(id=profissional_id)
                preco_consulta = profissional.preco_consulta
            except Profissionais.DoesNotExist:
                print(f'O profissional {profissional_id} não foi encontrado e por isso o preço da consulta não pode ser determinado.')
                return Response(
                    {"erro": "O profissional associado não foi encontrado para determinar o preço."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if preco_consulta is None or preco_consulta < 0:
                 print(f'O profissional {profissional_id} precisa ter um preço válido de consulta.')
                 return Response(
                    {"erro": "O profissional não tem um preço de consulta válido configurado."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        

            # Create the PagamentoDeConsulta instance
            novo_pagamento_data = PagamentoConsultas.objects.create(
                cliente=cliente_instance,
                consulta=nova_consulta_instance,
                metodo_de_pagamento=metodo_pagamento,
                preco_consulta=preco_consulta,
                data_vencimento=timezone.localdate(),
                status_pagamento='pendente'  # Set the initial status
            )
            
            self.registrar_pagamento_no_asaas(novo_pagamento_data)
        return response
    
    def registrar_pagamento_no_asaas(self, pagamento_data):
    
        if not asaas_token:
            print("ERRO: A variável de ambiente ASAAS_ACCESS_TOKEN não está configurada.")
            return 
        
        try:
        # Acessa o cliente relacionado ao pagamento e pega o ID do Asaas
            id_cliente_asaas = pagamento_data.cliente.asaas_customer_id
        
        # Verifica se o ID do cliente no Asaas realmente existe
            if not id_cliente_asaas:
                print(f"ERRO: O cliente {pagamento_data.cliente.id} não possui um asaas_customer_id registrado.")
                return

        except AttributeError:
        # Este erro acontece se pagamento_data.cliente for None ou se o campo não existir
            print("ERRO: Não foi possível encontrar o cliente associado a este pagamento.")
            return

        asaas_payload = {
            "billingType": pagamento_data.metodo_de_pagamento,
            "value": pagamento_data.preco_consulta,
            "dueDate": pagamento_data.data_vencimento.strftime('%Y-%m-%d'),
            "customer": id_cliente_asaas,
            "description": f"Pagamento da consulta ID {pagamento_data.consulta.id} para o cliente {pagamento_data.cliente.nome_social}",
            "externalReference": f"PAGAMENTO_{pagamento_data.id}" # Referência externa para conciliação
        }
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "access_token": asaas_token
        }
        print("Enviando para o Asaas o payload:", asaas_payload)

    # --- EXECUÇÃO DA CHAMADA À API ---
        try:
            response = requests.post(url_asaas, json=asaas_payload, headers=headers)
            response.raise_for_status()  # Lança uma exceção para erros HTTP (4xx ou 5xx)
            
            #salva o id do novo pagamento registrado
            response_data = response.json()
            id_pagamento_asaas = response_data.get('id')
            pagamento_data.asaas_payment_id = id_pagamento_asaas 
            pagamento_data.save()

        except requests.exceptions.RequestException as e:
            print(f"ERRO DE CONEXÃO: Falha ao se comunicar com a API do Asaas. Erro: {e}")
            return None
        
    # --- TRATAMENTO DA RESPOSTA ---
        response_data = response.json()
        print("Resposta do Asaas:", response_data)

    # Verifica se a cobrança foi criada com sucesso
        if response.status_code == 200:
            print("Pagamento criado com sucesso no Asaas!")
        
        
        else:
        # Se a resposta não for a esperada
            print(f"ERRO: O Asaas retornou um status inesperado ou um erro.")
            print(f"Status Code: {response.status_code}")
            print(f"Resposta: {response_data}")
        return None 
    

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
            print('a consulta informada para edição não existe.')
            return Response(
                {'error': 'Consulta não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        if data_agendamento:
            try:
                # Converte a string da data para um objeto datetime (ajuste conforme o formato da sua data)
                agendamento_dt = timezone.make_aware(datetime.strptime(data_agendamento, '%Y-%m-%d %H:%M')) 
                
                if agendamento_dt <= timezone.now():
                    print('Não é possivel editar consultas em datas ou horários passados.')
                    return Response(
                        {"erro": "Não é possível alterar a consulta com data ou horário passado."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                print('a data informada está no formato inválido.')
                return Response(
                    {"erro": "Formato de data inválido."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if 'status_consulta' in request.data and status_consulta not in ['cancelada', 'agendada', 'confirmada', 'completa']:
            print(f'o status da consulta /{status_consulta}/ não existe no sistema.')
            return Response(
                        {"erro": "O status da consulta informado não existe."},
                        status=status.HTTP_400_BAD_REQUEST
            )
        
        #logica para desativar a consulta completamente se for marcada como cancelada.
        if 'status_consulta' in request.data and (status_consulta == 'cancelada'):
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(consulta_ativa=False)
            print('a consulta foi desativada com sucesso.')

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
            print('o profissional informado não está cadastrado.')
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
    
    
   
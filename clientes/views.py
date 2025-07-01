from django.shortcuts import render
from django.conf import settings
from .models import CadastroClientes, PagamentoConsultas
from .serializers import SerializerCadastroClientes
from consultas.views import check_login
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .validador_cpf import validar_cpf
import requests, json, os, logging, sys

asaas_token = settings.ASAAS_ACCESS_TOKEN
url_asaas = "https://api-sandbox.asaas.com/v3/customers"
webhook_token = settings.TOKEN_ASAAS_ACESSO_API

logging.basicConfig(
    level=logging.DEBUG,  # Captura logs a partir do nível DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout  # Direciona a saída para stdout
)

class CadastroClientesCreate(generics.ListCreateAPIView):
    queryset = CadastroClientes.objects.all()
    serializer_class = SerializerCadastroClientes
    
    def list(self, request, *args, **kwargs):
        #verifica se o usuario está autenticado para exibir os profissionais.
        
        payload, error = check_login(request)
        if error:
            return error
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        #só criar o novo cliente se o usuário estiver logado.
        payload, error = check_login(request)
        if error:
            return error        
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
           novo_cliente_data = response.data
           self.registrar_cliente_no_asaas(novo_cliente_data)
           print(f"Cliente {novo_cliente_data.get('id')} registrado com sucesso.")

        return response
    def registrar_cliente_no_asaas(self, cliente_data):
    
        if not asaas_token:
            print("ERRO: A variável de ambiente ASAAS_ACCESS_TOKEN não está configurada.")
            return

        # 5. Mapeia os campos do seu modelo para os campos esperados pela API do Asaas
        asaas_payload = {
            "name": cliente_data.get("nome_social"),
            "cpfCnpj": cliente_data.get("cpf"),
            "email": cliente_data.get("email"),
            "phone": cliente_data.get("contato"),
            "address": cliente_data.get("logradouro"),
            "addressNumber": cliente_data.get("numero"),
            "complement": cliente_data.get("complemento"),
            "province": cliente_data.get("bairro"),
            "postalCode": cliente_data.get("cep"),
            "notificationDisabled": True,
        }
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "access_token": asaas_token
        }

        try:
            asaas_response = requests.post(url_asaas, json=asaas_payload, headers=headers, timeout=15)
            
            #Verifica se o cliente foi criado com sucesso no Asaas
            if asaas_response.status_code == 200:
                print(f"Cliente {cliente_data.get('id')} registrado com sucesso no Asaas.")
                asaas_data = asaas_response.json()
                asaas_customer_id = asaas_data.get('id')
                
                try:
                    cliente_local = CadastroClientes.objects.get(id=cliente_data.get('id'))
                    cliente_local.asaas_customer_id = asaas_customer_id
                    cliente_local.save(update_fields=['asaas_customer_id'])
                    print(f"ID do Asaas '{asaas_customer_id}' associado ao cliente local.")
                except CadastroClientes.DoesNotExist:
                    print(f"ERRO: Não foi possível encontrar o cliente local com id {cliente_data.get('id')} para salvar o ID do Asaas.")
                
            else:
                # Se der erro, imprima o status e a mensagem de erro do Asaas
                print(f"ERRO ao registrar cliente no Asaas. Status: {asaas_response.status_code}")
                print(f"Resposta do Asaas: {asaas_response.text}")

        except requests.exceptions.RequestException as e:
            # Erro de conexão com a API do Asaas
            print(f"ERRO de conexão com a API do Asaas: {e}")

class GerenciarPagamento(APIView):
    authentication_classes = []
    permission_classes = []
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        #SEGURANÇA: Validar o token do webhook vindo do header
        sent_token = request.headers.get("Asaas-Access-Token")
        logging.debug(f"{sent_token} token enviado pelo asaas")
        logging.debug(f"{webhook_token} token salvo no docker")
        if not sent_token or sent_token != webhook_token:
            print("Webhook recebido com token inválido ou ausente.")
            return Response({"error": "Acesso não autorizado"}, status=status.HTTP_401_UNAUTHORIZED)

        #EXTRAIR OS DADOS DO PAYLOAD DO WEBHOOK
        payload = request.data
        event_type = payload.get("event")
        payment_data = payload.get("payment", {})
        
        print(f"Webhook recebido! Evento: {event_type}")

        #VERIFICAR O TIPO DE EVENTO
        # Processamos apenas quando o pagamento é confirmado ou recebido
        if event_type in ["PAYMENT_CONFIRMED", "PAYMENT_RECEIVED"]:
            
            asaas_payment_id = payment_data.get("id")
            if not asaas_payment_id:
                return Response({"error": "ID do pagamento não encontrado no payload"}, status=status.HTTP_400_BAD_REQUEST)

            #ENCONTRAR NOSSO PAGAMENTO LOCAL USANDO O ID DO ASAAS
            try:
                pagamento_consulta = PagamentoConsultas.objects.get(asaas_payment_id=asaas_payment_id)
            except PagamentoConsultas.DoesNotExist:
                print(f"ERRO: Pagamento com ID Asaas {asaas_payment_id} não encontrado no nosso sistema.")
                # Retornamos 200 OK mesmo assim para que o Asaas não tente reenviar o webhook
                return Response({"status": "Pagamento não encontrado, ignorando"}, status=status.HTTP_200_OK)

            #ATUALIZAR OS STATUS
            # Atualiza o status do pagamento para 'pago'
            pagamento_consulta.status_pagamento = 'pago'
            pagamento_consulta.save()
            print(f"Pagamento {pagamento_consulta.id} atualizado para PAGO.")

            #Atualiza o status da consulta para 'confirmada'
            try:
                agendamento = pagamento_consulta.consulta
                if agendamento:
                    agendamento.status_consulta = 'confirmada'
                    agendamento.save()
                    print(f"Agendamento {agendamento.id} atualizado para CONFIRMADA.")
            except Exception as e:
                print(f"Erro ao tentar atualizar o agendamento relacionado: {e}")
                # Não para o processo, apenas registra o erro
        
        else:
            print(f"Evento '{event_type}' não relevante, ignorando.")

        # 6. RESPONDER AO ASAAS COM 200 OK
        # É CRÍTICO retornar 200 para o Asaas saber que você recebeu o webhook com sucesso.
        return Response({"status": "Webhook processado com sucesso"}, status=status.HTTP_200_OK)
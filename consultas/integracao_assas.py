import uuid
from datetime import datetime, timedelta
from django.http import JsonResponse

class AsaasMock:
    def __init__(self):
        self.customers = []
        self.payments = []
        self.subscriptions = []
        
    def create_customer(self, data):
        """Mock para criação de cliente no Asaas"""
        customer = {
            'id': f'cus_{uuid.uuid4().hex[:10]}',
            'name': data.get('name'),
            'cpfCnpj': data.get('cpfCnpj'),
            'email': data.get('email'),
            'mobilePhone': data.get('mobilePhone'),
            'dateCreated': datetime.now().isoformat(),
            'deleted': False
        }
        self.customers.append(customer)
        return JsonResponse(customer, status=201)
    
    def create_payment(self, data):
        """Mock para criação de pagamento no Asaas"""
        # Verifica se o cliente existe
        customer = next((c for c in self.customers if c['id'] == data.get('customer')), None)
        if not customer:
            return JsonResponse({'error': 'Customer not found'}, status=404)
        
        due_date = data.get('dueDate') or (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        payment = {
            'id': f'pay_{uuid.uuid4().hex[:10]}',
            'customer': data.get('customer'),
            'billingType': data.get('billingType', 'BOLETO'),
            'value': float(data.get('value', 0)),
            'dueDate': due_date,
            'description': data.get('description', 'Consulta Médica'),
            'status': 'PENDING',
            'dateCreated': datetime.now().isoformat(),
            'paymentDate': None
        }
        
        # Adiciona informações específicas do método de pagamento
        if payment['billingType'] == 'BOLETO':
            payment['bankSlipUrl'] = f'https://sandbox.asaas.com/mock/boleto/{payment["id"]}'
        elif payment['billingType'] == 'PIX':
            payment['pixQrCode'] = f'00020104...{payment["id"]}'
            payment['pixPayload'] = f'00020104...{payment["id"]}'
            payment['pixExpirationDate'] = (datetime.now() + timedelta(days=1)).isoformat()
        
        self.payments.append(payment)
        return JsonResponse(payment, status=201)
    
    def get_payment_status(self, payment_id):
        """Mock para consultar status de pagamento"""
        payment = next((p for p in self.payments if p['id'] == payment_id), None)
        if not payment:
            return JsonResponse({'error': 'Payment not found'}, status=404)
        
        return JsonResponse({
            'id': payment['id'],
            'status': payment['status'],
            'value': payment['value'],
            'paymentDate': payment['paymentDate']
        }, status=200)
    
    def simulate_webhook(self, payment_id, event_type='PAYMENT_RECEIVED'):
        """Mock para simular webhook do Asaas"""
        payment = next((p for p in self.payments if p['id'] == payment_id), None)
        if not payment:
            return JsonResponse({'error': 'Payment not found'}, status=404)
        
        # Atualiza status do pagamento
        if event_type == 'PAYMENT_RECEIVED':
            payment['status'] = 'RECEIVED'
            payment['paymentDate'] = datetime.now().isoformat()
        elif event_type == 'PAYMENT_OVERDUE':
            payment['status'] = 'OVERDUE'
        
        webhook_data = {
            'event': event_type,
            'payment': payment
        }
        
       
        
        return JsonResponse(webhook_data, status=200)
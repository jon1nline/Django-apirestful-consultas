from django.urls import path
from .views import CadastroClientes, GerenciarPagamento


urlpatterns = [
    path('cadastro/', CadastroClientes.as_view(), name='clientes-list-create'),
    path('consultas/<int:pk>/', GerenciarPagamento.as_view(), name='gerenciar-pagamento-detail'),
]
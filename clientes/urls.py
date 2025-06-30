from django.urls import path
from .views import CadastroClientesCreate, GerenciarPagamento


urlpatterns = [
    path('cadastro/', CadastroClientesCreate.as_view(), name='clientes-list-create'),
    path('consultas/gerenciarpagamento/', GerenciarPagamento.as_view(), name='gerenciar-pagamento-detail'),
]
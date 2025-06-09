from django.urls import path
from .views import CadastroConsultas, EditarConsultas, ConsultasPorProfissional

urlpatterns = [
    path('consultas/', CadastroConsultas.as_view(), name='listar-consultas'),
    path('consultas/<int:pk>/', EditarConsultas.as_view(), name='editar-excluir-consultas'),
    path('consultas/profissional/<int:profissional_id>/', ConsultasPorProfissional.as_view(), name='consultas-por-profissional')
    
]
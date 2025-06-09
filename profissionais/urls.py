from django.urls import path
from .views import CadastroProfissionais, ListarEditarExcluirProfissionais

urlpatterns = [
    path('profissionais/', CadastroProfissionais.as_view(), name='profissionais-list-create'),
    path('profissionais/<int:pk>/', ListarEditarExcluirProfissionais.as_view(), name='profissionais-retrieve-update-destroy'),
]
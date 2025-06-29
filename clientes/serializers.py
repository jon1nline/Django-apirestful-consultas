from rest_framework import serializers
from .models import CadastroClientes, PagamentoConsultas

class SerializerCadastroClientes(serializers.ModelSerializer):
    class Meta:
        model = CadastroClientes
        fields = '__all__'


class SerializerPagamentos(serializers.ModelSerializer):
    class Meta:
        model = PagamentoConsultas
        fields = '__all__'        
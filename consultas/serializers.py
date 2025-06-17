from rest_framework import serializers
from .models import AgendamentosConsultas

class SerializerConsultas(serializers.ModelSerializer):
    class Meta:
        model = AgendamentosConsultas
        fields = '__all__'
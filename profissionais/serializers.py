from rest_framework import serializers
from .models import Profissionais

class SerializerProfissionais(serializers.ModelSerializer):
    class Meta:
        model = Profissionais
        fields = '__all__'
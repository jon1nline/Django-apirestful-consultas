from rest_framework import serializers
from .models import de_Saude

class SerializerProfissionais(serializers.ModelSerializer):
    class Meta:
        model = de_Saude
        fields = '__all__'
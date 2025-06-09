from django.shortcuts import render
from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from .models import de_Saude
from .serializers import SerializerProfissionais
from drf_yasg import openapi

class CadastroProfissionais(generics.ListCreateAPIView):
    queryset = de_Saude.objects.all()
    serializer_class = SerializerProfissionais

class ListarEditarExcluirProfissionais(generics.RetrieveUpdateDestroyAPIView):
    queryset = de_Saude.objects.all()
    http_method_names = ['patch', 'delete']  
    serializer_class = SerializerProfissionais
    
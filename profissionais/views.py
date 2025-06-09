from django.shortcuts import render
from rest_framework import generics
from .models import de_Saude
from .serializers import SerializerProfissionais

class CadastroProfissionais(generics.ListCreateAPIView):
    queryset = de_Saude.objects.all()
    serializer_class = SerializerProfissionais

class EditarExcluirProfissionais(generics.RetrieveUpdateDestroyAPIView):
    queryset = de_Saude.objects.all()
    http_method_names = ['patch', 'get', 'delete']  
    serializer_class = SerializerProfissionais
    
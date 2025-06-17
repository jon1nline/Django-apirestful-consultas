from django.shortcuts import render
from rest_framework import generics
from .models import Profissionais
from .serializers import SerializerProfissionais

class CadastroProfissionais(generics.ListCreateAPIView):
    queryset = Profissionais.objects.all()
    serializer_class = SerializerProfissionais

class EditarExcluirProfissionais(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profissionais.objects.all()
    http_method_names = ['patch', 'get', 'delete']  
    serializer_class = SerializerProfissionais
    
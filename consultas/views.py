from django.shortcuts import render
from rest_framework import generics
from .models import Consultas
from .serializers import SerializerConsultas
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class CadastroConsultas(generics.ListCreateAPIView):
    queryset = Consultas.objects.all() 
    serializer_class = SerializerConsultas
    permission_classes = [AllowAny]
    

class EditarConsultas(generics.RetrieveUpdateDestroyAPIView):
    queryset = Consultas.objects.all()
    http_method_names = ['patch','get']  
    serializer_class = SerializerConsultas
    permission_classes = [AllowAny]

class ConsultasPorProfissional(generics.ListAPIView):
    serializer_class = SerializerConsultas
    permission_classes = [AllowAny]

    def get_queryset(self):
        profissional_id = self.kwargs['profissional_id']
        return Consultas.objects.filter(profissional_id=profissional_id)
    
    
   
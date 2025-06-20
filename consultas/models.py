from django.db import models
from django.utils import timezone

class AgendamentosConsultas(models.Model):
    data_consulta = models.DateTimeField(
        null=False,
        default=timezone.now)
    profissional = models.ForeignKey(
    'profissionais.Profissionais',  
    on_delete=models.CASCADE)
    nome_social_cliente = models.CharField(max_length=100, null=False)
    comparecimento = models.BooleanField(default=False)
    consulta_ativa = models.BooleanField(default=True)


    def __str__(self):
        return f"Data da consulta:{self.dataConsulta} Profissional{self.profissional}"
from django.db import models
from django.utils import timezone

class AgendamentosConsultas(models.Model):
    data_consulta = models.DateTimeField(
        null=False,
        default=timezone.now)
    profissional = models.ForeignKey(
    'profissionais.Profissionais',  
    on_delete=models.CASCADE)
    cliente = models.ForeignKey(
    'clientes.CadastroClientes',  
    on_delete=models.CASCADE)
    status_consulta = models.CharField(max_length=20, choices=(
        ('agendada', 'Agendada'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completa', 'Realizada'),
    ))
    consulta_ativa = models.BooleanField(default=True)


    def __str__(self):
        return f"Data da consulta:{self.data_consulta} Profissional{self.profissional}"
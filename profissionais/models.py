from django.db import models

class Profissionais(models.Model):
    id = models.AutoField(primary_key=True)
    nome_social = models.CharField(max_length=100, null=False)
    profissao = models.CharField(max_length=50, null=False)
    endereco =  models.CharField(max_length=200, null=False)   
    contato = models.CharField(max_length=11, null=False)
    ativo = models.BooleanField(default=True)


    def __str__(self):
        return f"Profissional:{self.nome_social} "


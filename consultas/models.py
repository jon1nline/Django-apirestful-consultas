from django.db import models

class Consultas(models.Model):
    idConsulta = models.AutoField(primary_key=True)
    dataConsulta = models.DateField(null=False) 
    profissional = models.ForeignKey(
    'profissionais.De_Saude',  
    on_delete=models.CASCADE)
    comparecimento = models.BooleanField(default=False)
    


    def __str__(self):
        return self.name
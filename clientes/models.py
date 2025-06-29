from django.db import models

class CadastroClientes(models.Model):
    nome_social = models.CharField(max_length=100,null=False)
    cpf = models.CharField(max_length=11,null=False,unique=True)
    email = models.EmailField(unique=True)
    contato = models.CharField(max_length=11)
    logradouro = models.CharField(max_length=200)
    numero = models.CharField(max_length=5)
    complemento = models.CharField(max_length=200)
    bairro = models.CharField(max_length=100)
    cep = models.CharField(max_length=8)

    def __str__(self):
        return f"nome social:{self.nome_social} email{self.email}"


class PagamentoConsultas(models.Model):
    cliente = models.ForeignKey(
        'clientes.CadastroClientes',  
        on_delete=models.CASCADE)
    consulta = models.ForeignKey(
        'consultas.AgendamentosConsultas',  
        on_delete=models.CASCADE)
    metodo_de_pagamento = models.CharField(max_length=20,choices=(
        ('pix', 'PIX'),
        ('boleto', 'Boleto')
    ))
    preco_consulta = models.DecimalField(
        max_digits=10,
        decimal_places=2, default=80.00
        )
    status_pagamento = models.CharField(max_length=20,choices=(
        ('pendente', 'pendente'),
        ('pago', 'pago')
    ))    

    def __str__(self):
        return f"Preço consulta:{self.preco_consulta}"        

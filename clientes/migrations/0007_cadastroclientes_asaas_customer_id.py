# Generated by Django 5.2.2 on 2025-06-29 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clientes", "0006_pagamentoconsultas_preco_consulta_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="cadastroclientes",
            name="asaas_customer_id",
            field=models.CharField(max_length=30, null=True),
        ),
    ]

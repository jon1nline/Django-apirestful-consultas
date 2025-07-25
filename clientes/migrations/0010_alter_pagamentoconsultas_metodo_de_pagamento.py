# Generated by Django 5.2.2 on 2025-06-30 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clientes", "0009_pagamentoconsultas_asaas_payment_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pagamentoconsultas",
            name="metodo_de_pagamento",
            field=models.CharField(
                choices=[
                    ("pix", "PIX"),
                    ("boleto", "BOLETO"),
                    ("credit_card", "CREDIT_CARD"),
                ],
                max_length=20,
            ),
        ),
    ]

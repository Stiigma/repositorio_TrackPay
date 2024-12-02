# Generated by Django 5.1.3 on 2024-12-01 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagos', '0002_pagorecurrente_hora_pagounico_hora'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagounico',
            name='tipo',
            field=models.CharField(choices=[('entretenimiento', 'Entretenimiento'), ('Salud', 'Salud'), ('Bancario', 'Bancaria'), ('Servicio', 'Servicio')], default='pendiente', max_length=50),
        ),
    ]

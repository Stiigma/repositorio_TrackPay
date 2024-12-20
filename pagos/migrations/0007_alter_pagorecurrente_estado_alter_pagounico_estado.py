# Generated by Django 5.1.3 on 2024-12-03 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagos', '0006_alter_pagorecurrente_tipo_alter_pagounico_tipo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagorecurrente',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('notificado', 'Notificado'), ('pagado', 'Pagado')], default='pendiente', max_length=50),
        ),
        migrations.AlterField(
            model_name='pagounico',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('notificado', 'Notificado'), ('pagado', 'Pagado')], default='pendiente', max_length=50),
        ),
    ]

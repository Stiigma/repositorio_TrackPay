# Generated by Django 5.1.3 on 2024-12-02 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagos', '0004_alter_pagorecurrente_frecuencia_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagorecurrente',
            name='fecha_inicio',
            field=models.DateField(auto_now_add=True),
        ),
    ]

# Generated by Django 5.1.3 on 2024-12-02 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagos', '0005_alter_pagorecurrente_fecha_inicio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagorecurrente',
            name='tipo',
            field=models.CharField(choices=[('entretenimiento', 'Entretenimiento'), ('salud', 'Salud'), ('bancario', 'Bancario'), ('servicio', 'Servicio')], default='pendiente', max_length=50),
        ),
        migrations.AlterField(
            model_name='pagounico',
            name='tipo',
            field=models.CharField(choices=[('entretenimiento', 'Entretenimiento'), ('salud', 'Salud'), ('bancario', 'Bancario'), ('servicio', 'Servicio')], default='pendiente', max_length=50),
        ),
    ]

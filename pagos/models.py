from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Modelo Base Abstracto
class PagoBase(models.Model):
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    concepto = models.CharField(max_length=255)  # Corregido de max_lenght a max_length
    estado = models.CharField(
        max_length=50,
        choices=[
            ('pendiente', 'Pendiente'),
            ('completado', 'Completado'),
            ('cancelado', 'Cancelado'),
        ],
        default='pendiente',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)  # Actualiza al modificar
    prioridad = models.IntegerField(choices=[
        (1, 'Importante - Urgente'),
        (2, 'Importante - No Urgente'),
        (3, 'No Importante - Urgente'),
        (4, 'No Importante - No Urgente')
    ])
    hora = models.TimeField(null=True, blank=True)  # Campo para la hora

    class Meta:
        abstract = True  # Modelo abstracto, no crea tabla en la base de datos

    def __str__(self):
        return f'{self.concepto} - {self.monto} ({self.estado})'
    
    def cambiar_estado(self, nuevo_estado):
        if nuevo_estado in ['pendiente', 'completado', 'cancelado']:
            self.estado = nuevo_estado
            self.save()
        else:
            raise ValueError("Estado no valido")
    
    def obtener_prioridad(self):
        if self.prioridad == 1:
            return f"Urgente-Importante"
        elif self.prioridad == 2:
            return f"NoUrgente-Importante"
        elif self.prioridad == 3:
            return "Urgente-NoImportante"
        elif self.prioridad == 4:
            return f"NoUrgente-NoImportante"
        else:
            return f"Sin prioridad definida"



# Modelo para Pagos Únicos
class PagoUnico(PagoBase):
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="pagos_unicos"  # Nombre único para este modelo
    )
    fecha = models.DateField()
    tipo = models.CharField(
        max_length=50,
        choices=[
            ('entretenimiento', 'Entretenimiento'),
            ('Salud', 'Salud'),
            ('Bancario', 'Bancaria'),
            ('Servicio', 'Servicio'),
        ],
        default='pendiente',
    )
    def __str__(self):
        return f"Pago Único: {self.concepto} - {self.monto} - Fecha: {self.fecha}"

    def esta_vencido(self):
        return self.fecha < date.today()

    def clase(self):
        return "pago_unico"
# Modelo para Pagos Recurrentes
class PagoRecurrente(PagoBase):
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="pagos_recurrentes"  # Nombre único para este modelo
    )
    frecuencia = models.CharField(
        max_length=50,
        choices=[
            ('diario', 'Diario'),
            ('semanal', 'Semanal'),
            ('mensual', 'Mensual'),
        ],
        default='mensual',
    )
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_fin = models.DateField(null=True, blank=True)
    tipo = models.CharField(
        max_length=50,
        choices=[
            ('entretenimiento', 'Entretenimiento'),
            ('Salud', 'Salud'),
            ('Bancario', 'Bancaria'),
            ('Servicio', 'Servicio'),
        ],
        default='pendiente',
    )

    def calcular_proximo_vencimiento(self):
        if self.frecuencia == 'mensual':
            delta = timedelta(days=30)
        elif self.frecuencia == 'anual':
            delta = timedelta(days=365)
        else:
            return None

        proximo_vencimiento = self.fecha_inicio
        while proximo_vencimiento <= date.today():
            proximo_vencimiento += delta

        return proximo_vencimiento
    
    def clase(self):
        return "pago_recurrente"
    
    def __str__(self):
        return f"Pago Recurrente: {self.concepto} - {self.monto} - Frecuencia: {self.frecuencia}"

    
class Usuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usuario')
    nombre_com = models.CharField(max_length=100)  # Nombre completo
    num_cel = models.CharField(max_length=15, blank=True, null=True)  # Número de celular
    Na = models.CharField(max_length=100, blank=True, null=True)  # Personaliza "Na"
    fecha_nac = models.DateField(blank=True, null=True)  # Fecha de nacimiento

    def __str__(self):
        return f"{self.nombre_com} ({self.usuario.email})"
    

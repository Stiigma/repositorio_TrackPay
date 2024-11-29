from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Modelo Base Abstracto
class PagoBase(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pagos")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    concepto = models.CharField(max_length=255)  # Corregido de max_lenght a max_length
    estado = models.CharField(
        max_length=50,  # Corregido de max_lenght a max_length
        choices=[
            ('pendiente', 'Pendiente'),
            ('completado', 'Completado'),
            ('cancelado', 'Cancelado'),
        ],
        default='pendiente',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)  # Actualiza al modificar
    prioridad = models.IntegerField()

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
            return "Urgente-Importante"
        elif self.prioridad == 2:
            return "NoUrgente-Importante"
        elif self.prioridad == 3:
            return "Urgente-NoImportante"
        elif self.prioridad == 4:
            return "NoUrgente-NoImportante"
        else:
            return "Sin prioridad definida"



# Modelo para Pagos Únicos
class PagoUnico(PagoBase):
    fecha = models.DateField()

    def __str__(self):
        return f"Pago Único: {self.concepto} - {self.monto} - Fecha: {self.fecha}"

    def esta_vencido(self):
        return self.fecha < date.today()


# Modelo para Pagos Recurrentes
class PagoRecurrente(PagoBase):
    frecuencia = models.CharField(
        max_length=50,
        choices=[
            ('mensual', 'Mensual'),
            ('anual', 'Anual'),
        ],
        default='mensual',
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    tipo = models.CharField(
        max_length=50,  # Corregido de max_lenght a max_length
        choices=[
            ('entretenimiento', 'Entretenimiento'),
            ('Salud', 'Salud'),
            ('Bancario', 'Bancaria'),
            ('Servicio', 'Servicio'),
        ],
        default='pendiente',
    )
    def calcular_proximo_vencimiento(self):
        # Lógica para calcular la próxima fecha de pago
        pass

    def __str__(self):
        return f"Pago Recurrente: {self.concepto} - {self.monto} - Frecuencia: {self.frecuencia}"
    
    @classmethod
    def filtrar_por_tipo(cls, tipo, usuario):
        return cls.objects.filter(tipo=tipo, usuario=usuario, estado='pendiente')

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

    
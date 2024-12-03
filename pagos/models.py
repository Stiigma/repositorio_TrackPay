from django.db import models
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta

# Modelo Base Abstracto
class PagoBase(models.Model):
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    concepto = models.CharField(max_length=255)  
    estado = models.CharField(
        max_length=50,
        choices=[
            ('pendiente', 'Pendiente'),
            ('notificado', 'Notificado'),
            ('pagado', 'Pagado'),
        ],
        default='pendiente',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)  
    prioridad = models.IntegerField(choices=[
        (1, 'Importante - Urgente'),
        (2, 'Importante - No Urgente'),
        (3, 'No Importante - Urgente'),
        (4, 'No Importante - No Urgente')
    ])
    hora = models.TimeField(null=True, blank=True) 

    class Meta:
        abstract = True 

    def __str__(self):
        return f'{self.concepto} - {self.monto} ({self.estado})'
    
    
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
        related_name="pagos_unicos"
    )
    fecha = models.DateField()
    tipo = models.CharField(
        max_length=50,
        choices=[
            ('entretenimiento', 'Entretenimiento'),
            ('salud', 'Salud'),
            ('bancario', 'Bancario'),
            ('servicio', 'Servicio'),
        ],
        default='pendiente',
    )

    def __str__(self):
        return f"Pago Único: {self.concepto} - {self.monto} - Fecha: {self.fecha}"

    def clase(self):
        return f'pago_unico'
    
    def esta_vencido(self):
    
        return self.fecha < date.today()

    def procesar_estado(self):
        
        if self.esta_vencido():
            self.cambiar_estado('pagado')

    def necesita_notificacion(self):
       
        if self.estado == 'pagado':
            return False  

        if not self.fecha:
            return False  

        dias_restantes = (self.fecha - date.today()).days

        if self.esta_vencido():
            self.cambiar_estado('pagado')  
            return False

        if self.estado == 'pendiente' and dias_restantes <= 3:
            self.cambiar_estado('notificado')  
            return True

        return False

    def cambiar_estado(self, nuevo_estado):
        
        estados_validos = ['pendiente', 'notificado', 'pagado']
        
        if nuevo_estado not in estados_validos:
            raise ValueError(f"Estado no válido: {nuevo_estado}")
        
        self.estado = nuevo_estado
        self.save()

    def enviar_notificacion(self):
        
        if self.necesita_notificacion():
            mensaje = (
                f"Hola {self.usuario.username}, recuerda que tu pago único '{self.concepto}' "
                f"de ${self.monto} vence el {self.fecha}. ¡No olvides realizarlo!"
            )
            print(f"Notificación enviada: {mensaje}")
    
class PagoRecurrente(PagoBase):
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="pagos_recurrentes"
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
            ('salud', 'Salud'),
            ('bancario', 'Bancario'),
            ('servicio', 'Servicio'),
        ],
        default='pendiente',
    )

    def calcular_proximo_vencimiento(self):
        
        if not self.fecha_fin:  
            return None  

        delta = timedelta(days=0)
        if self.frecuencia == 'diario':
            delta = timedelta(days=1)
        elif self.frecuencia == 'semanal':
            delta = timedelta(weeks=1)
        elif self.frecuencia == 'mensual':
            delta = timedelta(days=30)

        proximo_vencimiento = self.fecha_fin + delta
        return proximo_vencimiento
    def renovar_o_pagado(self):
        if self.fecha_fin < date.today():
            
            self.cambiar_estado('pagado')
            self.save()

            nuevo_pago = PagoRecurrente.objects.create(
                usuario=self.usuario,
                monto=self.monto,
                concepto=self.concepto,
                estado='pendiente',
                prioridad=self.prioridad,
                tipo=self.tipo,
                frecuencia=self.frecuencia,
                fecha_inicio=self.fecha_inicio,  
                fecha_fin=self.calcular_proximo_vencimiento(),  
                hora=self.hora, 
            )

            return nuevo_pago

        return None

    def necesita_notificacion(self):
        if self.estado in ['notificado', 'pagado']:
            return False  

        if not self.fecha_fin:
            return False  

        proximo_vencimiento = self.calcular_proximo_vencimiento()
        dias_restantes = (proximo_vencimiento - date.today()).days

        
        if dias_restantes <= 3:  
            self.cambiar_estado('notificado')
            self.save()
            return True

        return False

    def cambiar_estado(self, nuevo_estado):
        estados_validos = ['pendiente', 'notificado', 'pagado']
       
        if nuevo_estado not in estados_validos:
            raise ValueError(f"Estado no válido: {nuevo_estado}")

        self.estado = nuevo_estado
        self.save()

    def enviar_notificacion(self):
        if self.necesita_notificacion():
            proximo_vencimiento = self.calcular_proximo_vencimiento()
            mensaje = (
                f"Hola {self.usuario.username}, recuerda que tu pago recurrente '{self.concepto}' "
                f"de ${self.monto} vence el {proximo_vencimiento}. ¡No olvides realizarlo!"
            )
            print(f"Notificación enviada: {mensaje}")
            
    def clase(self):
        return f'pago_recurrente'
    
class Usuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usuario')
    nombre_com = models.CharField(max_length=100)  
    num_cel = models.CharField(max_length=15, blank=True, null=True)  
    Na = models.CharField(max_length=100, blank=True, null=True)  
    fecha_nac = models.DateField(blank=True, null=True)  

    def __str__(self):
        return f"{self.nombre_com} ({self.usuario.email})"
    

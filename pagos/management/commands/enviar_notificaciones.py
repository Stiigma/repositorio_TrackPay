import time
from datetime import date
from django.core.management.base import BaseCommand
from pagos.models import PagoUnico, PagoRecurrente
from twilio.rest import Client

# Configuración de Twilio para SMS
TWILIO_ACCOUNT_SID = 'AC006b218691adedbcc077ad85751dcf78'  
TWILIO_AUTH_TOKEN = 'caa5a431a27c60583a6419110675a830'  
TWILIO_SMS_NUMBER = '+16812286146'  

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
class Command(BaseCommand):
    help = 'Envía notificaciones de pagos pendientes vía SMS'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando verificación de pagos...")

        while True:
            hoy = date.today()

            self.verificar_pagos(PagoUnico)
            self.verificar_pagos(PagoRecurrente)

            time.sleep(5)

    def verificar_pagos(self, modelo_pago):
        pagos = modelo_pago.objects.filter(estado='pendiente')
        for pago in pagos:
            if pago.necesita_notificacion():
                self.enviar_notificacion(pago)

    def enviar_notificacion(self, pago):
        usuario = pago.usuario
        if hasattr(usuario, 'usuario') and usuario.usuario.num_cel:
            telefono = usuario.usuario.num_cel
            mensaje = f"Hola {usuario.usuario.nombre_com}, recuerda que tu pago '{pago.concepto}' de ${pago.monto} vence pronto."
            try:
                client.messages.create(
                    body=mensaje,
                    from_=TWILIO_SMS_NUMBER,  
                    to=telefono 
                )
                
                self.stdout.write(f"SMS enviado a {telefono}: {mensaje}")
                pago.cambiar_estado('notificado')
            except Exception as e:
                self.stderr.write(f"Error enviando SMS a {telefono}: {e}")
        else:
            self.stderr.write(f"El usuario {usuario.usuario.username} no tiene un número de celular registrado.")

import os
import django

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackpay.settings')  # Ajusta 'trackpay.settings' a tu proyecto
django.setup()

from pagos.models import PagoUnico,PagoRecurrente

def listar_pagos_recurrentes():
    pagos = PagoRecurrente.objects.all()
    if pagos.exists():
        print("Pagos Recurrentes:")
        for pago in pagos:
            print(f"""
                ID: {pago.id}
                Usuario: {pago.usuario.username}
                Monto: ${pago.monto:.2f}
                Concepto: {pago.concepto}
                Estado: {pago.estado}
                Tipo: {pago.tipo}
                Prioridad: {pago.prioridad}
                Hora: {pago.hora.strftime('%H:%M')}
            """)
    else:
        print("No hay pagos recurrentes registrados.")

# Ejecutar la función
if __name__ == "__main__":
    listar_pagos_recurrentes()

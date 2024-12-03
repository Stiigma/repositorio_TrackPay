from django.shortcuts import render, redirect,get_object_or_404
from pagos.forms import RegistroCompletoForm, LoginForm, PagoUnicoForm, PagoRecurrenteForm
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from pagos.models import PagoRecurrente, PagoUnico
from django.http import JsonResponse
import datetime 
import requests
import json
from datetime import date

def home(request):
    return render(request, "home/index.html")



def entrar(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
           
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                
                login(request, user)
                
                # Redirigir dinámicamente según el usuario o sus permisos
                if user.is_staff:
                    return redirect('admin_dashboard')  # Redirigir al panel de administración
                else:
                    return redirect('appFull')  
            else:
                return render(request, "home/login.html", {
                    "form": form,
                    "error": "Credenciales inválidas. Inténtalo de nuevo."
                })
    else:
        form = LoginForm()
    
    return render(request, "home/login.html", {"form": form})


def registro(request):
    if request.method == 'POST':  
        form = RegistroCompletoForm(request.POST)
        if form.is_valid():  # Validar datos del formulario
            form.save()  
            return redirect('login')  
    else:  
        form = RegistroCompletoForm()
    
    return render(request, "home/re.html", {'form': form})


@login_required
def appFull(request):
    from datetime import date

    
    pagos_unicos = list(PagoUnico.objects.filter(usuario=request.user, estado__in=['pendiente', 'notificado']))
    pagos_unicos = sorted(
        pagos_unicos,
        key=lambda pago: (pago.fecha or date.max, pago.prioridad)
    )

    pagos_recurrentes = list(PagoRecurrente.objects.filter(usuario=request.user, estado__in=['pendiente', 'notificado']))
    pagos_recurrentes = sorted(
        pagos_recurrentes,
        key=lambda pago: (pago.fecha_fin or date.max, pago.prioridad)
    )

    
    pagos_activos = pagos_unicos + pagos_recurrentes

    #
    valor_total = sum(pago.monto for pago in pagos_activos)

   
    if pagos_activos:
        pago_prioridad_obj = pagos_activos[0]  
        fecha = pago_prioridad_obj.fecha or pago_prioridad_obj.fecha_fin
        concepto = pago_prioridad_obj.concepto
        pago_prioridad = f"{fecha.strftime('%d/%m/%Y')} - {concepto}"
    else:
        pago_prioridad = "No hay pagos activos"

    
    usuario = request.user.usuario

   
    context = {
        'pagos_activos': pagos_activos,
        'usuario': usuario,
        'valor_total': valor_total,
        'pago_prioridad': pago_prioridad,
    }
    return render(request, "home/app.html", context)



def salir(request):
    logout(request)  
    return redirect('login')  



def validar_y_actualizar_pagos(usuario):
   
    pagos_unicos = PagoUnico.objects.filter(usuario=usuario)
    for pago_unico in pagos_unicos:
        
        if pago_unico.esta_vencido():
            pago_unico.cambiar_estado('pagado')  
        elif pago_unico.necesita_notificacion():
            pago_unico.enviar_notificacion()  

    # Obtener pagos recurrentes del usuario
    pagos_recurrentes = PagoRecurrente.objects.filter(usuario=usuario)
    for pago_recurrente in pagos_recurrentes:
        # Procesar el estado del pago recurrente
        if pago_recurrente.fecha_fin and pago_recurrente.fecha_fin < date.today():
            
            pago_recurrente.renovar_o_pagado()
        elif pago_recurrente.necesita_notificacion():
            pago_recurrente.enviar_notificacion()  # Envía notificación si es necesario
            
            

@login_required
def historial_pagos(request):
    
    validar_y_actualizar_pagos(request.user)
    
    pagos_unicos = list(PagoUnico.objects.filter(usuario=request.user, estado='pagado'))
    pagos_recurrentes = list(PagoRecurrente.objects.filter(usuario=request.user, estado='pagado'))

    
    hoy = datetime.datetime.now()
    mes_actual = hoy.month
    anio_actual = hoy.year
    usuario = request.user.usuario
    
    valor_mes = sum(
        pago.monto for pago in pagos_unicos
        if pago.fecha and pago.fecha.month == mes_actual and pago.fecha.year == anio_actual
    ) + sum(
        pago.monto for pago in pagos_recurrentes
        if pago.fecha_fin and pago.fecha_fin.month == mes_actual and pago.fecha_fin.year == anio_actual
    )
    
    valor_total = sum(pago.monto for pago in pagos_unicos + pagos_recurrentes)  # Suma total

  
    pagos = pagos_unicos + pagos_recurrentes
    contexto = {
        'pagos': pagos,
        'valor_mes': valor_mes,
        'valor_total': valor_total,
        'usuario' : usuario,
    }

    return render(request, 'home/historial.html', contexto)

@login_required
def crear_pago_unico(request):
    if request.method == 'POST':
        form = PagoUnicoForm(request.POST)
        if form.is_valid():
            pago_unico = form.save(commit=False)
            pago_unico.usuario = request.user  
            pago_unico.estado = 'pendiente'  
            pago_unico.save()
            return JsonResponse({'success': True, 'message': 'Pago Único creado exitosamente.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


@login_required
def crear_pago_recurrente(request):
    if request.method == 'POST':
        form = PagoRecurrenteForm(request.POST)
        if form.is_valid():
            pago_recurrente = form.save(commit=False)
            pago_recurrente.usuario = request.user 
            pago_recurrente.estado = 'pendiente'  # Asignar estado por defecto
            pago_recurrente.save()
            return JsonResponse({'success': True, 'message': 'Pago Recurrente creado exitosamente.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


from django.http import JsonResponse
import datetime

def obtener_pagos(request):
    # Obtener y ordenar pagos únicos con estado 'pendiente' o 'notificado'
    
    validar_y_actualizar_pagos(request.user)
    pagos_unicos = list(
        PagoUnico.objects.filter(
            usuario=request.user,
            estado__in=['pendiente', 'notificado']  # Incluye 'pendiente' y 'notificado'
        )
    )
    pagos_unicos = sorted(
        pagos_unicos,
        key=lambda pago: (pago.fecha or datetime.date.max, pago.prioridad)
    )
    

    pagos_recurrentes = list(
        PagoRecurrente.objects.filter(
            usuario=request.user,
            estado__in=['pendiente', 'notificado']  
        )
    )
    pagos_recurrentes = sorted(
        pagos_recurrentes,
        key=lambda pago: (pago.fecha_fin or datetime.date.max, pago.prioridad)
    )

    # Crear la respuesta JSON
    pagos_data = [
        {
            "id": pago.id,
            "concepto": pago.concepto,
            "monto": pago.monto,
            "tipo": pago.tipo,
            "fecha": pago.fecha.strftime('%Y-%m-%d') if hasattr(pago, 'fecha') and pago.fecha else None,
            "frecuencia": getattr(pago, 'frecuencia', "Ninguna"),  # Si 'frecuencia' no existe, usa "Ninguna"
            "estado": pago.estado,  # Incluye el estado en la respuesta
            "clase": "pago_unico" if isinstance(pago, PagoUnico) else "pago_recurrente"
        }
        for pago in pagos_unicos
    ] + [
        {
            "id": pago.id,
            "concepto": pago.concepto,
            "monto": pago.monto,
            "tipo": pago.tipo,
            "fecha": pago.fecha_fin.strftime('%Y-%m-%d') if hasattr(pago, 'fecha_fin') and pago.fecha_fin else None,
            "frecuencia": getattr(pago, 'frecuencia', "Ninguna"),  # Si 'frecuencia' no existe, usa "Ninguna"
            "estado": pago.estado,  # Incluye el estado en la respuesta
            "clase": "pago_unico" if isinstance(pago, PagoUnico) else "pago_recurrente"
        }
        for pago in pagos_recurrentes
    ]

    return JsonResponse(pagos_data, safe=False)


def eliminar_pago(request, pago_id):
    if request.method == 'POST':
        # Busca el pago por ID
        pago = PagoUnico.objects.filter(id=pago_id).first() or PagoRecurrente.objects.filter(id=pago_id).first()
        if pago:
            pago.delete()  # Elimina el pago
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Pago no encontrado.'})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})

@login_required
def editar_pago(request, pago_id):
    if request.method == 'POST':
        data = json.loads(request.body)  # Procesar el JSON del cliente
        tipo_clase = data.get('tipo_clase')
        concepto = data.get('subscription-name')
        fecha_vencimiento = data.get('subscription-date')
        temporalidad = data.get('subscription-temporality')
        tipo = data.get('subscription-type')
        monto = data.get('subscription-amount')

        if not tipo_clase or not pago_id:
            return JsonResponse({'success': False, 'error': 'ID y tipo de clase son requeridos.'})

        # Obtener el modelo correcto según tipo_clase
        if tipo_clase == 'pago_unico':
            pago = get_object_or_404(PagoUnico, id=pago_id, usuario=request.user)
        elif tipo_clase == 'pago_recurrente':
            pago = get_object_or_404(PagoRecurrente, id=pago_id, usuario=request.user)
        else:
            return JsonResponse({'success': False, 'error': 'Tipo de clase inválido.'})

        # Actualizar los campos
        if concepto:
            pago.concepto = concepto
        if fecha_vencimiento:
            pago.fecha_fin = fecha_vencimiento
            if isinstance(pago, PagoUnico):
                pago.fecha = fecha_vencimiento
        if temporalidad and isinstance(pago, PagoRecurrente):
            pago.frecuencia = temporalidad.lower()
        if tipo:
            pago.tipo = tipo.lower()
        if monto:
            try:
                pago.monto = float(monto)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Monto inválido.'})

        pago.save()
        return JsonResponse({'success': True, 'message': 'Pago actualizado exitosamente.'})

    return JsonResponse({'success': False, 'error': 'Método no permitido.'})



def enviar_mensaje_whatsapp(usuario, mensaje):
    """Ejemplo de función para enviar mensajes por WhatsApp."""
    # Ejemplo con Twilio
    account_sid = 'TU_ACCOUNT_SID'
    auth_token = 'TU_AUTH_TOKEN'
    from_whatsapp_number = 'whatsapp:+14155238886'  # Número Twilio
    to_whatsapp_number = f'whatsapp:{usuario.num_cel}'

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    data = {
        'From': from_whatsapp_number,
        'To': to_whatsapp_number,
        'Body': mensaje,
    }
    headers = {
        'Authorization': f'Basic {account_sid}:{auth_token}'
    }
    response = requests.post(url, data=data, auth=(account_sid, auth_token))

    if response.status_code == 201:
        print(f"Mensaje enviado a {usuario.nombre_com}: {mensaje}")
    else:
        print(f"Error al enviar mensaje: {response.content}")
        
        

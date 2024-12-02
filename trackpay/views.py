from django.shortcuts import render, redirect,get_object_or_404
from pagos.forms import RegistroCompletoForm, LoginForm, PagoUnicoForm, PagoRecurrenteForm
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from pagos.models import PagoRecurrente, PagoUnico
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import datetime
import json
def home(request):
    return render(request, "home/index.html")



def entrar(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Autenticar al usuario
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Iniciar la sesión
                login(request, user)
                
                # Redirigir dinámicamente según el usuario o sus permisos
                if user.is_staff:
                    return redirect('admin_dashboard')  # Redirigir al panel de administración
                else:
                    return redirect('appFull')  # Redirigir a la vista principal
            else:
                return render(request, "home/login.html", {
                    "form": form,
                    "error": "Credenciales inválidas. Inténtalo de nuevo."
                })
    else:
        form = LoginForm()
    
    return render(request, "home/login.html", {"form": form})


def registro(request):
    if request.method == 'POST':  # Si el formulario se envía
        form = RegistroCompletoForm(request.POST)
        if form.is_valid():  # Validar datos del formulario
            form.save()  # Guardar los datos en User y Usuario
            return redirect('login')  # Redirigir al login después del registro
    else:  # Si el formulario no se ha enviado, mostrarlo vacío
        form = RegistroCompletoForm()
    
    return render(request, "home/re.html", {'form': form})


@login_required
def appFull(request):
    
    # Obtener los pagos activos del usuario autenticado
    pagos_unicos = list(PagoUnico.objects.filter(usuario=request.user, estado='pendiente'))
    pagos_unicos = sorted(
        pagos_unicos,
        key=lambda pago: (pago.fecha or datetime.date.max, pago.prioridad)
    )
    pagos_recurrentes = list(PagoRecurrente.objects.filter(usuario=request.user, estado='pendiente'))
    pagos_recurrentes = sorted(
        pagos_recurrentes,
        key=lambda pago: (pago.fecha_fin or datetime.date.max, pago.prioridad)
    )
    
    # Combinar los pagos en una sola lista
    pagos_activos = pagos_unicos + pagos_recurrentes
    usuario = request.user.usuario
    
    context = {
        'pagos_activos': pagos_activos,
        'usuario': usuario,
    }
    return render(request, "home/app.html", context)


def salir(request):
    logout(request)  # Esto elimina la sesión actual
    return redirect('login')  # Redirige al login después de cerrar sesión

@login_required
def crear_pago_unico(request):
    if request.method == 'POST':
        form = PagoUnicoForm(request.POST)
        if form.is_valid():
            pago_unico = form.save(commit=False)
            pago_unico.usuario = request.user  # Asignar el usuario autenticado
            pago_unico.estado = 'pendiente'  # Asignar estado por defecto
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
            pago_recurrente.usuario = request.user  # Asignar el usuario autenticado
            pago_recurrente.estado = 'pendiente'  # Asignar estado por defecto
            pago_recurrente.save()
            return JsonResponse({'success': True, 'message': 'Pago Recurrente creado exitosamente.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


def obtener_pagos(request):
    # Obtener y ordenar pagos únicos
    pagos_unicos = list(PagoUnico.objects.filter(usuario=request.user, estado='pendiente'))
    pagos_unicos = sorted(
        pagos_unicos,
        key=lambda pago: (pago.fecha or datetime.date.max, pago.prioridad)
    )

    # Obtener y ordenar pagos recurrentes
    pagos_recurrentes = list(PagoRecurrente.objects.filter(usuario=request.user, estado='pendiente'))
    pagos_recurrentes = sorted(
        pagos_recurrentes,
        key=lambda pago: (pago.fecha_fin or datetime.date.max, pago.prioridad)
    )

    # Combinar ambos tipos de pagos
    pagos_activos = pagos_unicos + pagos_recurrentes

    # Crear la respuesta JSON
    pagos_data = [
        {
            "id": pago.id,
            "concepto": pago.concepto,
            "monto": pago.monto,
            "tipo": pago.tipo,
            "fecha": pago.fecha.strftime('%Y-%m-%d') if hasattr(pago, 'fecha') and pago.fecha else None,
            "frecuencia": getattr(pago, 'frecuencia', "Ninguna"),  # Si 'frecuencia' no existe, usa "Ninguna"
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

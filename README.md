# TrackPay

TrackPay es una aplicación web desarrollada con **Django** para gestionar pagos recurrentes, permitiendo a los usuarios visualizar, editar y organizar sus obligaciones financieras. Este documento detalla las funcionalidades del proyecto.

---

###### **Importante**:
creemos que los usuarios pueden llegar a dar errores. Usuario con el que todo funcion normal:
- Usuario: Stiigma
- Contrasena: eduardo

## **Estructura General**

### `models.py`

`models.py` es donde se define la estructura principal de los datos y cómo estos se relacionan entre sí. Este archivo es crucial porque organiza toda la información sobre los pagos y los usuarios en la aplicación, asegurándose de que todo se almacene y gestione correctamente en la base de datos.

Primero, se encuentra un modelo llamado PagoBase, que es una plantilla para todos los pagos. Este modelo tiene campos básicos que todos los pagos comparten, como el monto, el concepto, el estado (por ejemplo, pendiente, notificado o pagado)

```python
tipo = models.CharField(
        max_length=50,
        choices=[
            ('entretenimiento', 'Entretenimiento'),
            ('salud', 'Salud'),
            ('bancario', 'Bancario'),
            ('servicio', 'Servicio'),
        ],
        default='pendiente',
```
Un nivel de prioridad que indica qué tan urgente es el pago. 

```python
prioridad = models.IntegerField(choices=[
        (1, 'Importante - Urgente'),
        (2, 'Importante - No Urgente'),
        (3, 'No Importante - Urgente'),
        (4, 'No Importante - No Urgente')
    ])
```

Además, lleva un registro de cuándo se creó y actualizó cada pago, lo cual es útil para tener un historial. Sin embargo, PagoBase no se usa directamente para guardar datos en la base de datos; en su lugar, sirve como base para otros dos modelos más específicos: PagoUnico y PagoRecurrente.

El modelo PagoUnico es para los pagos que se hacen una sola vez. Además de los campos básicos que hereda de PagoBase, este modelo agrega información como la fecha en que vence el pago y el tipo de pago, que puede ser algo como entretenimiento, salud o servicios. 

```python
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
```

También tiene una relación con el modelo User, lo que significa que cada pago único está asociado a un usuario específico. Este modelo incluye funciones útiles como esta_vencido, que revisa si ya pasó la fecha de vencimiento, y necesita_notificacion, que verifica si se debería enviar un recordatorio al usuario sobre un pago próximo a vencer.

Por otro lado, el modelo PagoRecurrente está diseñado para manejar pagos que se repiten, como suscripciones mensuales o pagos semanales. Este modelo también hereda de PagoBase, pero añade campos para guardar información sobre la frecuencia del pago (diario, semanal o mensual)

```python
frecuencia = models.CharField(
        max_length=50,
        choices=[
            ('diario', 'Diario'),
            ('semanal', 'Semanal'),
            ('mensual', 'Mensual'),
        ],
        default='mensual',
    )
```

Así como la fecha de inicio y una fecha de finalización opcional. Además, incluye lógica para calcular automáticamente cuándo será el próximo vencimiento del pago

```python
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
```

Y si el pago llega a su fecha final, puede generar una nueva instancia del mismo pago para continuar el ciclo.

```python
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
```

Finalmente, el modelo Usuario extiende el modelo estándar User de Django para agregar más datos específicos del usuario, como su nombre completo, número de celular y fecha de nacimiento. 

```python
class Usuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usuario')
    nombre_com = models.CharField(max_length=100)  
    num_cel = models.CharField(max_length=15, blank=True, null=True)  
    Na = models.CharField(max_length=100, blank=True, null=True)  
    fecha_nac = models.DateField(blank=True, null=True)  

    def __str__(self):
        return f"{self.nombre_com} ({self.usuario.email})"

```

Este modelo permite personalizar la experiencia del usuario en la aplicación y se conecta directamente con los modelos de pagos, de manera que los pagos únicos y recurrentes siempre estén vinculados a un usuario específico.

### `settings.py`
El archivo `settings.py` en Django es el lugar donde se configura prácticamente todo lo que necesita la aplicación para funcionar correctamente. Desde la conexión con la base de datos, hasta la forma en que los usuarios interactúan con los recursos, todo se define aquí. A nivel lógico, es la base que le dice a Django cómo debe comportarse, dependiendo de si el proyecto está en desarrollo, producción u otra etapa.

Lo primero que hace `settings.py` es establecer el entorno general del proyecto. Por ejemplo, se define dónde está ubicado el directorio principal del proyecto con una variable llamada BASE_DIR. 

```python
BASE_DIR = Path(__file__).resolve().parent.parent
```

Esto le dice a Django cómo encontrar archivos importantes, como las plantillas o los archivos estáticos.

```python
STATIC_URL = '/static/'
```
Esta línea establece la URL base desde la cual se servirán los archivos estáticos (como CSS, JavaScript e imágenes) en la aplicación.

```python
STATICFILES_DIRS = [BASE_DIR / "static"]
```
Esta configuración le dice a Django dónde buscar archivos estáticos adicionales que no forman parte de una aplicación específica. En este caso, STATICFILES_DIRS apunta a un directorio llamado static ubicado en el directorio base del proyecto (BASE_DIR).

STATIC_URL y STATICFILES_DIRS trabajan juntos para gestionar cómo se sirven y organizan los archivos estáticos. STATIC_URL define la URL base y STATICFILES_DIRS indica a Django dónde buscar los archivos adicionales.

```python
 "APP_DIRS": True,
```
Esta configuración está dentro de la sección TEMPLATES y tiene un impacto en cómo Django busca plantillas. Al establecer "APP_DIRS": True, le indicas a Django que debe buscar plantillas HTML dentro de las carpetas templates de todas las aplicaciones instaladas en el proyecto.

Otro aspecto fundamental de este archivo es la configuración de seguridad. Por ejemplo, hay una variable llamada SECRET_KEY

```python
SECRET_KEY = "django-insecure-(*t2+($!7#f91vg&w5#hcatbwvhb2(0e*%vwydvqq7t&s9ttv8"
```
Que es una clave única y secreta que utiliza Django para cosas como la autenticación y la protección de datos. 

La conexión con la base de datos también se configura en este archivo. Por ejemplo, en TrackPay, se usa SQLite como base de datos, lo cual es perfecto para desarrollo porque no requiere configuraciones complejas. Si más adelante se quisiera usar una base de datos más robusta, como PostgreSQL, solo habría que cambiar esta configuración.

En resumen, settings.py es el lugar donde se toman todas las decisiones importantes sobre cómo debe funcionar el proyecto. Es como la hoja de ruta que sigue Django para asegurarse de que todo esté en su lugar.

### `urls.py`
El archivo `urls.py` en Django funciona como una especie de mapa que conecta las direcciones web que el usuario visita con las funciones específicas que están definidas en el archivo `views.py`, por lo que, cada vez que un usuario ingresa una URL en el navegador, Django consulta `urls.py` para saber qué acción debe realizar y cuál función de `views.py` debe ejecutar.

Por ejemplo, si un usuario quiere iniciar sesión y accede a la dirección /login/, Django encuentra en `urls.py` que esa ruta está vinculada a una función llamada entrar que está en `views.py`. Entonces, Django ejecuta esa función para manejar la solicitud del usuario.

Dentro de `urls.py`, las rutas se definen utilizando algo llamado path. Este comando establece la URL que se espera (como /login/) y la conecta directamente con una función.

```python
path('login/', views.entrar, name='login')
```

Aquí, la URL login/ está asociada a la función entrar en `views.py`. Esto significa que cada vez que alguien ingrese a esa dirección, Django sabrá que debe ejecutar la lógica definida en esa función.

Además, en Django es común usar nombres para las rutas con el parámetro name. Esto es útil porque, en lugar de referirnos a la URL directamente (como /login/), podemos usar el nombre de la ruta en otras partes del código, como en templates o redirecciones.

Otro aspecto importante es que `urls.py` no solo maneja direcciones simples; también puede pasar datos específicos a las funciones de `views.py`.

```python
path('eliminar-pago/<int:pago_id>/', views.eliminar_pago, name='eliminar_pago')
```
En este caso, `int:pago_id` significa que la URL debe contener un número, como /eliminar-pago/5/.

```python
def eliminar_pago(request, pago_id):
    pago = PagoUnico.objects.filter(id=pago_id).first()
    if pago:
        pago.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Pago no encontrado.'})
```
Aquí, el valor de pago_id se usa para buscar un pago en la base de datos. Si se encuentra, el pago se elimina; de lo contrario, la función devuelve un mensaje indicando que no se encontró.

`urls.py` organiza todas las posibles rutas de la aplicación y las conecta con la lógica que se encuentra en `views.py`. Es como si `urls.py` fuese una guía para que Django sepa qué hacer con cada solicitud del usuario.


### `views.py`

`views.py` es donde realmente todo ocurre, porque aquí se define toda la lógica que conecta a los usuarios con las funcionalidades del sistema. Básicamente, es el lugar donde se toman los datos de los modelos y se procesan para luego mostrarlos al usuario o para actualizar la base de datos según las acciones que este realice.

Primero, en este archivo se manejan las funciones relacionadas con el inicio y cierre de sesión, así como el registro de nuevos usuarios. Por ejemplo, la función entrar verifica si las credenciales del usuario son correctas utilizando una herramienta de Django llamada authenticate. Si los datos coinciden, el usuario puede iniciar sesión y es redirigido a la página principal o, si es un administrador, a un panel especial. 

```python
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

```

Por otro lado, la función salir simplemente cierra la sesión actual y lleva al usuario de vuelta a la página de login. 

```python
def salir(request):
    logout(request)  # Cierra la sesión
    return redirect('login')  # Redirige a la página de login
```

En cuanto al registro, la función registro permite a los nuevos usuarios crear una cuenta utilizando un formulario personalizado que incluye datos adicionales, como el nombre completo y el número de celular. Esta información se guarda en la base de datos para personalizar su experiencia.

```python
def registro(request):
    if request.method == 'POST':  
        form = RegistroCompletoForm(request.POST)
        if form.is_valid():  # Validar datos del formulario
            form.save()  
            return redirect('login')  
    else:  
        form = RegistroCompletoForm()
    
    return render(request, "home/re.html", {'form': form})

```

Además de las funciones de autenticación, `views.py` también tiene funciones clave para manejar los pagos. Por ejemplo, la función appFull es como el "panel de control" principal para los usuarios. Aquí se consultan los pagos activos (pendientes o notificados) de cada usuario, se organizan según su prioridad y fecha, y se calcula el monto total que el usuario debe. Incluso, esta función resalta el pago más importante para que el usuario pueda enfocarse en lo más urgente.

```python
@login_required
def appFull(request):
    pagos_unicos = list(PagoUnico.objects.filter(usuario=request.user, estado__in=['pendiente', 'notificado']))
    pagos_unicos = sorted(pagos_unicos, key=lambda pago: (pago.fecha or date.max, pago.prioridad))

    pagos_recurrentes = list(PagoRecurrente.objects.filter(usuario=request.user, estado__in=['pendiente', 'notificado']))
    pagos_recurrentes = sorted(pagos_recurrentes, key=lambda pago: (pago.fecha_fin or date.max, pago.prioridad))

    pagos_activos = pagos_unicos + pagos_recurrentes
    valor_total = sum(pago.monto for pago in pagos_activos)

    if pagos_activos:
        pago_prioridad_obj = pagos_activos[0]
        fecha = pago_prioridad_obj.fecha or pago_prioridad_obj.fecha_fin
        concepto = pago_prioridad_obj.concepto
        pago_prioridad = f"{fecha.strftime('%d/%m/%Y')} - {concepto}"
    else:
        pago_prioridad = "No hay pagos activos"

    context = {
        'pagos_activos': pagos_activos,
        'valor_total': valor_total,
        'pago_prioridad': pago_prioridad,
    }
    return render(request, "home/app.html", context)

```

Por otro lado, están las funciones crear_pago_unico y crear_pago_recurrente, que permiten a los usuarios registrar nuevos pagos según el tipo. Estas funciones verifican que los datos ingresados en el formulario sean válidos antes de guardarlos en la base de datos. Si algo no está bien, como un campo vacío o un formato incorrecto, el sistema devuelve un mensaje de error para que el usuario pueda corregirlo.

```python
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


```

Otra función es editar_pago, que sirve para modificar un pago existente. Aquí, el sistema toma el pago que el usuario selecciona, lo actualiza con los nuevos datos proporcionados, y guarda los cambios en la base de datos.

```python
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

```

Similarmente, la función eliminar_pago permite borrar un pago, siempre y cuando este pertenezca al usuario actual. 

```python
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


```

En ambos casos, el sistema devuelve mensajes claros para que el usuario sepa si la operación fue exitosa o no.

La función validar_y_actualizar_pagos se asegura de que los pagos estén siempre actualizados. Por ejemplo, si un pago único ya venció, lo marca automáticamente como "pagado". Si un pago recurrente llega a su fecha de vencimiento, crea una nueva instancia para continuar la recurrencia.

```python
def validar_y_actualizar_pagos(usuario):
    pagos_unicos = PagoUnico.objects.filter(usuario=usuario)
    for pago_unico in pagos_unicos:
        if pago_unico.esta_vencido():
            pago_unico.cambiar_estado('pagado')
        elif pago_unico.necesita_notificacion():
            pago_unico.enviar_notificacion()

    pagos_recurrentes = PagoRecurrente.objects.filter(usuario=usuario)
    for pago_recurrente in pagos_recurrentes:
        if pago_recurrente.fecha_fin and pago_recurrente.fecha_fin < date.today():
            pago_recurrente.renovar_o_pagado()
        elif pago_recurrente.necesita_notificacion():
            pago_recurrente.enviar_notificacion()


```

El historial de pagos también es una parte importante de TrackPay, y se gestiona con la función historial_pagos. 

```python
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

```

Esta función recopila todos los pagos completados (es decir, aquellos marcados como "pagados") y los presenta al usuario. Además, calcula estadísticas útiles, como el total pagado durante el mes actual o el monto total pagado hasta la fecha.

`views.py` es esencial porque aquí se define cómo interactúan los usuarios con el sistema. Desde iniciar sesión hasta gestionar sus pagos, todo está diseñado para ser eficiente y claro.


### `forms.py`
`forms.py` es donde se definen los formularios que los usuarios van a llenar para interactuar con la aplicación. `forms.py` se encarga de estructurar esa comunicación y asegurarse de que los datos que el usuario ingresa sean válidos antes de enviarlos al sistema.

Imagina que alguien quiere registrarse en TrackPay. El formulario en `forms.py` tiene campos para cosas como el nombre de usuario, la contraseña y otros datos como el nombre completo y el número de celular. Este formulario está diseñado para asegurarse de que el usuario complete toda la información necesaria y que lo haga correctamente. Por ejemplo, si alguien olvida ingresar su correo o escribe un correo en un formato incorrecto, el formulario devolverá un mensaje de error para que lo corrija antes de continuar.

En el caso del formulario de registro en TrackPay, llamado RegistroCompletoForm, está diseñado para trabajar directamente con el modelo de usuarios de Django, pero también incluye campos personalizados como el nombre completo y la fecha de nacimiento.

```python
class RegistroCompletoForm(forms.ModelForm):
    # Campos adicionales de Usuario
    nombre_com = forms.CharField(
        max_length=100,
        label="Nombre completo",
        widget=forms.TextInput(attrs={
            'class': 'controls',
            'placeholder': 'Ingrese su Nombre'
        })
    )
    num_cel = forms.CharField(
        max_length=15,
        label="Número de celular",
        widget=forms.TextInput(attrs={
            'class': 'controls',
            'placeholder': 'Ingrese su Número de celular'
        })
    )
    Na = forms.CharField(
        max_length=100,
        label="NA",
        widget=forms.TextInput(attrs={
            'class': 'controls',
            'placeholder': 'Ingrese su NA'
        })
    )
    fecha_nac = forms.DateField(
        label="Fecha de nacimiento",
        widget=forms.DateInput(attrs={
            'class': 'controls',
            'type': 'date'
        })
    )

    # Campos de User
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'controls',
            'placeholder': 'Ingrese su Contraseña'
        }),
        label="Contraseña"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'controls',
                'placeholder': 'Ingrese su Nombre de usuario'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'controls',
                'placeholder': 'Ingrese su Correo'
            }),
        }

    def save(self, commit=True):
        # Guardar el modelo User
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password']) 
        if commit:
            user.save()
            
            Usuario.objects.create(
                usuario=user,
                nombre_com=self.cleaned_data['nombre_com'],
                num_cel=self.cleaned_data['num_cel'],
                Na=self.cleaned_data['Na'],
                fecha_nac=self.cleaned_data['fecha_nac']
            )
        return user
```
Lo interesante es que este formulario no solo valida los datos, sino que también se encarga de guardarlos automáticamente en la base de datos si todo está bien. Esto simplifica mucho el trabajo porque no tienes que escribir todo el código para guardar cada dato manualmente.

Por otro lado, el formulario de inicio de sesión, LoginForm, es más simple porque no necesita guardar datos, solo verifica que el nombre de usuario y la contraseña sean correctos. Es como un filtro: si las credenciales son válidas, el usuario puede entrar; si no lo son, el formulario muestra un error para que el usuario intente de nuevo.

```python
class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Username",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Your Username',
            'class': 'controls'  
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter Your Password',
            'class': 'controls'  
        })
    )
```

Además, en TrackPay también hay formularios para registrar pagos, como PagoUnicoForm. Este formulario está conectado al modelo de pagos únicos, por lo que cada vez que alguien registra un pago único, el formulario toma los datos ingresados (como el concepto, la fecha y el monto) y los guarda directamente en la base de datos si todo es válido. También incluye pequeños detalles, como widgets personalizados que hacen que los campos sean más fáciles de usar. Por ejemplo, en el campo de fecha, aparece un selector de calendario para que el usuario no tenga que escribir manualmente la fecha.

```python
class PagoUnicoForm(forms.ModelForm):
    class Meta:
        model = PagoUnico
        fields = ['concepto', 'monto','fecha', 'hora', 'prioridad', 'tipo']
        widgets = {
            'concepto': forms.TextInput(attrs={
                'class': 'controls',
                'placeholder': 'Concepto del pago'
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'controls',
                'type': 'date'
            }),
            'monto': forms.DateInput(attrs={
                'class': 'controls',
                'placeholder': 'monto'
            }),
            'hora': forms.TimeInput(attrs={
                'class': 'controls',
                'type': 'time'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'controls'
            }),
            'tipo': forms.TextInput(attrs={
                'class': 'controls',
                'placeholder': 'Ejemplo: único'
            }),
        }
```

Otra ventaja es que los formularios están diseñados para trabajar en conjunto con las vistas. Por ejemplo, cuando un usuario llena un formulario y lo envía, la vista correspondiente usa ese formulario para verificar los datos y, si todo está en orden, realizar la acción necesaria, como guardar el registro en la base de datos o autenticar al usuario.

---

## **Conclusión**

En general, cada archivo juega un papel fundamental para lograr que la aplicación funcione de manera coherente, eficiente y organizada. 
En conjunto, estos archivos trabajan como un equipo bien coordinado. `settings.py` define las reglas generales, `urls.py` dirige el tráfico, `views.py` ejecuta las operaciones, `models.py` organiza y guarda los datos, y `forms.py` se encarga de que todo lo que llega al sistema sea válido. Gracias a esto, TrackPay puede ofrecer a los usuarios una experiencia fluida para gestionar sus pagos, asegurando que todo esté organizado, seguro y eficiente.

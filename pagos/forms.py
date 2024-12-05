from django import forms
from django.contrib.auth.models import User
from pagos.models import Usuario, PagoUnico, PagoRecurrente

class RegistroCompletoForm(forms.ModelForm):
    # Campos adicionales de Usuario
    nombre_com = forms.CharField(
        max_length=100,
        label="Nombre completo",
        widget=forms.TextInput(attrs={
            'class': 'controls',
            'placeholder': 'Ingrese su Nombre',
            'required': 'required'
        }),
        error_messages={
            'required': 'Por favor completa este campo.',
            'max_length': 'El nombre de usuario no puede superar los 100 caracteres.'
        }
    )
    num_cel = forms.CharField(
        max_length=15,
        label="Número de celular",
        widget=forms.TextInput(attrs={
            'class': 'controls',
            'placeholder': 'Ingrese su Número de celular'
        })
        ,
        
        error_messages={
            'required': 'Por favor completa este campo.',
            'max_length': 'El nombre de usuario no puede superar los 100 caracteres.'
        }
    )
    Na = forms.CharField(
        max_length=100,
        label="NA",
        widget=forms.TextInput(attrs={
            'class': 'controls',
            'placeholder': 'Ingrese su NA'
        })
        ,
        
        error_messages={
            'required': 'Por favor completa este campo.',
            'max_length': 'El nombre de usuario no puede superar los 100 caracteres.'
        }
    )
    fecha_nac = forms.DateField(
        label="Fecha de nacimiento",
        widget=forms.DateInput(attrs={
            'class': 'controls',
            'type': 'date'
        })
        ,
        
        error_messages={
            'required': 'Por favor completa este campo.',
            'max_length': 'El nombre de usuario no puede superar los 100 caracteres.'
        }
    )

    # Campos de User
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'controls',
            'placeholder': 'Ingrese su Contraseña'
        }),
        label="Contraseña"
        ,
        
        error_messages={
            'required': 'Por favor completa este campo.',
            'max_length': 'El nombre de usuario no puede superar los 100 caracteres.'
        }
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
            'password': forms.EmailInput(attrs={
                'class': 'controls',
                'placeholder': 'Ingresa tu contrasena'
            }),
            'nombre_com': forms.EmailInput(attrs={
                'class': 'controls',
                'placeholder': 'ingresa tu nombre'
            }),
            'num_cel': forms.EmailInput(attrs={
                'class': 'controls',
                'placeholder': 'ingresa tu numero'
            }),
            'Na': forms.EmailInput(attrs={
                'class': 'controls',
                'placeholder': 'Nacionalidad'
            }),
            'fecha_nac': forms.EmailInput(attrs={
                'class': 'controls',
                'placeholder': 'FechaNaciomiento'
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


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Usuario",
        widget=forms.TextInput(attrs={
            'placeholder': 'Coloca tu usuario',
            'class': 'controls',
            'required': 'required'
        })
        ,
        
        error_messages={
            'required': 'Por favor completa este campo.',
            'max_length': 'El nombre de usuario no puede superar los 100 caracteres.'
        }
    )
    password = forms.CharField(
        label="Contrasena",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Coloca tu contrasena',
            'class': 'controls',
            'required': 'required'
        })
        ,
        
        error_messages={
            'required': 'Por favor completa este campo.',
            'max_length': 'El nombre de usuario no puede superar los 100 caracteres.'
        }
    )

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
        
        
class PagoRecurrenteForm(forms.ModelForm):
    class Meta:
        model = PagoRecurrente
        fields = ['concepto', 'monto','frecuencia', 'fecha_fin', 'hora', 'prioridad', 'tipo']
        widgets = {
            'concepto': forms.TextInput(attrs={
                'class': 'controls',
                'placeholder': 'Nombre del pago'
            }),
            'frecuencia': forms.Select(attrs={
                'class': 'controls'
            }),
            'monto': forms.DateInput(attrs={
                'class': 'controls',
                'placeholder': 'monto'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'controls',
                'type': 'date'
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
                'placeholder': 'Ejemplo: recurrente'
            }),
        }
        
class PagoEdicionForm(forms.ModelForm):
    class Meta:
        model = PagoRecurrente
        fields = ['concepto', 'monto','frecuencia', 'fecha_fin', 'hora', 'prioridad', 'tipo']
        widgets = {
            'concepto': forms.TextInput(attrs={
                'class': 'controls',
                'placeholder': 'Nombre del pago'
            }),
            'frecuencia': forms.Select(attrs={
                'class': 'controls'
            }),
            'monto': forms.DateInput(attrs={
                'class': 'controls',
                'placeholder': 'monto'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'controls',
                'type': 'date'
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
                'placeholder': 'Ejemplo: recurrente'
            }),
        }
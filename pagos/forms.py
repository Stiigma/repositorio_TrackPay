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
        user.set_password(self.cleaned_data['password'])  # Encriptar la contraseña
        if commit:
            user.save()
            # Crear la instancia de Usuario asociada
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
        label="Username",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Your Username',
            'class': 'controls'  # Asegúrate de que coincida con el CSS
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter Your Password',
            'class': 'controls'  # Asegúrate de que coincida con el CSS
        })
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
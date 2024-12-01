from django import forms
from django.contrib.auth.models import User
from pagos.models import Usuario

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

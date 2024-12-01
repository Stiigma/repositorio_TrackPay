from django.shortcuts import render, redirect
from pagos.forms import RegistroCompletoForm, LoginForm
from django.contrib.auth import authenticate, login

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
                # Si la autenticación es exitosa, iniciar la sesión
                login(request, user)
                return redirect('home')  # Redirigir a la página principal después del login
            else:
                # Mostrar un mensaje de error si las credenciales son incorrectas
                return render(request, "home/login.html", {
                    "form": form,
                    "error": "Credenciales inválidas. Inténtalo de nuevo."
                })
    else:
        # Si es una solicitud GET, mostrar el formulario vacío
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





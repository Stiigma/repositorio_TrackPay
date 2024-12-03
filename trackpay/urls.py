"""
URL configuration for trackpay project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home'P)
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views as my_views  # Alias para las vistas locales
from django.contrib.auth import views as auth_views  # Alias para las vistas de autenticación

urlpatterns = [
    path('', my_views.home, name='home'),
    path('login/', my_views.entrar, name='login'),
    path('register/', my_views.registro, name='register'),
    path('app/', my_views.appFull, name='appFull'),
    path('logout/', my_views.salir, name='logout'),
    path("admin/", admin.site.urls),
    path('crear_pago_unico/', my_views.crear_pago_unico, name='crear_pago_unico'),
    path('crear_pago_recurrente/', my_views.crear_pago_recurrente, name='crear_pago_recurrente'),
    path('ruta-obtener-pagos/', my_views.obtener_pagos, name='obtener_pagos'),
    path('eliminar-pago/<int:pago_id>/', my_views.eliminar_pago, name='eliminar_pago'),
    path('editar_pago/<int:pago_id>/', my_views.editar_pago, name='editar_pago'),
    path('historial/', my_views.historial_pagos, name='historial'),
]

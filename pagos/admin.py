from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre_com', 'usuario', 'num_cel', 'fecha_nac')
    search_fields = ('nombre_com', 'usuario__email')


from django.contrib import admin
from .models import Usuario, PagoUnico, PagoRecurrente

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre_com', 'usuario', 'num_cel', 'fecha_nac')
    search_fields = ('nombre_com', 'usuario__email')


@admin.register(PagoUnico)
class PagoUnicoAdmin(admin.ModelAdmin):
    list_display = ('concepto', 'fecha', 'monto', 'tipo', 'usuario')
    search_fields = ('concepto', 'usuario__username')
    list_filter = ('tipo',)


@admin.register(PagoRecurrente)
class PagoRecurrenteAdmin(admin.ModelAdmin):
    list_display = ('concepto', 'frecuencia', 'fecha_inicio', 'fecha_fin', 'monto', 'usuario')
    search_fields = ('concepto', 'usuario__username')
    list_filter = ('frecuencia', 'tipo')




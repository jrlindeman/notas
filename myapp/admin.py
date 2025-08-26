from django.contrib import admin
from .models import Categoria, Nota, Paso

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")
    search_fields = ("nombre",)

@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "categoria", "fecha_actualizacion")
    list_filter = ("categoria", "fecha_actualizacion")
    search_fields = ("titulo", "descripcion")

@admin.register(Paso)
class PasoAdmin(admin.ModelAdmin):
    list_display = ("id", "nota", "titulo", "orden")
    list_filter = ("nota",)


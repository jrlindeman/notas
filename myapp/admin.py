from django.contrib import admin
from .models import Nota, Paso

class PasoInline(admin.TabularInline):
    model = Paso
    extra = 1

@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    inlines = [PasoInline]
    list_display = ('titulo', 'categoria')

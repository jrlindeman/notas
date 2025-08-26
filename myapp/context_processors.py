# myapp/context_processors.py

from .models import Categoria



def categorias_context(request):
    return {
        "categorias_menu": Categoria.objects.all().order_by("nombre")
    }


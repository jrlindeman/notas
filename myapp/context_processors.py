# myapp/context_processors.py

from .models import Categoria

"""def categorias_context(request):
    return {
        "categorias_menu": Categoria.objects.all()
    }
"""

def categorias_context(request):
    categorias = Categoria.objects.all()
    print("🔎 Categorías cargadas en el context_processor:", categorias)  # 👈 depuración
    return {"categorias_menu": categorias}

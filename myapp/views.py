# views.py
import os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from .models import Nota, Paso
from .forms import NotaForm, PasoFormSet
from .models import Categoria
from thefuzz import fuzz
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .utils import render_to_pdf 

def inicio(request):
    categoria_id = request.GET.get("categoria")
    notas = Nota.objects.all()

    if categoria_id:
        notas = notas.filter(categoria_id=categoria_id)

    return render(request, "myapp/inicio.html", {"notas": notas})



def detalle_nota(request, nota_id):
    """
    Muestra el detalle de una nota con sus pasos.
    """
    nota = get_object_or_404(Nota, id=nota_id)
    pasos = nota.pasos.all()
    return render(request, "myapp/detalle_nota.html", {"nota": nota, "pasos": pasos})


def crear_nota(request):
    """
    Crea una nueva nota junto con sus pasos.
    """
    nota = Nota()
    form = NotaForm(request.POST or None, request.FILES or None, instance=nota)
    formset = PasoFormSet(
        request.POST or None,
        request.FILES or None,
        instance=nota,
        prefix="form"
    )

    if request.method == "POST":
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                nota = form.save()
                formset.instance = nota
                formset.save()
            return redirect("inicio")

    return render(request, "myapp/crear_nota.html", {"form": form, "formset": formset})


def editar_nota(request, nota_id):
    nota = get_object_or_404(Nota, id=nota_id)
    form = NotaForm(request.POST or None, request.FILES or None, instance=nota)
    formset = PasoFormSet(
        request.POST or None,
        request.FILES or None,
        instance=nota,
        prefix="form"
    )

    if request.method == "POST":
        print("POST:", request.POST)  # 👈 debug
        print("TOTAL_FORMS:", request.POST.get("form-TOTAL_FORMS"))  # 👈 debug
        print("Formset valido?:", formset.is_valid())  # 👈 debug
        print("Errores formset:", formset.errors)  # 👈 debug
        print("Non-form errors:", formset.non_form_errors())  # 👈 debug

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                nota = form.save()
                formset.instance = nota
                formset.save()
            return redirect("inicio")

    return render(request, "myapp/editar_nota.html", {"form": form, "formset": formset})



def eliminar_nota(request, nota_id):
    """
    Elimina una nota y sus pasos asociados.
    """
    nota = get_object_or_404(Nota, id=nota_id)

    if request.method == "POST":
        nota.delete()
        return redirect("inicio")

    return render(request, "myapp/eliminar_nota.html", {"nota": nota})


def eliminar_paso(request, id):
    """
    Elimina un paso individual de una nota.
    Después de eliminar, redirige a la edición de la nota correspondiente.
    """
    paso = get_object_or_404(Paso, id=id)
    nota = paso.nota  # guardamos la nota antes de eliminar

    if request.method == "POST":
        paso.delete()
        return redirect("editar_nota", nota_id=nota.id)

    return render(
        request,
        "myapp/eliminar_paso.html",
        {"paso": paso, "nota": nota}
    )



# vista categoria

def notas_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    notas = Nota.objects.filter(categoria=categoria)
    return render(request, "myapp/inicio.html", {
        "notas": notas,
        "categoria": categoria
    })


#vista de BUSCAR NOTAS

def buscar_notas(request):
    query = request.GET.get("q", "").strip().lower()
    notas = Nota.objects.prefetch_related("pasos").all()

    if query:
        resultados = []
        for nota in notas:
            # Concatenamos todo el texto relevante de la nota y sus pasos
            texto = f"{nota.titulo or ''} {nota.descripcion or ''}"
            for paso in nota.pasos.all():
                texto += f" {paso.titulo or ''} {paso.descripcion or ''} {paso.codigo or ''}"

            texto = texto.lower()

            # Calculamos la similitud con fuzzywuzzy (partial_ratio permite encontrar subcadenas parecidas)
            similitud = fuzz.partial_ratio(query, texto)

            if similitud >= 60:  # 👈 Ajusta el umbral de tolerancia (0–100)
                resultados.append((nota, similitud))

        # Ordenamos los resultados de mayor a menor similitud
        resultados = sorted(resultados, key=lambda x: x[1], reverse=True)

        # Nos quedamos solo con las notas
        notas = [r[0] for r in resultados]

    return render(request, "myapp/inicio.html", {
        "notas": notas,
        "query": query
    })


def exportar_nota_pdf(request, nota_id):
    nota = Nota.objects.get(id=nota_id)

    # Preparar rutas absolutas para imágenes
    pasos = []
    for paso in nota.pasos.all():
        imagen_absoluta = None
        if paso.imagen:
            imagen_absoluta = os.path.join(settings.MEDIA_ROOT, paso.imagen.name)
        pasos.append({
            'titulo': paso.titulo,
            'descripcion': paso.descripcion,
            'codigo': paso.codigo,
            'imagen_absoluta': imagen_absoluta
        })

    context = {
        'nota': nota,
        'pasos': pasos
    }

    template = get_template('myapp/pdf_template.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="nota_{nota.id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response

# Vista de prueba
def test(request):
    return render(request, 'myapp/test.html')

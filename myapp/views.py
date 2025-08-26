import os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.template.loader import get_template
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from thefuzz import fuzz
from xhtml2pdf import pisa

from .models import Nota, Paso, Categoria
from .forms import NotaForm, PasoFormSet


# Vista protegida: listado de notas
@login_required
def index(request):
    notas = Nota.objects.all()
    return render(request, 'myapp/index.html', {'notas': notas})


# Vista protegida: perfil del usuario
@login_required
def perfil(request):
    return render(request, 'myapp/perfil.html', {
        'usuario': request.user
    })


# Vista protegida: detalle de nota
@login_required
def detalle_nota(request, nota_id):
    nota = get_object_or_404(Nota, id=nota_id)
    pasos = nota.pasos.all()
    return render(request, "myapp/detalle_nota.html", {"nota": nota, "pasos": pasos})


# Vista protegida: crear nota
@login_required
def crear_nota(request):
    nota = Nota()
    form = NotaForm(request.POST or None, request.FILES or None, instance=nota)
    formset = PasoFormSet(request.POST or None, request.FILES or None, instance=nota, prefix="form")

    if request.method == "POST":
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                nota = form.save()
                formset.instance = nota
                formset.save()
            return redirect("inicio")

    return render(request, "myapp/crear_nota.html", {"form": form, "formset": formset})


# Vista protegida: editar nota
@login_required
def editar_nota(request, nota_id):
    nota = get_object_or_404(Nota, id=nota_id)
    form = NotaForm(request.POST or None, request.FILES or None, instance=nota)
    formset = PasoFormSet(request.POST or None, request.FILES or None, instance=nota, prefix="form")

    if request.method == "POST":
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                nota = form.save()
                formset.instance = nota
                formset.save()
            return redirect("inicio")

    return render(request, "myapp/editar_nota.html", {"form": form, "formset": formset})


# Vista protegida: eliminar nota
@login_required
def eliminar_nota(request, nota_id):
    nota = get_object_or_404(Nota, id=nota_id)

    if request.method == "POST":
        nota.delete()
        return redirect("inicio")

    return render(request, "myapp/eliminar_nota.html", {"nota": nota})


# Vista protegida: eliminar paso
@login_required
def eliminar_paso(request, id):
    paso = get_object_or_404(Paso, id=id)
    nota = paso.nota

    if request.method == "POST":
        paso.delete()
        return redirect("editar_nota", nota_id=nota.id)

    return render(request, "myapp/eliminar_paso.html", {"paso": paso, "nota": nota})


# Vista protegida: notas por categoría
@login_required
def notas_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    notas = Nota.objects.filter(categoria=categoria)
    return render(request, "myapp/inicio.html", {
        "notas": notas,
        "categoria": categoria
    })


# Vista protegida: buscador inteligente
@login_required
def buscar_notas(request):
    query = request.GET.get("q", "").strip().lower()
    notas = Nota.objects.prefetch_related("pasos").all()

    if query:
        resultados = []
        for nota in notas:
            texto = f"{nota.titulo or ''} {nota.descripcion or ''}"
            for paso in nota.pasos.all():
                texto += f" {paso.titulo or ''} {paso.descripcion or ''} {paso.codigo or ''}"
            texto = texto.lower()
            similitud = fuzz.partial_ratio(query, texto)
            if similitud >= 60:
                resultados.append((nota, similitud))

        resultados = sorted(resultados, key=lambda x: x[1], reverse=True)
        notas = [r[0] for r in resultados]

    return render(request, "myapp/inicio.html", {
        "notas": notas,
        "query": query
    })


# Vista protegida: exportar PDF
@login_required
def exportar_nota_pdf(request, nota_id):
    nota = Nota.objects.get(id=nota_id)
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
        'pasos': pasos,
        'now': timezone.now()
    }

    template = get_template('myapp/pdf_template.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="nota_{nota.id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response


# Vista pública de prueba
def test(request):
    return render(request, 'myapp/test.html')

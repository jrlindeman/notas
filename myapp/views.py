import os
import re
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.template.loader import get_template
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from thefuzz import fuzz
from xhtml2pdf import pisa
from bs4 import BeautifulSoup

from .models import Nota, Paso, Categoria, NotaLibre
from .forms import NotaForm, PasoFormSet, NotaLibreForm


# Vista protegida: listado unificado (Notas + Notas Libres)
@login_required
def index(request):
    categoria_id = request.GET.get("categoria")

    notas = Nota.objects.all().order_by("-fecha_actualizacion").prefetch_related("pasos")
    notas_libres = NotaLibre.objects.all().order_by("-fecha_actualizacion")

    if categoria_id:
        notas = notas.filter(categoria_id=categoria_id)
        notas_libres = notas_libres.filter(categoria_id=categoria_id)

    notas_normalizadas = []
    for n in notas:
        notas_normalizadas.append({
            "id": n.id,
            "titulo": n.titulo,
            "descripcion": n.descripcion,
            "categoria": n.categoria,
            "fecha_actualizacion": n.fecha_actualizacion,
            "tipo": "nota",
        })

    for nl in notas_libres:
        notas_normalizadas.append({
            "id": nl.id,
            "titulo": nl.titulo,
            "descripcion": nl.contenido[:200],
            "categoria": nl.categoria,
            "fecha_actualizacion": nl.fecha_actualizacion,
            "tipo": "nota_libre",
        })

    notas_normalizadas.sort(key=lambda x: x["fecha_actualizacion"], reverse=True)

    return render(request, 'myapp/index.html', {"notas": notas_normalizadas})


# Vista protegida: perfil del usuario
@login_required
def perfil(request):
    return render(request, 'myapp/perfil.html', {"usuario": request.user})


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


# ✅ Vista protegida: notas por categoría (unificada)
@login_required
def notas_por_categoria(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug)

    notas = Nota.objects.filter(categoria=categoria).order_by("-fecha_actualizacion")
    notas_libres = NotaLibre.objects.filter(categoria=categoria).order_by("-fecha_actualizacion")

    notas_normalizadas = []
    for n in notas:
        notas_normalizadas.append({
            "id": n.id,
            "titulo": n.titulo,
            "descripcion": n.descripcion,
            "categoria": n.categoria,
            "fecha_actualizacion": n.fecha_actualizacion,
            "tipo": "nota",
        })
    for nl in notas_libres:
        notas_normalizadas.append({
            "id": nl.id,
            "titulo": nl.titulo,
            "descripcion": nl.contenido[:200],
            "categoria": nl.categoria,
            "fecha_actualizacion": nl.fecha_actualizacion,
            "tipo": "nota_libre",
        })

    notas_normalizadas.sort(key=lambda x: x["fecha_actualizacion"], reverse=True)

    return render(request, "myapp/index.html", {
        "notas": notas_normalizadas,
        "categoria": categoria
    })


# Vista protegida: buscador unificado
@login_required
def buscar_notas(request):
    query = request.GET.get("q", "").strip().lower()

    notas = Nota.objects.prefetch_related("pasos").all()
    notas_libres = NotaLibre.objects.all()

    resultados_normalizados = []

    if query:
        for nota in notas:
            texto = f"{nota.titulo or ''} {nota.descripcion or ''}"
            for paso in nota.pasos.all():
                texto += f" {paso.titulo or ''} {paso.descripcion or ''} {paso.codigo or ''}"
            similitud = fuzz.partial_ratio(query, texto.lower())
            if similitud >= 80:
                resultados_normalizados.append({
                    "id": nota.id,
                    "titulo": nota.titulo,
                    "descripcion": nota.descripcion,
                    "categoria": nota.categoria,
                    "fecha_actualizacion": nota.fecha_actualizacion,
                    "tipo": "nota",
                    "score": similitud
                })
        for nl in notas_libres:
            texto = f"{nl.titulo or ''} {nl.contenido or ''}"
            similitud = fuzz.partial_ratio(query, texto.lower())
            if similitud >= 80:
                resultados_normalizados.append({
                    "id": nl.id,
                    "titulo": nl.titulo,
                    "descripcion": nl.contenido[:200],
                    "categoria": nl.categoria,
                    "fecha_actualizacion": nl.fecha_actualizacion,
                    "tipo": "nota_libre",
                    "score": similitud
                })
        resultados_normalizados.sort(key=lambda x: (x["score"], x["fecha_actualizacion"]), reverse=True)
    else:
        for n in notas:
            resultados_normalizados.append({
                "id": n.id,
                "titulo": n.titulo,
                "descripcion": n.descripcion,
                "categoria": n.categoria,
                "fecha_actualizacion": n.fecha_actualizacion,
                "tipo": "nota",
            })
        for nl in notas_libres:
            resultados_normalizados.append({
                "id": nl.id,
                "titulo": nl.titulo,
                "descripcion": nl.contenido[:200],
                "categoria": nl.categoria,
                "fecha_actualizacion": nl.fecha_actualizacion,
                "tipo": "nota_libre",
            })
        resultados_normalizados.sort(key=lambda x: x["fecha_actualizacion"], reverse=True)

    return render(request, "myapp/index.html", {
        "notas": resultados_normalizados,
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

    context = {'nota': nota, 'pasos': pasos, 'now': timezone.now()}
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


# CRUD para Notas Libres
@login_required
def lista_notas_libres(request):
    notas = NotaLibre.objects.all().order_by("-fecha_actualizacion")
    return render(request, "myapp/notas_libres.html", {"notas": notas})

@login_required
def crear_nota_libre(request):
    if request.method == "POST":
        form = NotaLibreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("notas_libres")
    else:
        form = NotaLibreForm()
    return render(request, "myapp/crear_nota_libre.html", {"form": form})

@login_required
def editar_nota_libre(request, pk):
    nota = get_object_or_404(NotaLibre, pk=pk)
    if request.method == "POST":
        form = NotaLibreForm(request.POST, instance=nota)
        if form.is_valid():
            form.save()
            return redirect("notas_libres")
    else:
        form = NotaLibreForm(instance=nota)
    return render(request, "myapp/editar_nota_libre.html", {"form": form})

@login_required
def detalle_nota_libre(request, pk):
    nota_libre = get_object_or_404(NotaLibre, pk=pk)
    return render(request, "myapp/detalle_nota_libre.html", {"nota_libre": nota_libre})

@login_required
def eliminar_nota_libre(request, pk):
    nota = get_object_or_404(NotaLibre, pk=pk)
    if request.method == "POST":
        nota.delete()
        return redirect("notas_libres")
    return render(request, "myapp/eliminar_nota_libre.html", {"nota": nota})



@login_required
def exportar_nota_libre_pdf(request, pk):
    nota_libre = get_object_or_404(NotaLibre, pk=pk)
    template_path = 'myapp/pdf_template.html'
    contenido = nota_libre.contenido

    # Limpia el HTML con BeautifulSoup
    soup = BeautifulSoup(contenido, "html.parser")
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if src.startswith("/media/"):
            abs_path = os.path.join(settings.MEDIA_ROOT, src.replace('/media/', '').replace('/', os.sep))
            abs_path = abs_path.replace('\\', '/')  # Solo barras normales
            img.attrs = {}  # Elimina todos los atributos
            img['src'] = abs_path  # Sin 'file:///' y sin barras invertidas

    contenido_limpio = str(soup)
    context = {'nota_libre': nota_libre, 'contenido_pdf': contenido_limpio}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="nota_libre_{nota_libre.id}.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response
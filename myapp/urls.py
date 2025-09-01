from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from .views import (
    index, crear_nota, detalle_nota, editar_nota, eliminar_nota,
    exportar_nota_pdf, eliminar_paso, notas_por_categoria, buscar_notas, perfil
)
from myapp import views

urlpatterns = [
    # Página principal (requiere login)
    path('', index, name='inicio'),

    # Login personalizado
    path('login/', auth_views.LoginView.as_view(template_name='myapp/login.html'), name='login'),

    # Vista principal de notas
    path('notas/', index, name='index'),

    # CRUD de notas
    path('crear/', crear_nota, name='crear_nota'),
    path('nota/<int:nota_id>/', detalle_nota, name='detalle_nota'),
    path('nota/<int:nota_id>/editar/', editar_nota, name='editar_nota'),
    path('nota/<int:nota_id>/eliminar/', eliminar_nota, name='eliminar_nota'),
    path('nota/<int:nota_id>/exportar_pdf/', exportar_nota_pdf, name='exportar_nota_pdf'),

    # Gestión de pasos
    path('paso/<int:id>/eliminar/', eliminar_paso, name='eliminar_paso'),

    # Filtro por categoría
    path('categoria/<slug:slug>/', views.notas_por_categoria, name='notas_por_categoria'),

    # Buscador inteligente
    path('buscar/', buscar_notas, name='buscar_notas'),

    # Perfil del usuario
    path('perfil/', perfil, name='perfil'),

    # Sistema de autenticación completo
    path('accounts/', include('django.contrib.auth.urls')),

    # Redirección para compatibilidad con /accounts/login/
    path('accounts/login/', RedirectView.as_view(url='/login/', permanent=True)),

    #Exportar nota libre a PDF
    path('nota_libre/<int:pk>/exportar_pdf/', views.exportar_nota_libre_pdf, name='exportar_nota_libre_pdf'),
    
    #vistas de una nota libre sin pasos 
    path("notas-libres/", views.lista_notas_libres, name="notas_libres"),
    path("notas-libres/crear/", views.crear_nota_libre, name="crear_nota_libre"),
    path("notas-libres/<int:pk>/", views.detalle_nota_libre, name="detalle_nota_libre"),
    path("notas-libres/<int:pk>/editar/", views.editar_nota_libre, name="editar_nota_libre"),
    path("notas-libres/<int:pk>/eliminar/", views.eliminar_nota_libre, name="eliminar_nota_libre"),

    path("ckeditor/", include("ckeditor_uploader.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

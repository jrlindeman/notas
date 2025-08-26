from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('crear/', views.crear_nota, name='crear_nota'),
    path('nota/<int:nota_id>/', views.detalle_nota, name='detalle_nota'),
    path('nota/<int:nota_id>/editar/', views.editar_nota, name='editar_nota'),
    path('nota/<int:nota_id>/eliminar/', views.eliminar_nota, name='eliminar_nota'),
    path('paso/<int:id>/eliminar/', views.eliminar_paso, name='eliminar_paso'),
    path('categoria/<int:categoria_id>/', views.notas_por_categoria, name='notas_por_categoria'),
    path("buscar/", views.buscar_notas, name="buscar_notas"),
    path('accounts/', include('django.contrib.auth.urls')),  # Añade esta línea
]
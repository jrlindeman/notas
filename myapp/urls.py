from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('crear/', views.crear_nota, name='crear_nota'),
    path('nota/<int:nota_id>/', views.detalle_nota, name='detalle_nota'),
    path('nota/<int:nota_id>/editar/', views.editar_nota, name='editar_nota'),
    path('nota/<int:nota_id>/eliminar/', views.eliminar_nota, name='eliminar_nota'),
    path('paso/<int:id>/eliminar/', views.eliminar_paso, name='eliminar_paso'),
]


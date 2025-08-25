from django.db import models


class Categoria(models.Model):
    """
    Categoría a la que pertenece una nota.
    Ej: Trabajo, Estudio, Personal...
    """
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Nota(models.Model):
    """
    Una nota principal que puede tener varios pasos.
    """
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,   # Si se borra la categoría, la nota queda con categoria=None
        related_name="notas",
        blank=True,
        null=True
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_actualizacion", "-fecha_creacion"]

    def __str__(self):
        return self.titulo


class Paso(models.Model):
    """
    Paso perteneciente a una nota.
    Puede incluir título, descripción, código o imagen.
    """
    nota = models.ForeignKey(
        Nota,
        on_delete=models.CASCADE,
        related_name="pasos"  # acceso: nota.pasos.all()
    )
    titulo = models.CharField(max_length=200, blank=True)
    descripcion = models.TextField(blank=True, null=True)
    codigo = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to="pasos/", blank=True, null=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden", "id"]

    def __str__(self):
        if self.titulo:
            return f"{self.titulo} (Paso de {self.nota.titulo})"
        return f"Paso {self.id} de {self.nota.titulo}"

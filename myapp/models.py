from django.db import models
from django.utils.text import slugify


class Categoria(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nombre)
            slug = base_slug
            contador = 1
            while Categoria.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{contador}"
                contador += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre



class Nota(models.Model):
    """
    Nota principal que puede contener varios pasos.
    Cada nota pertenece opcionalmente a una categoría.
    """
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,   # si se elimina la categoría, la nota queda sin categoría
        null=True,
        blank=True,
        related_name="notas"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_actualizacion", "-fecha_creacion"]
        verbose_name = "Nota"
        verbose_name_plural = "Notas"

    def __str__(self):
        return f"{self.titulo} ({self.categoria.nombre if self.categoria else 'Sin categoría'})"


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
        verbose_name = "Paso"
        verbose_name_plural = "Pasos"

    def __str__(self):
        if self.titulo:
            return f"{self.titulo} (Paso de {self.nota.titulo})"
        return f"Paso {self.id} de {self.nota.titulo}"
    
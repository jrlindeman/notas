from django import forms
from django.forms import inlineformset_factory
from .models import Nota, Paso, Categoria


class NotaForm(forms.ModelForm):
    """
    Formulario para crear/editar Notas.
    Incluye un selector de categoría.
    """
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all().order_by("nombre"),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Categoría"
    )

    class Meta:
        model = Nota
        fields = ['titulo', 'descripcion', 'categoria']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class PasoForm(forms.ModelForm):
    """
    Formulario para crear/editar pasos de una Nota.
    Un paso es válido si al menos uno de sus campos está lleno,
    excepto si el paso está marcado para eliminarse.
    """
    class Meta:
        model = Paso
        fields = ['titulo', 'descripcion', 'codigo', 'imagen']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'codigo': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 4}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        titulo = cleaned_data.get("titulo")
        descripcion = cleaned_data.get("descripcion")
        codigo = cleaned_data.get("codigo")
        imagen = cleaned_data.get("imagen")

        # 👇 Si el formulario está marcado para eliminar, no validamos
        if self.cleaned_data.get("DELETE", False):
            return cleaned_data

        # Si todos los campos están vacíos, error
        if not any([titulo, descripcion, codigo, imagen]):
            raise forms.ValidationError(
                "Debe completar al menos un campo en el paso."
            )
        return cleaned_data


# Inline Formset para vincular Paso a Nota
PasoFormSet = inlineformset_factory(
    Nota,
    Paso,
    form=PasoForm,
    extra=1,          # al menos un paso vacío por defecto
    can_delete=True,  # permitir eliminar pasos en la edición
)

from django import template

register = template.Library()

def safe_as_widget(field, attrs):
    """Verifica que el campo tenga .as_widget antes de renderizar."""
    try:
        return field.as_widget(attrs=attrs)
    except AttributeError:
        return field  # Devuelve el valor original si no es un campo válido

@register.filter(name='add_class')
def add_class(field, css_class):
    """Agrega una clase CSS al campo del formulario."""
    return safe_as_widget(field, {"class": css_class})

@register.filter(name='add_placeholder')
def add_placeholder(field, text):
    """Agrega un placeholder al campo del formulario."""
    return safe_as_widget(field, {"placeholder": text})

@register.filter(name='add_data_attr')
def add_data_attr(field, attr_string):
    """Agrega un atributo data-* al campo del formulario."""
    if '=' not in attr_string:
        return field
    key, value = attr_string.split('=', 1)
    return safe_as_widget(field, {key: value})

@register.filter(name='add_attrs')
def add_attrs(field, attrs_string):
    """
    Agrega múltiples atributos al campo del formulario.
    Ejemplo: 'class=form-control,placeholder=Escribe aquí,data-lang=python'
    """
    attrs = {}
    for attr in attrs_string.split(','):
        if '=' in attr:
            key, value = attr.split('=', 1)
            attrs[key.strip()] = value.strip()
    return safe_as_widget(field, attrs)

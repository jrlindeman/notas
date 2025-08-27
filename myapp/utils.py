from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import logging

logger = logging.getLogger(__name__)

def render_to_pdf(template_path, context_dict):
    """
    Renderiza un template HTML a PDF usando xhtml2pdf.
    Retorna un HttpResponse con el PDF o None si hay error.
    """
    try:
        template = get_template(template_path)  # ← usa la ruta real: 'myapp/pdf_template.html'
        html = template.render(context_dict)
    except Exception as e:
        logger.error(f"Error al cargar/renderizar el template '{template_path}': {e}")
        return None

    result = BytesIO()
    pdf_status = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf_status.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    else:
        logger.error(f"Error al generar el PDF desde '{template_path}': {pdf_status.err}")
        return None
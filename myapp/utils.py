from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import logging
import re
from django.conf import settings
import os

logger = logging.getLogger(__name__)

def render_to_pdf(template_path, context_dict):
    """
    Renderiza un template HTML a PDF usando xhtml2pdf.
    Retorna un HttpResponse con el PDF o None si hay error.
    """
    try:
        template = get_template(template_path)  # ← usa la ruta real: 'myapp/pdf_template.html'
        html = template.render(context_dict)
        # Reemplaza rutas relativas de imágenes por rutas absolutas del sistema de archivos
        def replace_img_src(match):
            src = match.group(1)
            if src.startswith('/media/'):
                abs_path = os.path.join(settings.MEDIA_ROOT, src.replace('/media/', '').replace('/', os.sep))
                # En Windows, asegúrate de que las barras sean correctas
                abs_path = abs_path.replace('\\', '/')
                return f'src="file:///{abs_path}"'
            return f'src="{src}"'
        html = re.sub(r'src="([^"]+)"', replace_img_src, html)
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
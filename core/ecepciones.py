from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'success': False,
            'error': {
                'code':    response.status_code,
                'message': _flatten_errors(response.data),
            }
        }
        return response

    # Errores no manejados — loguear y devolver 500
    logger.exception('Error no controlado: %s', exc)
    return Response({
        'success': False,
        'error': {
            'code':    500,
            'message': 'Error interno del servidor. Contacte al administrador.',
        }
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _flatten_errors(data) -> str:
    if isinstance(data, str):
        return data
    if isinstance(data, list):
        return ' | '.join(str(e) for e in data)
    if isinstance(data, dict):
        return ' | '.join(f'{k}: {_flatten_errors(v)}' for k, v in data.items())
    return str(data)
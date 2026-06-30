# core/audit.py
from django.db import models


class AuditableMixin(models.Model):
    """
    Mixin que agrega campos de auditoría a cualquier modelo.
    Principio DRY: una sola definición para todos los modelos.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

import json
import logging
from django.utils.deprecation import MiddlewareMixin

audit_logger = logging.getLogger('hrms.audit')


class AuditMiddleware(MiddlewareMixin):
    """Registra todas las peticiones mutantes (POST, PUT, PATCH, DELETE)."""

    TRACKED_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}

    def process_response(self, request, response):
        if request.method not in self.TRACKED_METHODS:
            return response

        user = getattr(request, 'user', None)
        audit_logger.info(json.dumps({
            'user':      str(user.id) if user and user.is_authenticated else 'anon',
            'method':    request.method,
            'path':      request.path,
            'status':    response.status_code,
            'ip':        self._get_ip(request),
        }))
        return response

    def _get_ip(self, request) -> str:
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
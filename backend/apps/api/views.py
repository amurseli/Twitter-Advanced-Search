from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'ok', 'message': 'Backend is running'})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def debug_view(request):
    """Vista de debug para ver qué está pasando"""
    try:
        from django.conf import settings
        from django.db import connection
        
        # Test DB connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_ok = cursor.fetchone()[0] == 1
        
        return JsonResponse({
            'status': 'ok',
            'db_connection': db_ok,
            'debug': settings.DEBUG,
            'middleware': settings.MIDDLEWARE,
            'csrf_cookie_secure': settings.CSRF_COOKIE_SECURE,
            'allowed_hosts': settings.ALLOWED_HOSTS,
            'static_url': settings.STATIC_URL,
            'static_root': str(settings.STATIC_ROOT),
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'type': type(e).__name__
        }, status=500)

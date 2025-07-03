from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import XAccount, SearchTarget, ScrapingJob, Tweet
from .serializers import (
    XAccountSerializer, SearchTargetSerializer, 
    ScrapingJobSerializer, TweetSerializer
)
from .services.scraping_service import ScrapingService


class XAccountViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para listar cuentas X disponibles
    """
    serializer_class = XAccountSerializer
    permission_classes = [AllowAny]  # Por ahora sin auth
    
    def get_queryset(self):

        print("LLAMANDO A XACCOUNT VIEWSET")
        return XAccount.objects.filter(is_active=True)


class SearchTargetViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para listar usuarios objetivo
    """
    serializer_class = SearchTargetSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return SearchTarget.objects.filter(is_active=True)


class ScrapingJobViewSet(viewsets.ModelViewSet):
    """
    API endpoint para trabajos de scraping
    """
    serializer_class = ScrapingJobSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return ScrapingJob.objects.all().order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        print("=== DATOS RECIBIDOS ===")
        print(f"Data: {request.data}")
        print(f"Content-Type: {request.content_type}")
        
        # Validar con el serializer para ver el error específico
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(f"ERRORES DE VALIDACIÓN: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        # Por ahora usamos el primer usuario
        from django.contrib.auth.models import User
        user = User.objects.first()
        serializer.save(created_by=user)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Inicia un trabajo de scraping"""
        job = self.get_object()
        
        if job.status != 'pending':
            return Response(
                {'error': 'Job already started'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Ejecutar el scraping (en producción esto sería async con Celery)
        service = ScrapingService(job)
        service.run()
        
        # Recargar el job para obtener el estado actualizado
        job.refresh_from_db()
        serializer = self.get_serializer(job)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def tweets(self, request, pk=None):
        """Obtiene los tweets de un job"""
        job = self.get_object()
        tweets = job.tweets.all()
        
        # Paginación simple
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 50))
        
        start = (page - 1) * per_page
        end = start + per_page
        
        tweets_page = tweets[start:end]
        serializer = TweetSerializer(tweets_page, many=True)
        
        return Response({
            'count': tweets.count(),
            'page': page,
            'per_page': per_page,
            'results': serializer.data
        })


@login_required
def test_scraping(request):
    """Vista temporal para probar el scraping"""
    
    if request.method == 'POST':
        # Agarrar la primera cuenta X disponible
        account = XAccount.objects.filter(is_active=True).first()
        if not account:
            return HttpResponse("No hay cuentas X configuradas. Andá al admin y creá una.")
            
        # Agarrar algunos targets
        targets = SearchTarget.objects.filter(is_active=True)[:2]
        if not targets:
            return HttpResponse("No hay usuarios objetivo. Andá al admin y creá algunos.")
            
        # Crear un job de prueba con fechas del pasado
        from datetime import datetime
        
        # Últimos días de noviembre 2024
        job = ScrapingJob.objects.create(
            name="Test de scraping",
            account=account,
            start_date=datetime(2024, 11, 20, 0, 0, 0),
            end_date=datetime(2025, 3, 10, 23, 59, 59),
            query_type='from',
            created_by=request.user
        )
        job.targets.set(targets)
        
        # Ejecutar el scraping
        service = ScrapingService(job)
        service.run()
        
        return redirect('admin:scraping_scrapingjob_change', job.id)
        
    return render(request, 'scraping/test.html')
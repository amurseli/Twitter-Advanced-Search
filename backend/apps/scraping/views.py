from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, FileResponse
from django.conf import settings
import json
import os
from pathlib import Path

from .models import XAccount, SearchTarget, ScrapingJob, Tweet
from .serializers import (
    XAccountSerializer, SearchTargetSerializer, 
    ScrapingJobSerializer, TweetSerializer
)
from .services.scraping_service import ScrapingService


class XAccountViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = XAccountSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return XAccount.objects.filter(is_active=True)


class SearchTargetViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SearchTargetSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return SearchTarget.objects.filter(is_active=True)


class ScrapingJobViewSet(viewsets.ModelViewSet):
    serializer_class = ScrapingJobSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return ScrapingJob.objects.all().order_by('-created_at')
        
    def create(self, request, *args, **kwargs):
        print("\n=== DATOS RECIBIDOS ===")
        print(f"Method: {request.method}")
        print(f"Content-Type: {request.content_type}")
        print(f"Data type: {type(request.data)}")
        print(f"Raw data: {request.data}")
        
        try:
            if isinstance(request.data, str):
                data = json.loads(request.data)
            else:
                data = request.data
            print(f"Parsed data: {data}")
        except Exception as e:
            print(f"Error parsing data: {e}")
            data = request.data
        
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            print(f"\n=== ERRORES DE VALIDACIÓN ===")
            print(f"Errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"\n=== DATOS VALIDADOS ===")
        print(f"Validated data: {serializer.validated_data}")
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user = User.objects.first()
        if not user:
            user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        serializer.save(created_by=user)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        job = self.get_object()
        
        if job.status != 'pending':
            return Response(
                {'error': 'Job already started'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = ScrapingService(job)
        service.run()
        
        job.refresh_from_db()
        serializer = self.get_serializer(job)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def tweets(self, request, pk=None):
        job = self.get_object()
        tweets = job.tweets.all()
        
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
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        job = self.get_object()
        
        # Buscar el archivo JSON más reciente en la carpeta output
        output_dir = Path(settings.BASE_DIR) / 'output'
        
        if not output_dir.exists():
            return Response({'error': 'No output directory'}, status=404)
        
        # Buscar archivos que contengan los usuarios del job
        target_usernames = list(job.targets.values_list('username', flat=True))
        
        # Listar todos los archivos JSON
        json_files = list(output_dir.glob('*.json'))
        
        # Encontrar el archivo más reciente que coincida
        matching_file = None
        for file in sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True):
            file_content = file.read_text(encoding='utf-8')
            try:
                data = json.loads(file_content)
                # Verificar si es del job correcto
                if 'metadata' in data:
                    file_targets = data['metadata'].get('target_users', [])
                    if any(user in file_targets for user in target_usernames):
                        matching_file = file
                        break
            except:
                continue
        
        if not matching_file:
            return Response({'error': 'No file found for this job'}, status=404)
        
        # Devolver el archivo
        response = FileResponse(
            open(matching_file, 'rb'),
            as_attachment=True,
            filename=f'tweets_job_{job.id}_{job.created_at.strftime("%Y%m%d")}.json'
        )
        return response


@login_required
def test_scraping(request):
    if request.method == 'POST':
        account = XAccount.objects.filter(is_active=True).first()
        if not account:
            return HttpResponse("No hay cuentas X configuradas. Andá al admin y creá una.")
            
        targets = SearchTarget.objects.filter(is_active=True)[:2]
        if not targets:
            return HttpResponse("No hay usuarios objetivo. Andá al admin y creá algunos.")
            
        from datetime import datetime
        
        job = ScrapingJob.objects.create(
            name="Test de scraping",
            account=account,
            start_date=datetime(2024, 11, 20, 0, 0, 0),
            end_date=datetime(2025, 3, 10, 23, 59, 59),
            query_type='from',
            created_by=request.user
        )
        job.targets.set(targets)
        
        service = ScrapingService(job)
        service.run()
        
        return redirect('admin:scraping_scrapingjob_change', job.id)
        
    return render(request, 'scraping/test.html')
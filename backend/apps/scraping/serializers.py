from rest_framework import serializers
from .models import XAccount, SearchTarget, ScrapingJob, Tweet


class XAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = XAccount
        fields = ['id', 'username', 'is_active']


class SearchTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchTarget
        fields = ['id', 'username', 'display_name', 'is_active']


class ScrapingJobSerializer(serializers.ModelSerializer):
    account_username = serializers.CharField(source='account.username', read_only=True)
    targets_list = SearchTargetSerializer(source='targets', many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    target_usernames = serializers.ListField(
        child=serializers.CharField(), 
        write_only=True,
        required=False
    )
    
    class Meta:
        model = ScrapingJob
        fields = [
            'id', 'name', 'account', 'account_username', 'targets', 'targets_list',
            'target_usernames', 'start_date', 'end_date', 'query_type', 'status', 
            'status_display', 'tweets_count', 'created_at', 'error_message'
        ]
        read_only_fields = ['status', 'tweets_count', 'created_at', 'error_message']
    
    def create(self, validated_data):
        target_usernames = validated_data.pop('target_usernames', [])
        job = super().create(validated_data)
        
        # Crear o obtener SearchTargets
        targets = []
        for username in target_usernames:
            username = username.strip().replace('@', '')
            if username:
                target, created = SearchTarget.objects.get_or_create(
                    username=username,
                    defaults={'added_by': self.context['request'].user if self.context.get('request') else None}
                )
                targets.append(target)
        
        job.targets.set(targets)
        return job


class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = [
            'id', 'tweet_id', 'username', 'text', 'url', 'date',
            'reply_count', 'retweet_count', 'like_count', 'analytics_count',
            'is_quote', 'is_thread', 'is_rt'
        ]


# backend/apps/scraping/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

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


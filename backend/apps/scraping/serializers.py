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
    target_usernames = serializers.ListField(
        child=serializers.CharField(), 
        write_only=True,
        required=False
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    name = serializers.CharField(required=False, allow_blank=True)
    account = serializers.PrimaryKeyRelatedField(
        queryset=XAccount.objects.all(),
        required=False
    )
    
    class Meta:
        model = ScrapingJob
        fields = [
            'id', 'name', 'account', 'target_usernames', 
            'start_date', 'end_date', 'query_type', 'status', 
            'status_display', 'tweets_count', 'created_at', 'error_message'
        ]
        read_only_fields = ['status', 'status_display', 'tweets_count', 'created_at', 'error_message']
    
    def create(self, validated_data):
        target_usernames = validated_data.pop('target_usernames', [])
        
        if 'account' not in validated_data:
            try:
                validated_data['account'] = XAccount.objects.get(id=3)
            except XAccount.DoesNotExist:
                validated_data['account'] = XAccount.objects.filter(is_active=True).first()
                if not validated_data['account']:
                    raise serializers.ValidationError("No hay cuentas X activas disponibles")
        
        job = super().create(validated_data)
        
        targets = []
        for username in target_usernames:
            username = username.strip().replace('@', '')
            if username:
                target, created = SearchTarget.objects.get_or_create(
                    username=username,
                    defaults={'added_by': validated_data.get('created_by')}
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
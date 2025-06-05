from django.contrib import admin
from .models import XAccount, SearchTarget, ScrapingJob, Tweet


@admin.register(XAccount)
class XAccountAdmin(admin.ModelAdmin):
    """
    Para gestionar las cuentas de X desde el admin
    """
    list_display = ['username', 'email', 'is_active', 'last_login', 'owner']
    list_filter = ['is_active', 'last_login']
    search_fields = ['username', 'email']
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    
    # Ocultamos la contraseña en la lista por seguridad
    exclude = ['password'] if 'changelist' in admin.site.urls else []


@admin.register(SearchTarget) 
class SearchTargetAdmin(admin.ModelAdmin):
    """
    Los usuarios que queremos scrapear
    """
    list_display = ['username', 'display_name', 'is_active', 'added_by']
    list_filter = ['is_active']
    search_fields = ['username', 'display_name']
    readonly_fields = ['created_at']


@admin.register(ScrapingJob)
class ScrapingJobAdmin(admin.ModelAdmin):
    """
    Para ver y gestionar los trabajos de scraping
    """
    list_display = ['name', 'account', 'query_type', 'status', 
                    'tweets_count', 'created_by', 'created_at']
    list_filter = ['status', 'query_type', 'created_at']
    search_fields = ['name', 'error_message']
    readonly_fields = ['created_at', 'started_at', 'completed_at', 
                       'tweets_count', 'duration']
    
    # Agrupamos los campos en secciones
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'account', 'targets')
        }),
        ('Parámetros de búsqueda', {
            'fields': ('start_date', 'end_date', 'query_type')
        }),
        ('Estado y resultados', {
            'fields': ('status', 'tweets_count', 'error_message',
                      'started_at', 'completed_at', 'duration')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)  # Colapsado por defecto
        }),
    )
    
    def duration(self, obj):
        """Mostrar duración en el admin"""
        dur = obj.duration()
        return str(dur).split('.')[0] if dur else '-'
    duration.short_description = 'Duración'


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    """
    Para ver los tweets scrapeados
    """
    list_display = ['tweet_id', 'username', 'text_preview', 'date', 
                    'like_count', 'retweet_count', 'job']
    list_filter = ['date', 'is_rt', 'is_quote', 'is_thread', 'job']
    search_fields = ['text', 'username', 'tweet_id']
    readonly_fields = ['scraped_at', 'url']
    
    # Muchos tweets, paginamos de a 50
    list_per_page = 50
    
    def text_preview(self, obj):
        """Mostrar solo los primeros 60 caracteres del tweet"""
        return obj.text[:60] + '...' if obj.text and len(obj.text) > 60 else obj.text
    text_preview.short_description = 'Texto'
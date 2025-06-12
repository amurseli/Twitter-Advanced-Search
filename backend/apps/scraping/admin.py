from django.contrib import admin
from django.utils.html import format_html
from .models import XAccount, SearchTarget, ScrapingJob, Tweet


@admin.register(XAccount)
class XAccountAdmin(admin.ModelAdmin):
    """
    Para gestionar las cuentas de X desde el admin
    """
    list_display = ['username', 'email', 'is_active', 'last_login', 'has_cookies', 'owner']
    list_filter = ['is_active', 'last_login']
    search_fields = ['username', 'email']
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    
    def has_cookies(self, obj):
        """Indica si tiene cookies guardadas"""
        return '✅' if obj.cookies else '❌'
    has_cookies.short_description = 'Cookies'
    
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
    list_display = ['name', 'account', 'query_type', 'status_colored', 
                    'tweets_count', 'date_range', 'created_by', 'created_at']
    list_filter = ['status', 'query_type', 'created_at']
    search_fields = ['name', 'error_message']
    readonly_fields = ['created_at', 'started_at', 'completed_at', 
                       'tweets_count', 'duration', 'error_display']
    
    # Agrupamos los campos en secciones
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'account', 'targets')
        }),
        ('Parámetros de búsqueda', {
            'fields': ('start_date', 'end_date', 'query_type')
        }),
        ('Estado y resultados', {
            'fields': ('status', 'tweets_count', 'error_display',
                      'started_at', 'completed_at', 'duration')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)  # Colapsado por defecto
        }),
    )
    
    def status_colored(self, obj):
        """Mostrar estado con colores"""
        colors = {
            'pending': 'orange',
            'running': 'blue',
            'completed': 'green',
            'failed': 'red'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_colored.short_description = 'Estado'
    
    def date_range(self, obj):
        """Mostrar rango de fechas"""
        return f"{obj.start_date.date()} a {obj.end_date.date()}"
    date_range.short_description = 'Período'
    
    def error_display(self, obj):
        """Mostrar error con formato"""
        if obj.error_message:
            return format_html('<pre style="color: red;">{}</pre>', obj.error_message)
        return '-'
    error_display.short_description = 'Error'
    
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
                    'metrics_summary', 'job']
    list_filter = ['date', 'is_rt', 'is_quote', 'job']
    search_fields = ['text', 'username', 'tweet_id']
    readonly_fields = ['scraped_at', 'url', 'formatted_text']
    
    # Muchos tweets, paginamos de a 50
    list_per_page = 50
    
    # Ordenar por fecha descendente
    ordering = ['-date']
    
    def text_preview(self, obj):
        """Mostrar solo los primeros 60 caracteres del tweet"""
        return obj.text[:60] + '...' if obj.text and len(obj.text) > 60 else obj.text
    text_preview.short_description = 'Texto'
    
    def metrics_summary(self, obj):
        """Resumen de métricas"""
        return format_html(
            '❤️ {} 🔁 {} 💬 {}',
            obj.like_count,
            obj.retweet_count,
            obj.reply_count
        )
    metrics_summary.short_description = 'Métricas'
    
    def formatted_text(self, obj):
        """Texto completo con formato"""
        return format_html('<pre style="white-space: pre-wrap;">{}</pre>', obj.text)
    formatted_text.short_description = 'Texto completo'
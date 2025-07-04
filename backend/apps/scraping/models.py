from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class XAccount(models.Model):
    """
    Cuenta de Twitter para hacer scraping.
    """
    # El usuario de Django que es dueño de esta cuenta X
    owner = models.ForeignKey(User, on_delete=models.CASCADE, 
                            help_text="Quién agregó esta cuenta")
    
    # Credenciales de X
    username = models.CharField(max_length=100, unique=True,
                              help_text="Sin @, ej: nombreDeUsuario")
    password = models.CharField(max_length=255,
                              help_text="La vamos a encriptar después")
    email = models.EmailField(help_text="Email asociado a la cuenta X")
    
    # Estado de la cuenta
    is_active = models.BooleanField(default=True,
                                  help_text="Si está disponible para scrapear")
    cookies = models.JSONField(default=dict, blank=True,
                             help_text="Las cookies de sesión, como en states/")
    last_login = models.DateTimeField(null=True, blank=True,
                                    help_text="Última vez que se logueó")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cuenta X"
        verbose_name_plural = "Cuentas X"
        ordering = ['username']  
    
    def __str__(self):
        return f"@{self.username}"


class SearchTarget(models.Model):
    """
    Los usuarios que queremos scrapear.
    """
    username = models.CharField(max_length=100, unique=True,
                              help_text="Usuario a scrapear, sin @")
    display_name = models.CharField(max_length=255, blank=True,
                                  help_text="Nombre que muestra en el perfil")
    is_active = models.BooleanField(default=True,
                                  help_text="Si lo incluimos en búsquedas")
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Usuario objetivo"
        verbose_name_plural = "Usuarios objetivo"
        ordering = ['username']
    
    def __str__(self):
        return f"@{self.username}"


class ScrapingJob(models.Model):
    """
    Un trabajo de scraping.
    """
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('running', 'Ejecutando'), 
        ('completed', 'Completado'),
        ('failed', 'Falló'),
    ]
    
    QUERY_TYPE_CHOICES = [
        ('from', 'Tweets DE este usuario'),
        ('to', 'Tweets HACIA este usuario'),
        ('mentioning', 'Tweets que MENCIONAN al usuario'),
    ]
    
    # Configuración del job
    name = models.CharField(max_length=200, blank=True, default='',
                          help_text="Nombre descriptivo opcional")
    account = models.ForeignKey(XAccount, on_delete=models.CASCADE,
                              help_text="Con qué cuenta hacemos el scraping")
    targets = models.ManyToManyField(SearchTarget,
                                   help_text="A quiénes vamos a scrapear")
    
    start_date = models.DateTimeField(help_text="Desde cuándo buscar")
    end_date = models.DateTimeField(help_text="Hasta cuándo buscar")
    query_type = models.CharField(max_length=20, choices=QUERY_TYPE_CHOICES,
                                help_text="Tipo de búsqueda")
    
    # Estado y resultados
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                            default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True,
                                   help_text="Si falló, acá va el error")
    tweets_count = models.IntegerField(default=0,
                                     help_text="Cuántos tweets encontramos")
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Trabajo de scraping"
        verbose_name_plural = "Trabajos de scraping"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name or f"Job {self.id} - {self.get_query_type_display()}"
    
    def duration(self):
        """Cuánto tardó el scraping"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None


class Tweet(models.Model):
    """
    Un tweet scrapeado. 
    """
    # Relación con el job
    job = models.ForeignKey(ScrapingJob, on_delete=models.CASCADE,
                          related_name='tweets')
    
    # Datos del tweet (los mismos campos que tenías en el JSON)
    tweet_id = models.CharField(max_length=100, db_index=True)
    username = models.CharField(max_length=100, db_index=True)
    url = models.URLField(max_length=500)
    text = models.TextField(blank=True, null=True)
    
    # Multimedia
    image_url = models.URLField(max_length=500, blank=True, null=True)
    video_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Métricas
    date = models.DateTimeField(help_text="Cuándo se publicó el tweet")
    reply_count = models.IntegerField(default=0)
    retweet_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    analytics_count = models.IntegerField(default=0,
                                        help_text="Las views/impresiones")
    
    # Flags especiales
    is_quote = models.BooleanField(default=False)
    is_thread = models.BooleanField(default=False)
    is_rt = models.BooleanField(default=False)
    rt_by = models.CharField(max_length=100, blank=True, null=True,
                           help_text="Quién hizo el RT")
    
    # Metadata del scraping
    scraped_at = models.DateTimeField(auto_now_add=True)
    raw_data = models.JSONField(default=dict, blank=True,
                              help_text="El HTML crudo por si necesitamos algo más")
    
    class Meta:
        verbose_name = "Tweet"
        verbose_name_plural = "Tweets"
        ordering = ['-date']
        # No queremos duplicados del mismo tweet en el mismo job
        unique_together = ['job', 'tweet_id']
    
    def __str__(self):
        return f"@{self.username}: {self.text[:50]}..." if self.text else f"Tweet {self.tweet_id}"
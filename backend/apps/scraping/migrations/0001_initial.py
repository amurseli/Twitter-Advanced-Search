# Generated by Django 5.0.1 on 2025-06-05 20:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchTarget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(help_text='Usuario a scrapear, sin @', max_length=100, unique=True)),
                ('display_name', models.CharField(blank=True, help_text='Nombre que muestra en el perfil', max_length=255)),
                ('is_active', models.BooleanField(default=True, help_text='Si lo incluimos en búsquedas')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Usuario objetivo',
                'verbose_name_plural': 'Usuarios objetivo',
                'ordering': ['username'],
            },
        ),
        migrations.CreateModel(
            name='XAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(help_text='Sin @, ej: fantinofantino', max_length=100, unique=True)),
                ('password', models.CharField(help_text='La vamos a encriptar después', max_length=255)),
                ('email', models.EmailField(help_text='Email asociado a la cuenta X', max_length=254)),
                ('is_active', models.BooleanField(default=True, help_text='Si está disponible para scrapear')),
                ('cookies', models.JSONField(blank=True, default=dict, help_text='Las cookies de sesión, como en states/')),
                ('last_login', models.DateTimeField(blank=True, help_text='Última vez que se logueó', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(help_text='Quién agregó esta cuenta', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Cuenta X',
                'verbose_name_plural': 'Cuentas X',
            },
        ),
        migrations.CreateModel(
            name='ScrapingJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, help_text="Nombre descriptivo, ej: 'Tweets enero 2024'", max_length=200)),
                ('start_date', models.DateTimeField(help_text='Desde cuándo buscar')),
                ('end_date', models.DateTimeField(help_text='Hasta cuándo buscar')),
                ('query_type', models.CharField(choices=[('from', 'Tweets DE este usuario'), ('to', 'Tweets HACIA este usuario'), ('mentioning', 'Tweets que MENCIONAN al usuario')], help_text='Tipo de búsqueda', max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pendiente'), ('running', 'Ejecutando'), ('completed', 'Completado'), ('failed', 'Falló')], default='pending', max_length=20)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True, help_text='Si falló, acá va el error')),
                ('tweets_count', models.IntegerField(default=0, help_text='Cuántos tweets encontramos')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('targets', models.ManyToManyField(help_text='A quiénes vamos a scrapear', to='scraping.searchtarget')),
                ('account', models.ForeignKey(help_text='Con qué cuenta hacemos el scraping', on_delete=django.db.models.deletion.CASCADE, to='scraping.xaccount')),
            ],
            options={
                'verbose_name': 'Trabajo de scraping',
                'verbose_name_plural': 'Trabajos de scraping',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tweet_id', models.CharField(db_index=True, max_length=100)),
                ('username', models.CharField(db_index=True, max_length=100)),
                ('url', models.URLField(max_length=500)),
                ('text', models.TextField(blank=True, null=True)),
                ('image_url', models.URLField(blank=True, max_length=500, null=True)),
                ('video_url', models.URLField(blank=True, max_length=500, null=True)),
                ('date', models.DateTimeField(help_text='Cuándo se publicó el tweet')),
                ('reply_count', models.IntegerField(default=0)),
                ('retweet_count', models.IntegerField(default=0)),
                ('like_count', models.IntegerField(default=0)),
                ('analytics_count', models.IntegerField(default=0, help_text='Las views/impresiones')),
                ('is_quote', models.BooleanField(default=False)),
                ('is_thread', models.BooleanField(default=False)),
                ('is_rt', models.BooleanField(default=False)),
                ('rt_by', models.CharField(blank=True, help_text='Quién hizo el RT', max_length=100, null=True)),
                ('scraped_at', models.DateTimeField(auto_now_add=True)),
                ('raw_data', models.JSONField(blank=True, default=dict, help_text='El HTML crudo por si necesitamos algo más')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tweets', to='scraping.scrapingjob')),
            ],
            options={
                'verbose_name': 'Tweet',
                'verbose_name_plural': 'Tweets',
                'ordering': ['-date'],
                'unique_together': {('job', 'tweet_id')},
            },
        ),
    ]

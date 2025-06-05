import asyncio
from datetime import datetime
from asgiref.sync import sync_to_async

from django.utils import timezone

from ..models import ScrapingJob, Tweet
from .twitter_scraper import TweetScraper


class ScrapingService:
    """Conecta los modelos de Django con el scraper"""
    
    def __init__(self, job: ScrapingJob):
        self.job = job
        self.scraper = None
        
    def run(self):
        """Ejecuta el job de scraping"""
        self.job.status = 'running'
        self.job.started_at = timezone.now()
        self.job.save()
        
        try:
            asyncio.run(self._execute())
            self.job.status = 'completed'
        except Exception as e:
            self.job.status = 'failed'
            self.job.error_message = str(e)
        finally:
            self.job.completed_at = timezone.now()
            self.job.save()
            
    async def _execute(self):
        """Lógica principal asíncrona"""
        # Obtener datos de forma síncrona antes del contexto async
        account_data = await sync_to_async(self._get_account_data)()
        target_users = await sync_to_async(self._get_target_users)()
        
        # Inicializar scraper
        self.scraper = TweetScraper(
            username=account_data['username'],
            password=account_data['password']
        )
        
        try:
            await self.scraper.start_browser(headless=True)
            
            # Intentar usar cookies guardadas o hacer login
            if account_data['cookies']:
                await self.scraper.create_context(cookies=account_data['cookies'])
            else:
                await self.scraper.create_context()
                await self.scraper.login()
                
                # Guardar cookies para próxima vez
                cookies = await self.scraper.save_cookies()
                await sync_to_async(self._save_cookies)(cookies)
                
            # Ejecutar búsqueda
            tweets_data = await self.scraper.search_tweets(
                users=target_users,
                query_type=self.job.query_type,
                since_date=self.job.start_date.strftime('%Y-%m-%d'),
                until_date=self.job.end_date.strftime('%Y-%m-%d')
            )
            
            # Guardar tweets de forma síncrona
            await sync_to_async(self._save_tweets)(tweets_data)
            
        finally:
            await self.scraper.close_browser()
            
    def _get_account_data(self):
        """Obtiene datos de la cuenta (sync)"""
        return {
            'username': self.job.account.username,
            'password': self.job.account.password,
            'cookies': self.job.account.cookies
        }
    
    def _get_target_users(self):
        """Obtiene usuarios objetivo (sync)"""
        return list(self.job.targets.values_list('username', flat=True))
    
    def _save_cookies(self, cookies):
        """Guarda cookies en la cuenta (sync)"""
        self.job.account.cookies = cookies
        self.job.account.last_login = timezone.now()
        self.job.account.save()
            
    def _save_tweets(self, tweets_data: list):
        """Guarda los tweets en la base de datos (sync)"""
        tweets_to_create = []
        
        for data in tweets_data:
            # Parsear fecha
            tweet_date = datetime.fromisoformat(
                data['datetime'].replace('Z', '+00:00')
            )
            
            tweet = Tweet(
                job=self.job,
                tweet_id=data['tweet_id'],
                username=data['username'],
                url=data['url'],
                text=data['text'],
                date=tweet_date,
                reply_count=data['metrics']['replies'],
                retweet_count=data['metrics']['retweets'],
                like_count=data['metrics']['likes'],
                analytics_count=data['metrics']['views'],
                is_rt=data['is_retweet'],
                is_quote=data['is_quote'],
                image_url=data['url'] if data['has_image'] else None,
                video_url=data['url'] if data['has_video'] else None,
            )
            tweets_to_create.append(tweet)
            
        # Crear todos de una vez
        Tweet.objects.bulk_create(tweets_to_create, ignore_conflicts=True)
        
        # Actualizar contador
        self.job.tweets_count = len(tweets_to_create)
        self.job.save()
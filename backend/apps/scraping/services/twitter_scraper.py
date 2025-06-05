import os
import re
import asyncio
from datetime import datetime
from urllib.parse import urlencode
from typing import List, Dict

from playwright.async_api import async_playwright
from django.conf import settings


class TwitterScraper:
    """Maneja la conexión con Twitter/X usando Playwright"""
    
    base_url = "https://x.com/"
    
    def __init__(self, username: str, password: str = None):
        self.username = username
        self.password = password
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
    async def manual_pause(self, message: str = "Pausa"):
        """Para debugging - override en subclases"""
        pass
        
    async def start_browser(self, headless: bool = True):
        """Inicia Playwright y el navegador"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        
    async def close_browser(self):
        """Cierra todo limpiamente"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    async def create_context(self, cookies: dict = None):
        """Crea contexto del navegador con o sin cookies"""
        if cookies:
            self.context = await self.browser.new_context(storage_state=cookies)
        else:
            self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        
    async def save_cookies(self):
        """Guarda el estado actual (cookies, localStorage, etc)"""
        if self.context:
            return await self.context.storage_state()
        return None
        
    async def login(self):
        """Login en Twitter/X"""
        if not self.password:
            raise ValueError("Password requerido para login")
            
        print("🔐 Navegando a login...")
        await self.page.goto(f"{self.base_url}i/flow/login")
        await self.page.wait_for_timeout(2000)
        
        # Username
        print("📝 Ingresando username...")
        await self.page.fill('input[autocomplete="username"]', self.username)
        await self.page.keyboard.press('Enter')
        await self.page.wait_for_timeout(2000)
        
        # Password
        print("🔑 Ingresando password...")
        await self.page.fill('input[type="password"]', self.password)
        await self.page.keyboard.press('Enter')
        
        # Esperar más tiempo para captcha manual
        print("⏳ Esperando login (resolvé el captcha si aparece)...")
        await self.page.wait_for_timeout(10000)  # 10 segundos
        
        # Esperar hasta que aparezca el home
        try:
            await self.page.wait_for_selector('[data-testid="primaryColumn"]', timeout=30000)
            print("✅ Login exitoso!")
        except:
            # Si no aparece, esperar más
            print("⏳ Esperando un poco más...")
            await self.page.wait_for_timeout(5000)
            
        # Verificar que llegamos al home
        if "i/flow/login" in self.page.url:
            raise Exception("Login falló - verificá las credenciales")
            
        # Pausa opcional para verificar el login
        await self.manual_pause("Login completado. Verificá que estés en el home")
            
        return True


class TweetScraper(TwitterScraper):
    """Busca y extrae tweets"""
    
    def __init__(self, username: str, password: str = None, debug_mode: bool = False):
        super().__init__(username, password)
        self.tweets_data = []
        self.debug_mode = debug_mode
        
    async def manual_pause(self, message: str = "Pausa para debugging"):
        """Pausa manual para debugging"""
        if self.debug_mode:
            input(f"\n⏸️  {message}. Presioná Enter para continuar...\n")
        
    def build_search_url(self, users: List[str], query_type: str, 
                        since_date: str, until_date: str) -> str:
        """Arma la URL de búsqueda avanzada"""
        # Asegurar que los usuarios NO tengan @ al principio
        clean_users = [u.lstrip('@') for u in users]
        print(f"👥 Usuarios a buscar: {clean_users}")
        print(f"📅 Fecha: {since_date} hasta {until_date}")
        print(f"🔍 Tipo: {query_type}")
        
        # Construir query según el tipo
        if query_type == 'from':
            query_parts = [f"from:{user}" for user in clean_users]
            query = f"({' OR '.join(query_parts)})"
        elif query_type == 'to':
            query_parts = [f"to:{user}" for user in clean_users]
            query = f"({' OR '.join(query_parts)})"
        else:  # mentioning
            query_parts = [f"@{user}" for user in clean_users]
            query = f"({' OR '.join(query_parts)})"
            
        params = {
            "q": f"{query} until:{until_date} since:{since_date}",
            "src": "typed_query",
            "f": "live"
        }
        
        return f"{self.base_url}search?" + urlencode(params)
        
    async def search_tweets(self, users: List[str], query_type: str,
                           since_date: str, until_date: str):
        """Ejecuta búsqueda y extrae tweets"""
        url = self.build_search_url(users, query_type, since_date, until_date)
        print(f"🔍 Buscando en: {url}")
        
        await self.page.goto(url)
        await self.page.wait_for_timeout(5000)  # Más tiempo de espera
        
        # Pausa para verificar la búsqueda
        await self.manual_pause("Verificá que la búsqueda se cargó correctamente")
        
        # Verificar si hay resultados
        empty_state = await self.page.query_selector('[data-testid="empty_state_header_text"]')
        if empty_state:
            print("❌ No se encontraron tweets")
            return []
            
        print("✅ Página cargada, buscando tweets...")
        
        # Verificar si hay tweets
        initial_tweets = await self.page.query_selector_all('article[data-testid="tweet"]')
        print(f"📊 Tweets iniciales encontrados: {len(initial_tweets)}")
        
        # Scrollear y extraer tweets
        previous_height = 0
        max_empty_scrolls = 3
        empty_scrolls = 0
        
        while empty_scrolls < max_empty_scrolls:
            # Extraer tweets visibles
            await self._extract_visible_tweets()
            print(f"📈 Total tweets extraídos hasta ahora: {len(self.tweets_data)}")
            
            # Scrollear
            current_height = await self.page.evaluate("document.body.scrollHeight")
            if current_height == previous_height:
                empty_scrolls += 1
                print(f"⚠️ Sin nuevo contenido, intento {empty_scrolls}/{max_empty_scrolls}")
            else:
                empty_scrolls = 0
                
            previous_height = current_height
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self.page.wait_for_timeout(3000)  # Más tiempo entre scrolls
            
        print(f"✅ Búsqueda completada. Total tweets: {len(self.tweets_data)}")
        return self.tweets_data
        
    async def _extract_visible_tweets(self):
        """Extrae datos de los tweets visibles en pantalla"""
        tweets = await self.page.query_selector_all('article[data-testid="tweet"]')
        
        for tweet in tweets:
            try:
                data = await self._extract_tweet_data(tweet)
                if data and not self._is_duplicate(data['tweet_id']):
                    self.tweets_data.append(data)
            except Exception as e:
                # Seguir con el siguiente tweet
                continue
                
    async def _extract_tweet_data(self, tweet_element) -> Dict:
        """Extrae información de un tweet"""
        # Tweet ID desde el link
        link = await tweet_element.query_selector('a[href*="/status/"]')
        if not link:
            return None
            
        href = await link.get_attribute('href')
        tweet_id = href.split('/status/')[-1]
        
        # Username
        user_elem = await tweet_element.query_selector('[data-testid="User-Name"]')
        username_text = await user_elem.text_content() if user_elem else ""
        username_match = re.search(r'@(\w+)', username_text)
        username = username_match.group(1) if username_match else None
        
        if not username:
            return None
            
        # Fecha
        time_elem = await tweet_element.query_selector('time')
        datetime_str = await time_elem.get_attribute('datetime') if time_elem else None
        
        # Texto
        text_elem = await tweet_element.query_selector('[data-testid="tweetText"]')
        text = await text_elem.text_content() if text_elem else ""
        
        # Métricas
        metrics = await self._extract_metrics(tweet_element)
        
        # Multimedia
        has_image = await tweet_element.query_selector('img[src*="pbs.twimg.com/media"]') is not None
        has_video = await tweet_element.query_selector('video') is not None
        
        # Tipo de tweet
        is_retweet = await tweet_element.query_selector('span:has-text("Retweeted")') is not None
        is_quote = await tweet_element.query_selector('span:has-text("Quote")') is not None
        
        return {
            'tweet_id': tweet_id,
            'username': username,
            'text': text,
            'datetime': datetime_str,
            'metrics': metrics,
            'has_image': has_image,
            'has_video': has_video,
            'is_retweet': is_retweet,
            'is_quote': is_quote,
            'url': f"{self.base_url}{username}/status/{tweet_id}"
        }
        
    async def _extract_metrics(self, tweet_element) -> Dict[str, int]:
        """Extrae replies, retweets, likes"""
        metrics = {
            'replies': 0,
            'retweets': 0,
            'likes': 0,
            'views': 0
        }
        
        # Botones con métricas
        buttons = {
            'replies': '[data-testid="reply"]',
            'retweets': '[data-testid="retweet"]',
            'likes': '[data-testid="like"]'
        }
        
        for metric, selector in buttons.items():
            elem = await tweet_element.query_selector(selector)
            if elem:
                text = await elem.text_content()
                metrics[metric] = self._parse_metric_value(text)
                
        # Views (analytics)
        analytics = await tweet_element.query_selector('a[href*="/analytics"]')
        if analytics:
            text = await analytics.text_content()
            metrics['views'] = self._parse_metric_value(text)
            
        return metrics
        
    def _parse_metric_value(self, text: str) -> int:
        """Convierte '1.5K' a 1500, '2M' a 2000000, etc"""
        if not text:
            return 0
            
        text = text.strip()
        if text.endswith('K'):
            return int(float(text[:-1]) * 1000)
        elif text.endswith('M'):
            return int(float(text[:-1]) * 1000000)
        else:
            # Remover comas y convertir
            return int(text.replace(',', '') or 0)
            
    def _is_duplicate(self, tweet_id: str) -> bool:
        """Verifica si ya tenemos este tweet"""
        return any(t['tweet_id'] == tweet_id for t in self.tweets_data)
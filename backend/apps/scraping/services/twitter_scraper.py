import os
import re
import json
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
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        
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
        await self.page.wait_for_timeout(3000)
        
        # Username
        print("📝 Ingresando username...")
        await self.page.fill('input[autocomplete="username"]', self.username)
        await self.page.keyboard.press('Enter')
        await self.page.wait_for_timeout(3000)
        
        # Password
        print("🔑 Ingresando password...")
        await self.page.fill('input[type="password"]', self.password)
        await self.page.keyboard.press('Enter')
        
        # Esperar más tiempo para captcha manual
        print("⏳ Esperando login (resolvé el captcha si aparece)...")
        await self.page.wait_for_timeout(15000)  # 15 segundos
        
        # Verificar login exitoso
        try:
            await self.page.wait_for_selector('[data-testid="primaryColumn"]', timeout=30000)
            print("✅ Login exitoso!")
            
            # Verificar que realmente estamos logueados
            current_url = self.page.url
            if "i/flow/login" in current_url:
                raise Exception("Login falló - seguimos en la página de login")
                
        except Exception as e:
            print(f"❌ Error en login: {str(e)}")
            raise Exception(f"Login falló - verificá las credenciales")
            
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
        
        url = f"{self.base_url}search?" + urlencode(params)
        print(f"🔗 URL de búsqueda: {url}")
        return url
        
    async def search_tweets(self, users: List[str], query_type: str,
                           since_date: str, until_date: str):
        """Ejecuta búsqueda y extrae tweets"""
        self.tweets_data = []  # Limpiar datos anteriores
        
        url = self.build_search_url(users, query_type, since_date, until_date)
        print(f"🔍 Navegando a búsqueda...")
        
        await self.page.goto(url)
        await self.page.wait_for_timeout(8000)  # Más tiempo de espera inicial
        
        # Pausa para verificar la búsqueda
        await self.manual_pause("Verificá que la búsqueda se cargó correctamente")
        
        # Verificar si hay resultados
        empty_state = await self.page.query_selector('[data-testid="empty_state_header_text"]')
        if empty_state:
            empty_text = await empty_state.text_content()
            print(f"❌ No se encontraron tweets. Mensaje: {empty_text}")
            return []
            
        print("✅ Página cargada, buscando tweets...")
        
        # Verificar si hay tweets
        initial_tweets = await self.page.query_selector_all('article[data-testid="tweet"]')
        print(f"📊 Tweets iniciales encontrados: {len(initial_tweets)}")
        
        if len(initial_tweets) == 0:
            print("⚠️ No se encontraron tweets con el selector. Verificando página...")
            
            # Intentar con otros selectores
            articles = await self.page.query_selector_all('article')
            print(f"📄 Artículos encontrados: {len(articles)}")
            
            # Buscar cualquier elemento con data-testid
            test_elements = await self.page.query_selector_all('[data-testid]')
            print(f"🔍 Elementos con data-testid: {len(test_elements)}")
            
            # Imprimir algunos data-testid encontrados
            for i, elem in enumerate(test_elements[:10]):
                testid = await elem.get_attribute('data-testid')
                print(f"  - {testid}")
            
            # Verificar si estamos logueados
            login_prompt = await self.page.query_selector('[href="/login"]')
            if login_prompt:
                print("❌ No estás logueado! Redirigiendo a login...")
                raise Exception("Sesión no autenticada - se requiere login")
        
        # Scrollear y extraer tweets
        previous_height = 0
        max_empty_scrolls = 5
        empty_scrolls = 0
        scroll_count = 0
        
        while empty_scrolls < max_empty_scrolls:
            scroll_count += 1
            print(f"📜 Scroll #{scroll_count}")
            
            # Extraer tweets visibles
            new_tweets = await self._extract_visible_tweets()
            if new_tweets > 0:
                print(f"📈 Nuevos tweets extraídos: {new_tweets}. Total: {len(self.tweets_data)}")
            
            # Scrollear
            current_height = await self.page.evaluate("document.body.scrollHeight")
            if current_height == previous_height:
                empty_scrolls += 1
                print(f"⚠️ Sin nuevo contenido, intento {empty_scrolls}/{max_empty_scrolls}")
            else:
                empty_scrolls = 0
                
            previous_height = current_height
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self.page.wait_for_timeout(4000)  # Más tiempo entre scrolls
            
        print(f"✅ Búsqueda completada. Total tweets: {len(self.tweets_data)}")
        
        # Guardar resultados en JSON
        if self.tweets_data:
            self._save_to_json(users, query_type, since_date, until_date)
        
        return self.tweets_data
        
    def _save_to_json(self, users: List[str], query_type: str, 
                     since_date: str, until_date: str):
        """Guarda los tweets en un archivo JSON"""
        # Crear directorio de output si no existe
        output_dir = os.path.join(settings.BASE_DIR, 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        users_str = "_".join(users[:3])  # Primeros 3 usuarios
        filename = f"tweets_{users_str}_{query_type}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Estructura del JSON
        output = {
            "metadata": {
                "scraping_date": datetime.now().isoformat(),
                "target_users": users,
                "query_type": query_type,
                "date_range": {
                    "from": since_date,
                    "to": until_date
                },
                "total_tweets": len(self.tweets_data)
            },
            "tweets": self.tweets_data
        }
        
        # Guardar JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"💾 JSON guardado en: {filepath}")
        print(f"📊 Total tweets guardados: {len(self.tweets_data)}")
        
    async def _extract_visible_tweets(self):
        """Extrae datos de los tweets visibles en pantalla"""
        tweets = await self.page.query_selector_all('article[data-testid="tweet"]')
        new_tweets = 0
        
        for tweet in tweets:
            try:
                data = await self._extract_tweet_data(tweet)
                if data and not self._is_duplicate(data['tweet_id']):
                    self.tweets_data.append(data)
                    new_tweets += 1
                    print(f"  ✓ Tweet extraído: @{data['username']} - {data['tweet_id']}")
            except Exception as e:
                print(f"  ⚠️ Error extrayendo tweet: {str(e)}")
                continue
                
        return new_tweets
                
    async def _extract_tweet_data(self, tweet_element) -> Dict:
        """Extrae información de un tweet"""
        try:
            # Tweet ID desde el link
            link = await tweet_element.query_selector('a[href*="/status/"]')
            if not link:
                print("    - No se encontró link del tweet")
                return None
                
            href = await link.get_attribute('href')
            tweet_id = href.split('/status/')[-1].split('?')[0]  # Limpiar query params
            
            # Username
            user_elem = await tweet_element.query_selector('[data-testid="User-Name"]')
            username_text = await user_elem.text_content() if user_elem else ""
            username_match = re.search(r'@(\w+)', username_text)
            username = username_match.group(1) if username_match else None
            
            if not username:
                print("    - No se encontró username")
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
            is_quote = await tweet_element.query_selector('[data-testid="quoteTweet"]') is not None
            
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
        except Exception as e:
            print(f"    - Error procesando tweet: {str(e)}")
            return None
        
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
            try:
                return int(float(text[:-1]) * 1000)
            except:
                return 0
        elif text.endswith('M'):
            try:
                return int(float(text[:-1]) * 1000000)
            except:
                return 0
        else:
            # Remover comas y convertir
            try:
                return int(text.replace(',', '') or 0)
            except:
                return 0
            
    def _is_duplicate(self, tweet_id: str) -> bool:
        """Verifica si ya tenemos este tweet"""
        return any(t['tweet_id'] == tweet_id for t in self.tweets_data)
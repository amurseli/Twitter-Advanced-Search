from django.http import JsonResponse
import subprocess
import os

def test_playwright(request):
    """Test if Playwright is working correctly"""
    try:
        # Test basic imports
        from playwright.sync_api import sync_playwright
        
        # Test browser launch
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            page = browser.new_page()
            page.goto('https://example.com')
            title = page.title()
            browser.close()
            
        return JsonResponse({
            'status': 'success',
            'title': title,
            'playwright': 'working'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'type': type(e).__name__
        })

def check_environment(request):
    """Check environment setup"""
    try:
        # Check if Chrome is installed
        chrome_check = subprocess.run(['which', 'chromium'], capture_output=True, text=True)
        
        # Check environment variables
        env_vars = {
            'PLAYWRIGHT_BROWSERS_PATH': os.environ.get('PLAYWRIGHT_BROWSERS_PATH', 'Not set'),
            'DJANGO_SETTINGS_MODULE': os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set'),
        }
        
        return JsonResponse({
            'chrome_installed': bool(chrome_check.stdout),
            'chrome_path': chrome_check.stdout.strip(),
            'environment': env_vars
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})

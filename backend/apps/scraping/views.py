from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta

from .models import ScrapingJob, XAccount, SearchTarget
from .services.scraping_service import ScrapingService


@login_required
def test_scraping(request):
    """Vista temporal para probar el scraping"""
    
    if request.method == 'POST':
        # Agarrar la primera cuenta X disponible
        account = XAccount.objects.filter(is_active=True).first()
        if not account:
            return HttpResponse("No hay cuentas X configuradas. Andá al admin y creá una.")
            
        # Agarrar algunos targets
        targets = SearchTarget.objects.filter(is_active=True)[:2]
        if not targets:
            return HttpResponse("No hay usuarios objetivo. Andá al admin y creá algunos.")
            
        # Crear un job de prueba con fechas del pasado
        from datetime import datetime
        
        # Últimos días de noviembre 2024
        job = ScrapingJob.objects.create(
            name="Test de scraping",
            account=account,
            start_date=datetime(2024, 11, 20, 0, 0, 0),   # 20 nov 2024
            end_date=datetime(2024, 11, 30, 23, 59, 59),  # 30 nov 2024
            query_type='from',
            created_by=request.user
        )
        job.targets.set(targets)
        
        # Ejecutar el scraping
        service = ScrapingService(job)
        service.run()
        
        return redirect('admin:scraping_scrapingjob_change', job.id)
        
    return render(request, 'scraping/test.html')
from django.urls import path
from . import views
from .views_debug import test_playwright, check_environment

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('test-playwright/', test_playwright),
    path('check-env/', check_environment),



]

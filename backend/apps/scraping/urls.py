from django.urls import path
from . import views

app_name = 'scraping'

urlpatterns = [
    path('test/', views.test_scraping, name='test_scraping'),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'accounts', views.XAccountViewSet, basename='xaccount')
router.register(r'targets', views.SearchTargetViewSet, basename='searchtarget')
router.register(r'jobs', views.ScrapingJobViewSet, basename='scrapingjob')

app_name = 'scraping'

urlpatterns = [
    path('api/', include(router.urls)),
    path('test/', views.test_scraping, name='test_scraping'),
]

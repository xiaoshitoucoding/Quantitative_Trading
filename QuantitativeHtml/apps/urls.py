from django.urls import path
from django.conf import settings
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('IncreaseVolume', views.IncreaseVolume, name='IncreaseVolume'),
    path('BreakAndVolume', views.BreakAndVolume, name='BreakAndVolume'),
    path('StockShape', views.StockShape, name='StockShape'),
    path('IndustryInfo', views.IndustryInfo, name='IndustryInfo'),
    path('ChilliPepper', views.ChilliPepper, name='ChilliPepper'),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

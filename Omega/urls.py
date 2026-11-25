from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/core/', include('core.urls')),
    path('api/logistica/', include('logistica.urls')),
    path('api/compras/', include('compras.urls')),
    path('api/obras/', include('obras.urls')),
    path('api/reportes/', include('reportes.urls')),
]
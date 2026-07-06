from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cuenta/', include('django.contrib.auth.urls')),  # Login / Logout
    path('', include('gestion.urls')),                     # App principal
]

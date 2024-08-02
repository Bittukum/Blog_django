# blog/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('user.urls')),  # Correctly include the 'user' app's URLs
]

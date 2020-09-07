from django.urls import include, path
from . import views

# 用來串接callback主程式
urlpatterns = [
    path('callback/', views.callback),
]

# Use static() to add url mapping to serve static files during development (only)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

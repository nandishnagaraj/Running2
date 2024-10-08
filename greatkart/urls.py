"""
URL configuration for greatkart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('store/', include('store.urls')),
    path('cart/', include('carts.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
    path('privacy-policy/', TemplateView.as_view(template_name='privacy_policy.html'), name='privacy_policy'),
    path('termsofuse/', TemplateView.as_view(template_name='termsofuse.html'), name='termsofuse'),
    path('yourrunzone/', TemplateView.as_view(template_name='yourrunzone.html'), name='yourrunzone'),
    path('smitha/', TemplateView.as_view(template_name='smitha.html'), name='smitha'),
    path('pranesh/', TemplateView.as_view(template_name='pranesh.html'), name='pranesh'),
    path('nandish/', TemplateView.as_view(template_name='nandish.html'), name='nandish'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

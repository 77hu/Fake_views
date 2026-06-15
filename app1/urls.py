"""
URL configuration for Fake_views project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='login.html'), name='logout'),
    path('home/', views.home, name='home'),
    path('center/',views.center,name='center'),
    path('user_dashboard/',views.user_dashboard,name='user_dashboard'),
    # path('user_history/',views.user_history,name='user_history'),
    path('analysis/<int:analysis_id>/', views.analysis_detail, name='analysis_detail'),
    path('net/',views.net_graph,name='net'),
    path('heatmap/',views.heatmap_view,name='heatmap'),
    path('delete-analysis/<int:analysis_id>/', views.delete_analysis, name='delete_analysis'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

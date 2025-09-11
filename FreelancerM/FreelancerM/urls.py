"""
URL configuration for FreelancerM project.

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
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path("users/", include("users.urls")),
    path("jobs/", include("jobs.urls")),
    
      # API URLs
    path('api/', include('users.api_urls')),    # REST endpoints for users
    path('api/', include('jobs.api_urls')),     # REST endpoints for jobs
    #path('api/', include('proposals.api_urls')), # REST endpoints for proposals
    #path('api/', include('messaging.api_urls')), 

]

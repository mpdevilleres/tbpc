"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
#    url(r'^polls/', include('polls.urls')),
    url(r'^', include('main.urls')),
    url(r'^budget-mgt/', include('budget_mgt.urls')),
    url(r'^contract-mgt/', include('contract_mgt.urls')),
    url(r'^user-mgt/', include('user_mgt.urls')),
    url(r'^team-mgt/', include('team_mgt.urls')),
    url(r'^section-kpi-mgt/', include('section_kpi_mgt.urls')),

    url(r'^admin/', admin.site.urls),
]

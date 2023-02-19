"""exhauster URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from data_loader import views
from django.contrib import admin
from django.urls import path

from .swagger import schema_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("api/metrics", views.Metrics.as_view()),
    path("api/exhausters/<int:pk>", views.Exhausters.as_view()),
    path("api/exhausters", views.Exhausters.as_view()),
    path("api/machines", views.SinterMachines.as_view()),
    path("api/actual_indicators", views.ActualSystemIndicators.as_view()),
    path("api/historical_indicators", views.HistoricalSystemIndicator.as_view()),
]

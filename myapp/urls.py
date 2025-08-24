from django.urls import path
from . import views

urlpatterns = [
    # path('', views.home, name='home'),
    path('webhook/yaya/', views.webhook, name='yaya-webhook'),
]

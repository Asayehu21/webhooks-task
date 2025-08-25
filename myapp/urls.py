from django.urls import path
from . import views

urlpatterns = [
    
    path('webhook/yaya/', views.webhook, name='yaya-webhook'),
    # Endpoint to generate signature for testing
    path('webhook/yaya/generate-signature/', views.generate_signature_view, name='generate-signature'),
]

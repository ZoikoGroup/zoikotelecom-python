from django.urls import path
from .views import apply_reseller

urlpatterns = [
    path('apply/', apply_reseller, name='apply_reseller'),
]

from django.urls import path
from .views import ResellerFormAPIView

urlpatterns = [
    path(
        "submit/",
        ResellerFormAPIView.as_view(),
        name="reseller-form-submit"
    ),
]
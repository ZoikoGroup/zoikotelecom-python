from django.urls import path
from .views import ReviewListCreateView

urlpatterns = [
    path("reviews/", ReviewListCreateView.as_view(), name="product_reviews"),
]

from django.urls import path
from .views import (
    BusinessSolutionCreateAPIView,
    BusinessSolutionListAPIView,
)

urlpatterns = [
    path(
        "submit/",
        BusinessSolutionCreateAPIView.as_view(),
        name="business-solution-submit",
    ),
    path(
        "",
        BusinessSolutionListAPIView.as_view(),
        name="business-solution-list",
    ),
]
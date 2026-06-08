from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import BusinessSolution
from .serializers import (
    BusinessSolutionSerializer
)


class BusinessSolutionCreateAPIView(
    generics.CreateAPIView
):
    queryset = BusinessSolution.objects.all()
    serializer_class = BusinessSolutionSerializer
    permission_classes = [AllowAny]


class BusinessSolutionListAPIView(
    generics.ListAPIView
):
    queryset = BusinessSolution.objects.all()
    serializer_class = BusinessSolutionSerializer
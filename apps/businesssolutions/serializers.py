from rest_framework import serializers
from .models import BusinessSolution


class BusinessSolutionSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = BusinessSolution
        fields = "__all__"
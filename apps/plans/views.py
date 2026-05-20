from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Plan, PlanCategory
from .serializers import PlanSerializer

class PlanListView(APIView):
    """
    GET /api/v1/plans/
    Returns all active plans with their variations and category info.
    """

    def get(self, request):
        plans = (
            Plan.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related("variations")
            .order_by("sort_order", "name")
        )
        serializer = PlanSerializer(plans, many=True)
        return Response({
            "count": plans.count(),
            "results": serializer.data,
        })


class PlanByIdView(APIView):
    """
    GET /api/v1/plans/id/<int:pk>/
    Returns a single plan by its database primary key.
    """

    def get(self, request, pk):
        plan = get_object_or_404(
            Plan.objects.select_related("category").prefetch_related("variations"),
            pk=pk,
            is_active=True,
        )
        serializer = PlanSerializer(plan)
        return Response(serializer.data)


class PlanByBtPlanIdView(APIView):
    """
    GET /api/v1/plans/bt-id/<str:bt_plan_id>/
    Returns a single plan matched by BT Plan ID.
    """

    def get(self, request, bt_plan_id):
        plan = get_object_or_404(
            Plan.objects.select_related("category").prefetch_related("variations"),
            bt_plan_id=bt_plan_id,
            is_active=True,
        )
        serializer = PlanSerializer(plan)
        return Response(serializer.data)


class PlanByBtPlanNameView(APIView):
    """
    GET /api/v1/plans/bt-name/<str:bt_plan_name>/
    Returns plans matched by  BT Plan Name (case-insensitive).
    """

    def get(self, request, bt_plan_name):
        plans = (
            Plan.objects.filter(
                bt_plan_name__iexact=bt_plan_name,
                is_active=True,
            )
            .select_related("category")
            .prefetch_related("variations")
            .order_by("sort_order", "name")
        )

        if not plans.exists():
            return Response(
                {"detail": f"No plans found with  plan name '{bt_plan_name}'."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PlanSerializer(plans, many=True)
        return Response({
            "count": plans.count(),
            "results": serializer.data,
        })


class PlanByCategorySlugView(APIView):
    """
    GET /api/v1/plans/category/<str:slug>/
    Returns all active plans belonging to a specific category slug.
    """

    def get(self, request, slug):
        # Validate the category exists
        category = get_object_or_404(PlanCategory, slug=slug, is_active=True)

        plans = (
            Plan.objects.filter(category=category, is_active=True)
            .select_related("category")
            .prefetch_related("variations")
            .order_by("sort_order", "name")
        )

        serializer = PlanSerializer(plans, many=True)
        return Response({
            "category": {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
            },
            "count": plans.count(),
            "results": serializer.data,
        })

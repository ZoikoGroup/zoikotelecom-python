from django.db.models import Avg, Count
from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import ProductReview
from .serializers import ReviewReadSerializer, ReviewCreateSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/reviews/?product_id=7   (or ?product_slug=usb-c-cable)
         -> approved reviews + summary { count, average }
    POST /api/reviews/                -> create a review
    """
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        return ReviewCreateSerializer if self.request.method == "POST" else ReviewReadSerializer

    def get_queryset(self):
        qs = ProductReview.objects.filter(is_approved=True)
        pid = self.request.query_params.get("product_id")
        slug = self.request.query_params.get("product_slug")
        if pid:
            qs = qs.filter(product_id=pid)
        elif slug:
            qs = qs.filter(product_slug=slug)
        else:
            qs = qs.none()
        return qs

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        agg = qs.aggregate(count=Count("id"), average=Avg("rating"))
        return Response({
            "success": True,
            "count": agg["count"] or 0,
            "average": round(agg["average"], 1) if agg["average"] else 0,
            "results": ReviewReadSerializer(qs, many=True).data,
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "message": "Validation failed",
                             "errors": serializer.errors}, status=400)
        review = serializer.save()
        return Response({
            "success": True,
            "message": "Review submitted.",
            "data": ReviewReadSerializer(review).data,
        }, status=201)

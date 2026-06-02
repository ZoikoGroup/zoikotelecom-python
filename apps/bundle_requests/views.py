from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import BundleRequestSerializer
from django.core.mail import send_mail
from django.conf import settings
from .models import BundleRequest
import threading
import logging

logger = logging.getLogger(__name__)

def send_bundle_request_email(instance_id):
    """
    Runs in background thread so it doesn't block the API response.
    Fetch instance safely using ID.
    """
    try:
        instance = BundleRequest.objects.get(id=instance_id)

        send_mail(
            subject=f"New Bundle Request: {instance.bundle_name}",
            message=f"""New Bundle Request:

Name: {instance.name}
Email: {instance.email}
Phone: {instance.phone}

Bundle: {instance.bundle_name}
Price: {instance.bundle_price}
""",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )

        # Mark as sent ONLY after success
        instance.is_sent = True
        instance.save()


    except Exception as e:
        logger.error(f"Error sending bundle request email: {e}")


@api_view(['POST'])
def create_bundle_request(request):
    serializer = BundleRequestSerializer(data=request.data)

    if serializer.is_valid():
        instance = serializer.save()

        # Run email in background thread (safe version)
        threading.Thread(
            target=send_bundle_request_email,
            args=(instance.id,),
            daemon=True
        ).start()

        return Response(
            {"message": "Request saved successfully"},
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )
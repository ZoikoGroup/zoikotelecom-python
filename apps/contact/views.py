from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import ContactMessageSerializer
from django.core.mail import send_mail
from django.conf import settings
import threading  # Add this


def send_contact_email(instance):
    """Runs in background thread so it doesn't block the response."""
    try:
        send_mail(
            subject=f"New Contact: {instance.subject}",
            message=f"""
New Contact Form Submission:

Name: {instance.first_name} {instance.last_name}
Email: {instance.email}
Phone: {instance.phone}

Message:
{instance.message}
""",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        instance.is_sent = True
        instance.save()
    except Exception as e:
        print("Email error:", e)

@api_view(['POST'])
def contact_us(request):
    serializer = ContactMessageSerializer(data=request.data)

    if serializer.is_valid():
        instance = serializer.save()

        # Fire email in background — response returns immediately
        thread = threading.Thread(target=send_contact_email, args=(instance,))
        thread.daemon = True
        thread.start()

        return Response({
            "success": True,
            "message": "Thank you for contacting Golite. We will reach out soon."
        }, status=status.HTTP_201_CREATED)

    return Response({
        "success": False,
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

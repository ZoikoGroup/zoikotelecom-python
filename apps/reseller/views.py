from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .serializers import ResellerApplicationSerializer
from .models import ResellerApplication
import threading

def send_reseller_email(instance_id):
    """Sends reseller application details via email in a background thread."""
    try:
        instance = ResellerApplication.objects.get(id=instance_id)
        
        services_str = ", ".join(instance.services_of_interest) if instance.services_of_interest else "None selected"
        
        subject = f"New Reseller Application: {instance.company_name}"
        message = f"""
New Reseller Application Submitted:

COMPANY INFORMATION
Company Name: {instance.company_name}
Contact Name: {instance.contact_name}
Position: {instance.position or "N/A"}
Email Address: {instance.email}
Phone Number: {instance.phone}
Company Website: {instance.website or "N/A"}

BUSINESS ADDRESS
Address: {instance.address}
City: {instance.city}
Post Code: {instance.post_code}
Country: {instance.country}

SERVICES OF INTEREST
{services_str}

SIGNATURE / DECLARATION
I hereby declare that the information provided is true and accurate.
Full Name: {instance.full_name}
Digital Signature: {instance.digital_signature}
Date: {instance.signature_date}
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=["resellers@zoikotelecom.com", settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        
        instance.is_sent = True
        instance.save()
    except Exception as e:
        print("Reseller Email Error:", e)

@api_view(['POST'])
def apply_reseller(request):
    serializer = ResellerApplicationSerializer(data=request.data)
    
    if serializer.is_valid():
        instance = serializer.save()
        
        # Trigger background email task
        thread = threading.Thread(target=send_reseller_email, args=(instance.id,))
        thread.daemon = True
        thread.start()
        
        return Response({
            "success": True,
            "message": "Your reseller application has been submitted successfully."
        }, status=status.HTTP_201_CREATED)
        
    return Response({
        "success": False,
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Job
from .serializers import JobSerializer

@api_view(['GET'])

@permission_classes([])
def job_list_api(request):
    jobs = Job.objects.filter(status=True).order_by('-posted_at')
    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data)

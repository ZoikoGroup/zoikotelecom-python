from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

def home(request):
    return HttpResponse("Zoikotelecom Django API is running")

urlpatterns = [
    path('', home),  # 👈 ROOT URL
    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('api/blog/', include('apps.blog.api_urls', namespace='blog_api')),
    path('api/', include('apps.bundle_requests.urls')),
    path('api/products/', include('apps.products.api_urls', namespace='products_api')),
    path("api/v1/plans/", include("apps.plans.urls", namespace="plans")),
    path('api/accounts/', include('apps.accounts.urls')),
    path("api/v1/order/", include("apps.orders.urls")),

    path("api/v1/", include("apps.coupons.api_urls")),
    path('api/contact/', include('apps.contact.urls')),
    path('api/newsletter/', include('apps.newsletter.urls')),
    path('jobs/', include('apps.jobs.urls')),

    path('search/', include('apps.search.urls')),
    path('business-solutions/', include('apps.businesssolutions.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

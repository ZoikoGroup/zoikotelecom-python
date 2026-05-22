from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.db.models import Q
from django.utils.text import slugify

# MODELS
from apps.plans.models import Plan
from apps.products.models import Product
from apps.blog.models import BlogPost
from apps.jobs.models import Job


@api_view(['GET'])
@permission_classes([AllowAny])
def global_search(request):
    """
    Global Search API

    Endpoint:
    /api/search?key=iphone 15

    Searches in:
    - Plans
    - Products
    - Blogs
    - Jobs
    """

    key = request.GET.get("key", "").strip()

    if not key:
        return Response({
            "status": False,
            "message": "Search key required",
            "count": 0,
            "data": []
        })


    keywords = key.split()

    results = []



    # ====================================================
    # PLAN SEARCH
    # ====================================================

    plan_query = Q()

    for word in keywords:

        plan_query |= Q(name__icontains=word)
        plan_query |= Q(slug__icontains=word)

        # optional if exists
        if hasattr(Plan, "description"):
            plan_query |= Q(description__icontains=word)


    plans = Plan.objects.filter(plan_query).select_related("category").distinct()[:10]


    for plan in plans:

        results.append({

            "type": "plan",

            "title": plan.name,

            "slug": plan.slug,

            "category": plan.category.name if plan.category else None,

            "category_slug": plan.category.slug if plan.category else None,

        })




    # ====================================================
    # PRODUCT SEARCH
    # ====================================================

    product_query = Q()

    for word in keywords:

        product_query |= Q(name__icontains=word)
        product_query |= Q(slug__icontains=word)

        if hasattr(Product, "description"):
            product_query |= Q(description__icontains=word)


    products = Product.objects.filter(product_query).select_related("category").distinct()[:10]


    for product in products:

        results.append({

            "type": "product",

            "title": product.name,

            "slug": product.slug,

            "category": product.category.name if product.category else None,

            "category_slug": product.category.slug if product.category else None,

        })




    # ====================================================
    # BLOG SEARCH
    # ====================================================

    blog_query = Q()

    for word in keywords:

        blog_query |= Q(title__icontains=word)
        blog_query |= Q(slug__icontains=word)

        if hasattr(BlogPost, "content"):
            blog_query |= Q(content__icontains=word)


    blogs = BlogPost.objects.filter(blog_query).distinct()[:10]


    for blog in blogs:

        results.append({

            "type": "blog",

            "title": blog.title,

            "slug": blog.slug,

            "category": None,

            "category_slug": None,

        })




    # ====================================================
    # JOB SEARCH
    # ====================================================

    job_query = Q()

    for word in keywords:

        job_query |= Q(title__icontains=word)

        if hasattr(Job, "description"):
            job_query |= Q(description__icontains=word)


    jobs = Job.objects.filter(job_query).distinct()[:10]


    for job in jobs:

        results.append({

            "type": "job",

            "title": job.title,

            "slug": slugify(job.title),

            "category": None,

            "category_slug": None,

        })





    return Response({

        "status": True,

        "message": "Search result",

        "count": len(results),

        "data": results

    })
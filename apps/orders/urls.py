"""
URL routes for bqorders.

Wire into the project's root urls.py with:

    from django.urls import path, include
    urlpatterns += [
        path("api/v1/", include("apps.orders.urls")),
    ]
"""

from django.urls import path

from .views import (
    BTOrderCreateView,
    BTOrderRetrieveView,
    BTOrderWebhookView,
    MyOrdersView,
)

app_name = "orders"

urlpatterns = [
    # POST  /api/v1/bqorders/                  → create
    path("bqorders/",                         BTOrderCreateView.as_view(),   name="bqorders-create"),

    # POST  /api/v1/bqorders/webhook/          → BT API 8 notifications
    # Declared BEFORE the <external_id> pattern so "webhook" is never captured.
    path("bqorders/webhook/",                 BTOrderWebhookView.as_view(),  name="bqorders-webhook"),

    # GET   /api/v1/my-orders/                 → logged-in user's orders (all types)
    path("my-orders/",                        MyOrdersView.as_view(),        name="my-orders"),


    # GET   /api/v1/bqorders/<external_id>/    → retrieve
    path("bqorders/<str:external_id>/",       BTOrderRetrieveView.as_view(), name="bqorders-detail"),
]
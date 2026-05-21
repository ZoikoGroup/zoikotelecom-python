from django.urls import path
from .views import (
    PlanListView,
    PlanByIdView,
    PlanByBtPlanIdView,
    PlanByBtPlanNameView,
    PlanByCategorySlugView,
)


app_name = "plans"


urlpatterns = [
    # GET /api/v1/plans/                          → all plans
    path("", PlanListView.as_view(), name="plan-list"),

    # GET /api/v1/plans/id/<pk>/                  → by database ID
    path("id/<int:pk>/", PlanByIdView.as_view(), name="plan-by-id"),

    # GET /api/v1/plans/bt-id/<bt_plan_id>/       → by BT Plan ID
    path("bt-id/<str:bt_plan_id>/", PlanByBtPlanIdView.as_view(), name="plan-by-bt-id"),

    # GET /api/v1/plans/bt-name/<bt_plan_name>/   → by  BT Plan Name
    path("bt-name/<str:bt_plan_name>/", PlanByBtPlanNameView.as_view(), name="plan-by-bt-name"),

    # GET /api/v1/plans/category/<slug>/          → all plans in a category
    path("category/<slug:slug>/", PlanByCategorySlugView.as_view(), name="plan-by-category"),
]

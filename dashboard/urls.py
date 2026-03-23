from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),
    path("orders/", views.order_list, name="order_list"),
    path("reviews/", views.review_list, name="review_list"),   # <-- this must exist
    path("analytics/", views.analytics_dashboard, name="analytics_dashboard"),
    path("api/sales-data/", views.sales_data_api, name="sales_data_api"),
    path("api/review-data/", views.review_data_api, name="review_data_api"),
    path("reviews/delete/<int:review_id>/", views.delete_review, name="delete_review"),
    path("reviews/edit/<int:review_id>/", views.edit_review, name="edit_review"),
    path("orders/update/<int:order_id>/", views.update_order_status, name="update_order_status"),
    path("orders/<int:order_id>/bill/", views.generate_bill, name="dashboard_generate_bill"),
    path("api/favorite-data/", views.favorite_data_api, name="favorite_data_api"),


    ]



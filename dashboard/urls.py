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

    # Catalog Management
    path("categories/", views.category_list, name="dashboard_category_list"),
    path("categories/create/", views.category_create, name="dashboard_category_create"),
    path("categories/<int:pk>/edit/", views.category_update, name="dashboard_category_edit"),
    path("categories/<int:pk>/delete/", views.category_delete, name="dashboard_category_delete"),

    path("products/", views.product_list, name="dashboard_product_list"),
    path("products/create/", views.product_create, name="dashboard_product_create"),
    path("products/<int:pk>/edit/", views.product_update, name="dashboard_product_edit"),
    path("products/<int:pk>/delete/", views.product_delete, name="dashboard_product_delete"),

    # User Interactions
    path("feedbacks/", views.feedback_list, name="dashboard_feedback_list"),
    path("feedbacks/<int:pk>/delete/", views.feedback_delete, name="dashboard_feedback_delete"),
]

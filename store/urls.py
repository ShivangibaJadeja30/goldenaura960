from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", views.home, name="home"),
    # store/urls.py
    path("products/", views.product_list, name="product_list"),
    path("products/<int:category_id>/", views.product_list_by_category, name="product_list_by_category"),   
    path("cart/", views.cart, name="cart"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.order_history, name="order_history"),
    path("account/", views.login_signup, name="login_signup"),
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),
    path("contact/", views.contact, name="contact"), 
]

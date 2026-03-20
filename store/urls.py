from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.home, name="home"),
    # store/urls.py
    path("products/", views.product_list, name="product_list"),
    path("products/<int:category_id>/", views.product_list_by_category, name="product_list_by_category"),   
    path("cart/", views.cart, name="cart"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:cart_id>/<str:action>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:cart_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.order_history, name="order_history"),
    path("account/", views.login_signup, name="login_signup"),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path("contact/", views.contact, name="contact"),
    path('profile/', views.profile, name='profile'),
    path('search/', views.search_results, name='search_results'),
    path("favorites/", views.favorites_list, name="favorites_list"),
    path("favorites/add/<int:product_id>/", views.add_to_favorites, name="add_to_favorites"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    path("product/<int:product_id>/review/", views.add_review, name="add_review"),
    path("login/", views.login_signup, name="login"),
]

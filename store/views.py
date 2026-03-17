from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings

from .models import Category, Product, Cart, Order
from .forms import SignupForm, FeedbackForm

def home(request):
    categories = Category.objects.all()
    return render(request, "store/home.html", {"categories": categories})

# store/views.py
from django.shortcuts import render, get_object_or_404
from .models import Category, Product

def product_list(request):
    # Show all products
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, "store/product_list.html", {
        "products": products,
        "categories": categories,
        "selected_category": None
    })

def product_list_by_category(request, category_id):
    # Show products only from one category
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    return render(request, "store/product_list.html", {
        "products": products,
        "categories": categories,
        "selected_category": category
    })



def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
        )
        if not created:
            cart_item.quantity += 1
            cart_item.save()
    return redirect("cart")

def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, "store/cart.html", {"cart_items": cart_items, "total": total})

def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if request.method == "POST":
        order = Order.objects.create(
            user=request.user,
            payment_method="COD",
            status="Pending"
        )
        order.products.set(cart_items)
        cart_items.delete()
        return render(request, "store/order_success.html", {"order": order})
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, "store/checkout.html", {"cart_items": cart_items, "total": total})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "store/order_history.html", {"orders": orders})

def login_signup(request):
    login_form = AuthenticationForm()
    signup_form = SignupForm()

    if request.method == "POST":
        if "login" in request.POST:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect("home")
        elif "signup" in request.POST:
            signup_form = SignupForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)
                return redirect("home")

    return render(request, "store/login_signup.html", {
        "login_form": login_form,
        "signup_form": signup_form
    })

def contact(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            if request.user.is_authenticated:
                feedback.user = request.user
            feedback.save()
            # Optional email notification
            send_mail(
                "New Feedback Received",
                feedback.message,
                settings.DEFAULT_FROM_EMAIL,
                ["admin@example.com"],
            )
            return render(request, "store/contact_success.html")
    else:
        form = FeedbackForm()
    return render(request, "store/contact.html", {"form": form})

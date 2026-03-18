from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings

from .models import Category, Product, Cart, Order
from .forms import SignupForm, FeedbackForm

# store/views.py
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from .models import UserProfile

from django.shortcuts import render
from .models import Product

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserForm, UserProfileForm

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("profile")  # after saving, go back to view mode
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

    # Check if user clicked "edit"
    edit_mode = request.GET.get("edit") == "true"

    return render(request, "store/profile.html", {
        "user_form": user_form,
        "profile_form": profile_form,
        "profile": profile,
        "edit_mode": edit_mode
    })

def search_results(request):
    query = request.GET.get('q')
    results = Product.objects.filter(name__icontains=query)
    return render(request, 'store/search_results.html', {'query': query, 'results': results})


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

from django.shortcuts import render, get_object_or_404
from .models import Category, Product

def product_list_by_category(request, category_id):
    # Get the selected category
    category = get_object_or_404(Category, id=category_id)
    # Get products in that category, sorted by name
    products = Product.objects.filter(category=category).order_by("name")
    # Get all categories for sidebar/menu
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
    for item in cart_items:
        item.subtotal = item.product.price * item.quantity
    total = sum(item.subtotal for item in cart_items)
    return render(request, "store/cart.html", {
        "cart_items": cart_items,
        "total": total
    })

def update_cart(request, cart_id, action):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    if action == "increase":
        cart_item.quantity += 1
    elif action == "decrease" and cart_item.quantity > 1:
        cart_item.quantity -= 1
    cart_item.save()
    return redirect("cart")

def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    return redirect("cart")


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

import razorpay
from django.conf import settings

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)

    # Build UPI deep link dynamically
    upi_id = "shivangiba@oksbi"   # replace with your real UPI ID
    payee_name = "GoldenAura960"
    upi_link = f"upi://pay?pa={upi_id}&pn={payee_name}&am={total}&cu=INR"

    if request.method == "POST":
        # User confirms payment manually
        order = Order.objects.create(
            user=request.user,
            payment_method="UPI (Manual)",
            status="Pending"  # mark Paid after verifying
        )
        order.products.set(cart_items)
        cart_items.delete()
        return render(request, "store/order_success.html", {"order": order})

    return render(request, "store/checkout.html", {
        "cart_items": cart_items,
        "total": total,
        "upi_link": upi_link
    })









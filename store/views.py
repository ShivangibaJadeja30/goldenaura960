from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings

from .models import Category, Product, Cart, Order, UserProfile, Favorite, Review
from .forms import SignupForm, FeedbackForm, UserForm, UserProfileForm

# ------------------ User Profile ------------------
@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("profile")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

    edit_mode = request.GET.get("edit") == "true"
    return render(request, "store/profile.html", {
        "user_form": user_form,
        "profile_form": profile_form,
        "profile": profile,
        "edit_mode": edit_mode
    })

# ------------------ Search ------------------
def search_results(request):
    query = request.GET.get('q', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    category_id = request.GET.get('category')

    results = Product.objects.all()

    if query:
        results = results.filter(name__icontains=query)

    if min_price:
        try:
            results = results.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            results = results.filter(price__lte=float(max_price))
        except ValueError:
            pass

    if category_id:
        try:
            results = results.filter(category_id=int(category_id))
        except ValueError:
            pass

    categories = Category.objects.all()

    return render(request, 'store/search_results.html', {
        'query': query,
        'results': results,
        'categories': categories,
        'min_price': min_price,
        'max_price': max_price,
        'selected_category': category_id
    })

# ------------------ Home ------------------
def home(request):
    categories = Category.objects.all()
    return render(request, "store/home.html", {"categories": categories})

# ------------------ Products ------------------
def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, "store/product_list.html", {
        "products": products,
        "categories": categories,
        "selected_category": None
    })

def product_list_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category).order_by("name")
    categories = Category.objects.all()
    return render(request, "store/product_list.html", {
        "products": products,
        "categories": categories,
        "selected_category": category
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "store/product_detail.html", {"product": product})

# ------------------ Cart ------------------
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect("cart")

@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    for item in cart_items:
        item.subtotal = item.product.price * item.quantity
    total = sum(item.subtotal for item in cart_items)
    return render(request, "store/cart.html", {"cart_items": cart_items, "total": total})

@login_required
def update_cart(request, cart_id, action):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    if action == "increase":
        cart_item.quantity += 1
    elif action == "decrease" and cart_item.quantity > 1:
        cart_item.quantity -= 1
    cart_item.save()
    return redirect("cart")

@login_required
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    return redirect("cart")

# ------------------ Checkout ------------------
@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)

    upi_id = "shivangiba@oksbi"   # replace with your real UPI ID
    payee_name = "GoldenAura960"
    upi_link = f"upi://pay?pa={upi_id}&pn={payee_name}&am={total}&cu=INR"

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user,
            payment_method="UPI (Manual)",
            status="Pending"
        )
        order.products.set(cart_items.values_list("product", flat=True))
        cart_items.delete()
        return render(request, "store/order_success.html", {"order": order})

    return render(request, "store/checkout.html", {
        "cart_items": cart_items,
        "total": total,
        "upi_link": upi_link
    })

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "store/order_history.html", {"orders": orders})

@login_required
def generate_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # Calculate total and prepare items if needed
    total = sum(product.price for product in order.products.all())
    return render(request, "store/invoice.html", {"order": order, "total": total})


# ------------------ Auth ------------------
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

# ------------------ Contact ------------------
def contact(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            if request.user.is_authenticated:
                feedback.user = request.user
            feedback.save()
            try:
                send_mail(
                    "New Feedback Received",
                    feedback.message,
                    settings.DEFAULT_FROM_EMAIL,
                    ["admin@example.com"],
                    fail_silently=True,
                )
            except Exception:
                pass
            return render(request, "store/contact_success.html")
    else:
        form = FeedbackForm()
    return render(request, "store/contact.html", {"form": form})

# ------------------ Favorites ------------------
@login_required
def add_to_favorites(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Favorite.objects.get_or_create(user=request.user, product=product)
    return redirect("favorites_list")

@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, "store/favorites.html", {"favorites": favorites})

# ------------------ Reviews ------------------
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if rating and comment:
            existing_review = Review.objects.filter(product=product, user=request.user).first()
            if existing_review:
                existing_review.rating = rating
                existing_review.comment = comment
                existing_review.save()
            else:
                Review.objects.create(product=product, user=request.user, rating=rating, comment=comment)

        return redirect("product_detail", product_id=product.id)

    return redirect("product_detail", product_id=product.id)

# ------------------ Order Tracking ------------------
def track_order(request):
    order = None
    error = None
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                error = "Order not found. Please check your Order ID."
            except ValueError:
                error = "Invalid Order ID format."

    return render(request, "store/track_order.html", {"order": order, "error": error})

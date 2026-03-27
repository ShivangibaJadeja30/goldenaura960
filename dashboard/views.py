from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count, Sum
from store.models import Order, Review, Favorite
from django.contrib.auth.models import User
import json
from django.core.serializers.json import DjangoJSONEncoder

@login_required
def dashboard_home(request):
    # Calculate revenue manually to avoid ManyToMany aggregate join quirks
    total_revenue = sum(
        sum(product.price for product in order.products.all())
        for order in Order.objects.exclude(status="Cancelled")
    )
    
    stats = {
        "total_orders": Order.objects.count(),
        "total_revenue": total_revenue,
        "total_reviews": Review.objects.count(),
    }

    # ... rest of your analytics code ...


    # Sales data
    sales_data = (
        Order.objects.values("created_at__date")
        .annotate(count=Count("id"))
        .order_by("created_at__date")
    )
    sales_json = json.dumps(list(sales_data), cls=DjangoJSONEncoder)

    # Review data
    review_data = (
        Review.objects.values("product__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    review_json = json.dumps(list(review_data), cls=DjangoJSONEncoder)

    # Favorites data
    favorite_data = (
        Favorite.objects.values("product__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    favorite_json = json.dumps(list(favorite_data), cls=DjangoJSONEncoder)

    # User growth data
    user_data = (
        User.objects.values("date_joined__date")
        .annotate(count=Count("id"))
        .order_by("date_joined__date")
    )
    user_json = json.dumps(list(user_data), cls=DjangoJSONEncoder)

    # Active vs inactive users
    active_users = User.objects.filter(last_login__isnull=False).count()
    inactive_users = User.objects.filter(last_login__isnull=True).count()

    return render(request, "dashboard/home.html", {
        "stats": stats,
        "sales_data": sales_json,
        "review_data": review_json,
        "favorite_data": favorite_json,
        "user_data": user_json,
        "active_users": active_users,
        "inactive_users": inactive_users,
    })



# ---------------- Orders ----------------
@user_passes_test(lambda u: u.is_staff)
def order_list(request):
    orders = Order.objects.all().order_by("-created_at")
    return render(request, "dashboard/orders.html", {"orders": orders})

@user_passes_test(lambda u: u.is_staff)
def generate_bill(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    total = sum(product.price for product in order.products.all())
    return render(request, "store/invoice.html", {"order": order, "total": total})

# ---------------- Analytics ----------------
@login_required
def analytics_dashboard(request):
    sales_data = []     # handled via sales_data_api
    favorite_data = []  # handled via future favorites API
    return render(
        request,
        "dashboard/analytics.html",
        {"sales_data": sales_data, "favorite_data": favorite_data},
    )

# ---------------- Reviews ----------------
@login_required
def review_list(request):
    reviews = Review.objects.select_related("product", "user").all().order_by("-created_at")
    return render(request, "dashboard/reviews.html", {"reviews": reviews})

# ---------------- API Endpoints ----------------
def sales_data_api(request):
    data = (
        Order.objects.values("created_at")
        .annotate(total=Count("id"))   # FIXED: count orders per day
        .order_by("created_at")
    )
    return JsonResponse(list(data), safe=False)

def review_data_api(request):
    data = list(
        Review.objects.values("product__name").annotate(count=Count("id"))
    )
    return JsonResponse(data, safe=False)

# ---------------- Review Moderation ----------------
def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)

@staff_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    messages.success(request, "Review deleted successfully.")
    return redirect("review_list")

@staff_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == "POST":
        review.rating = request.POST.get("rating", review.rating)
        review.comment = request.POST.get("comment", review.comment)
        review.save()
        messages.success(request, "Review updated successfully.")
        return redirect("review_list")
    return render(request, "dashboard/edit_review.html", {"review": review})

from django.views.decorators.http import require_POST

@staff_required
@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get("status")
    if new_status:
        order.status = new_status
        order.save()
        messages.success(request, f"Order {order.id} status updated to {new_status}.")
    return redirect("order_list")


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from store.models import Order, Review, Favorite
from django.db.models import Count

from django.http import JsonResponse

def sales_data_api(request):
    sales_data = (
        Order.objects.values("created_at__date")
        .annotate(count=Count("id"))
        .order_by("created_at__date")
    )
    return JsonResponse(list(sales_data), safe=False)

def review_data_api(request):
    review_data = (
        Review.objects.values("product__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    return JsonResponse(list(review_data), safe=False)

from django.http import JsonResponse
from django.db.models import Count
from store.models import Favorite

def favorite_data_api(request):
    favorite_data = (
        Favorite.objects.values("product__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    return JsonResponse(list(favorite_data), safe=False)




# ---------------- Catalog Management ----------------
from .forms import CategoryForm, ProductForm
from store.models import Category, Product, Feedback

@staff_required
def category_list(request):
    items = Category.objects.all()
    return render(request, "dashboard/catalog_list.html", {"title": "Categories", "items": items, "type": "category"})

@staff_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect("dashboard_category_list")
    else:
        form = CategoryForm()
    return render(request, "dashboard/catalog_form.html", {"title": "Create Category", "form": form})

@staff_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect("dashboard_category_list")
    else:
        form = CategoryForm(instance=category)
    return render(request, "dashboard/catalog_form.html", {"title": "Edit Category", "form": form})

@staff_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted successfully.")
        return redirect("dashboard_category_list")
    return render(request, "dashboard/catalog_confirm_delete.html", {"title": "Delete Category", "item": category, "cancel_url": "dashboard_category_list"})

@staff_required
def product_list(request):
    items = Product.objects.all()
    return render(request, "dashboard/catalog_list.html", {"title": "Products", "items": items, "type": "product"})

@staff_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product created successfully.")
            return redirect("dashboard_product_list")
    else:
        form = ProductForm()
    return render(request, "dashboard/catalog_form.html", {"title": "Create Product", "form": form})

@staff_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect("dashboard_product_list")
    else:
        form = ProductForm(instance=product)
    return render(request, "dashboard/catalog_form.html", {"title": "Edit Product", "form": form})

@staff_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect("dashboard_product_list")
    return render(request, "dashboard/catalog_confirm_delete.html", {"title": "Delete Product", "item": product, "cancel_url": "dashboard_product_list"})

@staff_required
def feedback_list(request):
    feedbacks = Feedback.objects.select_related("user").all().order_by("-created_at")
    return render(request, "dashboard/feedback_list.html", {"feedbacks": feedbacks})

@staff_required
def feedback_delete(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    if request.method == "POST":
        feedback.delete()
        messages.success(request, "Feedback deleted successfully.")
        return redirect("dashboard_feedback_list")
    return render(request, "dashboard/catalog_confirm_delete.html", {"title": "Delete Feedback", "item": feedback, "cancel_url": "dashboard_feedback_list"})

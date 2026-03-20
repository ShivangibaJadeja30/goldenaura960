from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count
from store.models import Order, Review

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.contrib.auth.models import User
from store.models import Order, Review, Favorite

@login_required
def dashboard_home(request):
    stats = {
    "total_orders": Order.objects.count(),
    "total_revenue": 0,  # placeholder until you add a field
    "total_reviews": Review.objects.count(),
}


    # ... rest of your analytics code ...


    # Sales data
    sales_data = (
        Order.objects.values("created_at__date")
        .annotate(count=Count("id"))
        .order_by("created_at__date")
    )

    # Review data
    review_data = (
        Review.objects.values("product__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Favorites data
    favorite_data = (
        Favorite.objects.values("product__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # User growth data
    user_data = (
        User.objects.values("date_joined__date")
        .annotate(count=Count("id"))
        .order_by("date_joined__date")
    )

    # Active vs inactive users
    active_users = User.objects.filter(last_login__isnull=False).count()
    inactive_users = User.objects.filter(last_login__isnull=True).count()

    return render(request, "dashboard/home.html", {
        "stats": stats,
        "sales_data": list(sales_data),
        "review_data": list(review_data),
        "favorite_data": list(favorite_data),
        "user_data": list(user_data),
        "active_users": active_users,
        "inactive_users": inactive_users,
    })



# ---------------- Orders ----------------
@login_required
def order_list(request):
    orders = Order.objects.all().order_by("-created_at")
    return render(request, "dashboard/orders.html", {"orders": orders})

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

@login_required
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







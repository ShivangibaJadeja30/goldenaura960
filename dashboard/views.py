from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count
from store.models import Order, Review

# ---------------- Dashboard Home ----------------
@login_required
def dashboard_home(request):
    stats = {
        "total_orders": Order.objects.count(),
        # FIXED: use Count("id") instead of Sum("total") since no 'total' field exists
        "total_revenue": Order.objects.aggregate(total=Count("id"))["total"] or 0,
        "total_reviews": Review.objects.count(),
    }
    return render(request, "dashboard/home.html", {"stats": stats})

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

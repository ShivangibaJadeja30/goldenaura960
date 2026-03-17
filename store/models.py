from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    payment_option = models.CharField(
        max_length=50,
        choices=[
            ("COD", "Cash on Delivery"),
            ("CARD", "Credit/Debit Card"),
            ("UPI", "UPI"),
            ("NETBANKING", "Net Banking"),
        ],
        default="COD"
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"
    

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to="products/")

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Cart)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user or 'Guest'}"



from django.db import models
from django.contrib.auth.models import User
from admins.models import CdInventory
from django.utils import timezone

# Create your models here.
class StaffCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cd = models.ForeignKey(CdInventory, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    contact = models.CharField(max_length=20)
    email = models.EmailField()
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    total_with_tax = models.DecimalField(max_digits=10, decimal_places=2)
    date_and_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.title}"
    
class LowStockAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cd = models.ForeignKey(CdInventory, on_delete=models.CASCADE)
    alert_message = models.CharField(max_length=255)
    alert_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Low stock alert for {self.cd.title}"
    
class StaffLowStockReport(models.Model):
    logged_user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert_message = models.TextField()
    alert_time = models.DateTimeField(auto_now_add=True)
    date_and_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.logged_user.username} on {self.alert_time}"
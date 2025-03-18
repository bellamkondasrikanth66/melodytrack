from django.db import models

# Create your models here.
class CategorySelection(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100)

    def __str__(self):
        return self.category

class CdInventory(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    moviename = models.CharField(max_length=200, blank=True, null=True)
    artist = models.CharField(max_length=200)
    release_year = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    subcategory =models.CharField(max_length=100)
    supplier = models.CharField(max_length=100, default='None')

    def __str__(self):
        return f"{self.title} by {self.artist}"
    
class Supplier(models.Model):
    id = models.AutoField(primary_key=True)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    contact = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} by {self.email}"
    
class SupplierPurchase(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    contact = models.CharField(max_length=15)  
    quantity = models.IntegerField()
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
class SupplierInvoice(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    email = models.EmailField()
    category = models.CharField(max_length=100, null=True, blank=True)
    subcategory = models.CharField(max_length=100, null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice for {self.first_name} {self.last_name} - {self.total_price}"
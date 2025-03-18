from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
from decimal import Decimal
from admins.models import *
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from datetime import datetime
from admins.models import CdInventory
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from django.db.models import Sum
import io
import urllib, base64

def generate_pie_chart_user():
    active_staff_users = User.objects.filter(is_staff=True, is_active=True).count()
    inactive_staff_users = User.objects.filter(is_staff=True, is_active=False).count()
    active_non_staff_users = User.objects.filter(is_staff=False, is_active=True).count()
    inactive_non_staff_users = User.objects.filter(is_staff=False, is_active=False).count()

    data = {
        'status': ['Active Staff', 'Inactive Staff', 'Active Non-Staff', 'Inactive Non-Staff'],
        'count': [active_staff_users, inactive_staff_users, active_non_staff_users, inactive_non_staff_users]
    }
    df = pd.DataFrame(data)

    plt.figure(figsize=(8, 6))
    plt.pie(df['count'], labels=df['status'], autopct='%1.1f%%', startangle=140)
    plt.title('User Distribution by Staff and Active Status')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    return uri

def generate_pie_chart():
    cds = CdInventory.objects.all()
    df = pd.DataFrame(list(cds.values('category', 'quantity')))
    df_grouped = df.groupby('category').sum().reset_index()

    plt.figure(figsize=(8, 6))
    plt.pie(df_grouped['quantity'], labels=df_grouped['category'], autopct='%1.1f%%')
    plt.title('CD Inventory Distribution by Category')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    return uri

def generate_bar_chart():
    purchases = SupplierPurchase.objects.all()
    df = pd.DataFrame(list(purchases.values('category', 'quantity')))
    df_grouped = df.groupby('category').sum().reset_index()

    plt.figure(figsize=(10, 6))
    plt.bar(df_grouped['category'], df_grouped['quantity'], color='skyblue')
    plt.xlabel('Category')
    plt.ylabel('Quantity')
    plt.title('Supplier Purchases by Category')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    return uri

# Create your views here.
def staffhomepage(request):
    pie_chart_data = generate_pie_chart()
    bar_chart_data = generate_bar_chart()
    user_pie_chart_data = generate_pie_chart_user()

    context = {
        'pie_chart_data': pie_chart_data,
        'bar_chart_data': bar_chart_data,
        'user_pie_chart_data': user_pie_chart_data,
    }
    return render(request, 'staff/staffhomepage.html', context)

def user_Account(request):
    user = request.user  
    return render(request, 'staff/user_Account.html', {'user': user})

def staffupdatedetailsaction(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not user_id:
            messages.error(request, "No user ID provided.")
            return redirect('user_Account')  
        user = get_object_or_404(User, id=user_id)
        
        new_username = request.POST.get('username')
        new_first_name = request.POST.get('first_name')
        new_last_name = request.POST.get('last_name')
        new_email = request.POST.get('email')

        if user.username != new_username:
            user.username = new_username
        if user.first_name != new_first_name:
            user.first_name = new_first_name
        if user.last_name != new_last_name:
            user.last_name = new_last_name
        if user.email != new_email:
            user.email = new_email
        
        user.save()
        messages.success(request, 'staff details updated successfully!')
        return redirect('user_Account') 
    else:
        return redirect('user_Account') 

def staffchangepasswordaction(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not user_id:
            messages.error(request, "No user ID provided.")
            return redirect('user_Account')  
        user = get_object_or_404(User, id=user_id)

        new_password = request.POST.get('new_password')
        cnfm_Password = request.POST.get('cnfm_Password')

        if cnfm_Password != new_password:
            messages.error(request, "Passwords do not match.")
            return redirect('user_Account')

        user.password = make_password(new_password)
        user.save()
        messages.success(request, 'Password reset successfully!')
        return redirect('user_Account')
    else:
        user_id = request.GET.get('id')
        if not user_id:
            messages.error(request, "No user ID provided.")
            return redirect('user_Account')  
        return redirect('user_Account')

def staffviewcds(request):
    cd_inventory_list = CdInventory.objects.all()
    paginator = Paginator(cd_inventory_list, 12) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'staff/staffviewcds.html', {'page_obj': page_obj})

@login_required
def staff_addtocart(request):
    cd_id = request.GET.get('id')
    cd = get_object_or_404(CdInventory, id=cd_id)
    user = request.user
    cart_item, created = StaffCart.objects.get_or_create(user=user, cd=cd)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return HttpResponse(status=204)

def cd_inventory_search_view(request):
    search_term = request.GET.get('search_term', '')

    cds = CdInventory.objects.all()

    if search_term:
        cds = cds.filter(
            Q(title__icontains=search_term) |
            Q(artist__icontains=search_term) |
            Q(category__icontains=search_term) |
            Q(subcategory__icontains=search_term) |
            Q(moviename__icontains=search_term) |
            Q(release_year__icontains=search_term)
        )

    paginator = Paginator(cds, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'staff/staffsearchviewcds.html', {'page_obj': page_obj})

def cd_inventory_filter_view(request):
    title = request.GET.get('title', '')
    artist = request.GET.get('artist', '')
    category = request.GET.get('category', '')
    subcategory = request.GET.get('subcategory', '')
    moviename = request.GET.get('moviename', '')
    release_year = request.GET.get('release_year', '')

    cds = CdInventory.objects.all()

    if title:
        cds = cds.filter(title__icontains=title)
    if artist:
        cds = cds.filter(artist__icontains=artist)
    if category:
        cds = cds.filter(category__icontains=category)
    if subcategory:
        cds = cds.filter(subcategory__icontains=subcategory)
    if moviename:
        cds = cds.filter(moviename__icontains=moviename)
    if release_year:
        cds = cds.filter(release_year__icontains=release_year)

    paginator = Paginator(cds, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'staff/stafffilterviewcds.html', {'page_obj': page_obj})

def cd_inventory_sort_view(request):
    sort_by = request.GET.get('sort_by', '')

    cds = CdInventory.objects.all()

    if sort_by:
        cds = cds.order_by(sort_by)

    paginator = Paginator(cds, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'staff/staffsortviewcds.html', {'page_obj': page_obj})

def staffcart(request):
    cart_items = StaffCart.objects.filter(user=request.user)
    total_price = sum(item.cd.price * item.quantity for item in cart_items)
    return render(request, 'staff/staffcart.html', {'cart_items': cart_items, 'total_price': total_price})

def staffproceedtonext(request):
    return render(request, 'staff/staffproceedtocheckout.html')

def staffproceedtocheckout(request):
    if request.method == 'POST':
        request.session['customer_details'] = {
            'customer_first_name': request.POST.get('first_name'),
            'customer_last_name': request.POST.get('last_name'),
            'customer_phone_number': request.POST.get('Phone contact'),
            'customer_email': request.POST.get('email'),
        }
        return redirect('staffgenerateinvoice') 
    else:
        return render(request, 'staff/staffproceedtocheckout.html')

def increment_cart_item(request):
    item_id = request.GET.get('item_id')
    cart_item = get_object_or_404(StaffCart, id=item_id)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('staffcart')

def decrement_cart_item(request):
    item_id = request.GET.get('item_id')
    cart_item = get_object_or_404(StaffCart, id=item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    return redirect('staffcart')

def delete_cart_item(request):
    item_id = request.GET.get('item_id')
    cart_item = get_object_or_404(StaffCart, id=item_id)
    cart_item.delete()
    return redirect('staffcart')

def staffgenerateinvoice(request):
    customer_details = request.session.get('customer_details')
    if not customer_details:
        return redirect('staffproceedtocheckout')  

    cart_items = StaffCart.objects.filter(user=request.user)
    total_price = sum(item.cd.price * item.quantity for item in cart_items)
    tax_rate = Decimal('0.1')  
    tax = total_price * tax_rate
    total_with_tax = total_price + tax

    cart_items_with_total = []
    for item in cart_items:
        item_total = item.cd.price * item.quantity
        cart_items_with_total.append({
            'title': item.cd.title,
            'price': item.cd.price,
            'quantity': item.quantity,
            'total': item_total
        })

    return render(request, 'staff/staffgenerateinvoice.html', {
        'cart_items': cart_items_with_total,
        'total_price': total_price,
        'tax': tax,
        'total_with_tax': total_with_tax,
        'customer_details': customer_details
    })

def customerpurchaseaction(request):
    user = request.user 
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        titles = request.POST.getlist('title')
        prices = request.POST.getlist('price')
        quantities = request.POST.getlist('quantity')
        total_price = request.POST.get('total_price')
        tax = request.POST.get('tax')
        total_with_tax = request.POST.get('total_with_tax')

        for title, price, quantity in zip(titles, prices, quantities):
            quantity = int(quantity) 
            cd = get_object_or_404(CdInventory, title=title)
            
            if cd.quantity >= quantity:
                cd.quantity -= quantity
                cd.save()
                
                purchase = Purchase(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    contact=contact,
                    email=email,
                    title=title,
                    price=price,
                    quantity=quantity,
                    total_price=total_price,
                    tax=tax,
                    total_with_tax=total_with_tax
                )
                purchase.save()
            else:
                messages.error(request, f"Insufficient quantity for {title}. Available: {cd.quantity}")

        return redirect('staffcart')

    return redirect('staffcart')

def staffpurchasereport(request):
    user = request.user
    purchases = Purchase.objects.filter(user=user).order_by('-date_and_time')
    
    paginator = Paginator(purchases, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'staff/staffpurchasereport.html', {'page_obj': page_obj})

def staffupdatestock(request):
    cd_inventory_list = CdInventory.objects.all()
    paginator = Paginator(cd_inventory_list, 12) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'staff/staffupdatestock.html', {'page_obj': page_obj})

def staff_cd_details(request):
    cd_id = request.GET.get('id')
    cd = get_object_or_404(CdInventory, id=cd_id)
    return render(request, 'staff/staff_cd_details.html', {'cd': cd})

def staffupdatecddetails(request):
    if request.method == 'POST':
        cd_id = request.POST.get('cd_id')
        if not cd_id:
            messages.error(request, "No CD ID provided.")
            return redirect('staffupdatestock')

        cd = get_object_or_404(CdInventory, id=cd_id)

        cd.title = request.POST.get('title')
        cd.artist = request.POST.get('artist')
        cd.moviename = request.POST.get('moviename', '')
        cd.release_year = request.POST.get('release_year')
        cd.quantity = request.POST.get('quantity')
        cd.price = request.POST.get('price')
        cd.category = request.POST.get('category')
        cd.subcategory = request.POST.get('subcategory')

        cd.save()
        messages.success(request, 'CD details updated successfully!')
        return HttpResponseRedirect(reverse('staff_cd_details') + f'?id={cd.id}')
    else:
        cd_id = request.GET.get('id')
        if not cd_id:
            messages.error(request, "No CD ID provided.")
            return redirect('staffupdatestock')
        return HttpResponseRedirect(reverse('staff_cd_details') + f'?id={cd_id}')
    
def staffreturncd(request):
    return render(request, 'staff/staffreturncd.html')

def return_cd(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        artist = request.POST.get('artist')
        
        if title and artist:
            cd = get_object_or_404(CdInventory, title=title, artist=artist)
            cd.quantity += 1
            cd.save()
            return render(request, 'staff/staffreturncd.html')  
        else:
            return render(request, 'staff/staffreturncd.html')
    else:
        return render(request, 'staff/staffreturncd.html')
    
@login_required
def staffstockalert(request):
    user = request.user
    LowStockAlert.objects.filter(user=user).delete()
    low_stock_cds = CdInventory.objects.filter(quantity__lt=50)
    for cd in low_stock_cds:
        alert_message = f"Low stock alert for {cd.title} by {cd.artist}, quantity is {cd.quantity}"
        LowStockAlert.objects.create(cd=cd, alert_message=alert_message, alert_time=timezone.now(), user=user)
    low_stock_alerts = LowStockAlert.objects.filter(user=user).order_by('-alert_time')

    paginator = Paginator(low_stock_alerts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, 'staff/staffstockalert.html', context)

def report_admin(request):
    if request.method == 'POST':
        logged_user  = request.user
        alerts = LowStockAlert.objects.filter(user=logged_user )
        for alert in alerts:
            alert_message = alert.alert_message
            alert_time = alert.alert_time

            report = StaffLowStockReport(
                logged_user=logged_user,
                alert_message=alert_message,
                alert_time=alert_time
            )
            report.save()

        messages.success(request, 'All alerts have been reported.')

    return redirect('staffstockalert')
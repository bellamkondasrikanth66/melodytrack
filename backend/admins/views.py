from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from collections import defaultdict
from datetime import datetime, timedelta
from .models import *
from staff.models import *
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

def adminhomepage(request):
    pie_chart_data = generate_pie_chart()
    bar_chart_data = generate_bar_chart()
    user_pie_chart_data = generate_pie_chart_user()

    context = {
        'pie_chart_data': pie_chart_data,
        'bar_chart_data': bar_chart_data,
        'user_pie_chart_data': user_pie_chart_data,
    }
    return render(request, 'admin/adminhomepage.html', context)

def admincreatestaff(request):
    staff_accounts = User.objects.filter(is_superuser=False).order_by('-date_joined')
    paginator = Paginator(staff_accounts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/admincreatestaff.html', {'page_obj': page_obj})

def admincreatestaffaction(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('admincreatestaff')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('admincreatestaff')
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                is_superuser=False,
                is_staff=False,
                is_active=False
            )
            user.save()
            messages.success(request, 'staff account created successful.')
            return redirect('admincreatestaff')
    else:
        return redirect('admincreatestaff')
    
def admin_user_detail(request):
    user_id = request.GET.get('id')
    if not user_id:
        messages.error(request, "No user ID provided.")
        return redirect('admincreatestaffaction') 
    user = get_object_or_404(User, id=user_id)
    return render(request, 'admin/admin_user_detail.html', {'user': user})

def adminupdatestaffdetailsaction(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not user_id:
            messages.error(request, "No user ID provided.")
            return redirect('admincreatestaff')  
        user = get_object_or_404(User, id=user_id)
        
        new_username = request.POST.get('username')
        new_first_name = request.POST.get('first_name')
        new_last_name = request.POST.get('last_name')
        new_email = request.POST.get('email')
        isactive = request.POST.get('status')
        role = request.POST.get('role')

        if user.username != new_username:
            user.username = new_username
        if user.first_name != new_first_name:
            user.first_name = new_first_name
        if user.last_name != new_last_name:
            user.last_name = new_last_name
        if user.email != new_email:
            user.email = new_email
        if user.is_active != isactive:
            user.is_active = isactive
        if user.is_staff != role:
            user.is_staff = role
        
        user.save()
        messages.success(request, 'staff details updated successfully!')
        return HttpResponseRedirect(reverse('admin_user_detail') + f'?id={user.id}')
    else:
        return HttpResponseRedirect(reverse('admin_user_detail') + f'?id={user_id}')

def adminresetstaffpasswordaction(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not user_id:
            messages.error(request, "No user ID provided.")
            return redirect('admincreatestaff')  
        user = get_object_or_404(User, id=user_id)

        new_password = request.POST.get('new_password')
        cnfm_Password = request.POST.get('cnfm_Password')

        if cnfm_Password != new_password:
            messages.error(request, "Passwords do not match.")
            return HttpResponseRedirect(reverse('admin_user_detail') + f'?id={user.id}')

        user.password = make_password(new_password)
        user.save()
        messages.success(request, 'Password reset successfully!')
        return HttpResponseRedirect(reverse('admin_user_detail') + f'?id={user.id}')
    else:
        user_id = request.GET.get('id')
        if not user_id:
            messages.error(request, "No user ID provided.")
            return redirect('admincreatestaff')  
        return HttpResponseRedirect(reverse('admin_user_detail') + f'?id={user_id}')
    
def admindeletestaffaction(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not user_id:
            messages.error(request, "No user ID provided.")
            return redirect('admincreatestaff')  

        username = request.POST.get('username')
        user = get_object_or_404(User, id=user_id)

        if user.username == username:
            user.delete()
            messages.success(request, 'staff deleted successfully!')
            return redirect('admincreatestaff')
        else:
            messages.error(request, "Username does not match.")
            return HttpResponseRedirect(reverse('admin_user_detail') + f'?id={user.id}')
    else:
        user_id = request.GET.get('id')
        if not user_id:
            messages.error(request, "No user ID provided.")
            return redirect('admincreatestaff')   
        return HttpResponseRedirect(reverse('admin_user_detail') + f'?id={user_id}')

def adminaddcdcategory(request):
    categories = CategorySelection.objects.all()
    grouped_categories = defaultdict(list)
    
    for category in categories:
        grouped_categories[category.category].append(category.subcategory)
    
    return render(request, 'admin/adminaddcdcategory.html', {'categories': dict(grouped_categories)})

def adminaddcdcategoryaction(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        subcategory = request.POST.get('subcategory')
        if category and subcategory:
            if not CategorySelection.objects.filter(category=category, subcategory=subcategory).exists():
                CategorySelection.objects.create(category=category, subcategory=subcategory)
                messages.success(request, "Category added successfully.")
            else:
                messages.info(request, "This category and subcategory already exist.")
        else:
            messages.error(request, "Category and subcategory cannot be empty.")
        return redirect('adminaddcdcategory')
    else:
        return redirect('adminaddcdcategory')
    
def adminaddnewcd(request):
    categories = CategorySelection.objects.values_list('category', flat=True).distinct()
    return render(request, 'admin/adminaddnewcd.html', {'categories': categories})

def load_subcategories(request):
    category = request.GET.get('category')
    subcategories = CategorySelection.objects.filter(category=category).values('id', 'subcategory')
    return JsonResponse(list(subcategories), safe=False)

def adminaddnewcdaction(request):
    if request.method == 'POST':
        title = request.POST['title']
        artist = request.POST['artist']
        release_year = request.POST['release_year']
        quantity = request.POST['quantity']
        price = request.POST['price']
        category = request.POST['category']
        subcategory = request.POST['subcategory']
        moviename = request.POST['moviename']

        cd = CdInventory.objects.create(
            title=title,
            artist=artist,
            release_year=release_year,
            quantity=quantity,
            price=price,
            category=category,
            subcategory=subcategory,
            moviename = moviename
        )
        cd.save() 
        messages.success(request, "New CD Added Successfull.")
        return redirect('adminaddnewcd')  
    else:
        messages.error(request, "New CD Added Un-Successfull.")
        return redirect('adminaddnewcd')
    
def admin_bulk_add_cd_action(request):
    if request.method == 'POST':
        if 'cd_excel_file' in request.FILES:
            file = request.FILES['cd_excel_file']
            file_extension = os.path.splitext(file.name)[1]
            try:
                if file_extension == '.xlsx':
                    df = pd.read_excel(file, engine='openpyxl')
                elif file_extension == '.csv':
                    df = pd.read_csv(file)
                else:
                    messages.error(request, "Unsupported file format. Please upload an Excel or CSV file.")
                    return redirect('adminaddnewcd')

                required_columns = ['title', 'artist', 'release_year', 'quantity', 'price', 'category', 'subcategory']
                for column in required_columns:
                    if column not in df.columns:
                        messages.error(request, f"Missing required column: {column}")
                        return redirect('adminaddnewcd')

                existing_records = CdInventory.objects.values_list('title', 'artist', 'release_year')
                existing_set = set(existing_records)

                cds = []
                for _, row in df.iterrows():
                    record_tuple = (row['title'], row['artist'], row['release_year'])
                    if record_tuple not in existing_set:
                        cds.append(CdInventory(
                            title=row['title'],
                            artist=row['artist'],
                            release_year=row['release_year'],
                            quantity=row['quantity'],
                            price=row['price'],
                            category=row['category'],
                            subcategory=row['subcategory'],
                            moviename=row.get('moviename', '') 
                        ))

                if cds:
                    CdInventory.objects.bulk_create(cds)
                    messages.success(request, "Bulk CD upload successful.")
                else:
                    messages.info(request, "No new records to add. All records already exist.")

            except Exception as e:
                messages.error(request, f"Bulk CD upload failed: {e}")

            return redirect('adminaddnewcd')
        else:
            messages.error(request, "No file uploaded.")
            return redirect('adminaddnewcd')
    else:
        messages.error(request, "Invalid request method.")
        return redirect('adminaddnewcd')

def admincdinventory(request):
    cd_inventory_list = CdInventory.objects.all()

    supplier = request.GET.get('supplier')
    title = request.GET.get('title')
    artist = request.GET.get('artist')
    release_year = request.GET.get('release_year')
    category = request.GET.get('category')
    subcategory = request.GET.get('subcategory')

    if supplier:
        cd_inventory_list = cd_inventory_list.filter(supplier__icontains=supplier)
    if title:
        cd_inventory_list = cd_inventory_list.filter(title__icontains=title)
    if artist:
        cd_inventory_list = cd_inventory_list.filter(artist__icontains=artist)
    if release_year:
        cd_inventory_list = cd_inventory_list.filter(release_year__icontains=release_year)
    if category:
        cd_inventory_list = cd_inventory_list.filter(category__icontains=category)
    if subcategory:
        cd_inventory_list = cd_inventory_list.filter(subcategory__icontains=subcategory)

    paginator = Paginator(cd_inventory_list, 12) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/admincdinventory.html', {'page_obj': page_obj})

def download_cd_report(request):
    cd_inventory_list = CdInventory.objects.all()

    supplier = request.GET.get('supplier')
    title = request.GET.get('title')
    artist = request.GET.get('artist')
    release_year = request.GET.get('release_year')
    category = request.GET.get('category')
    subcategory = request.GET.get('subcategory')

    if supplier:
        cd_inventory_list = cd_inventory_list.filter(supplier__icontains=supplier)
    if title:
        cd_inventory_list = cd_inventory_list.filter(title__icontains=title)
    if artist:
        cd_inventory_list = cd_inventory_list.filter(artist__icontains=artist)
    if release_year:
        cd_inventory_list = cd_inventory_list.filter(release_year__icontains=release_year)
    if category:
        cd_inventory_list = cd_inventory_list.filter(category__icontains=category)
    if subcategory:
        cd_inventory_list = cd_inventory_list.filter(subcategory__icontains=subcategory)
    
    data = [{
        'Supplier': cd.supplier,
        'Title': cd.title,
        'Artist': cd.artist,
        'Release Year': cd.release_year,
        'Category': cd.category,
        'Subcategory': cd.subcategory,
    }for cd in cd_inventory_list]

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=cd_report.xlsx'
    df.to_excel(response, index=False, engine='openpyxl')
    
    return response

def admin_cd_details(request):
    cd_id = request.GET.get('id')
    cd = get_object_or_404(CdInventory, id=cd_id)
    suppliers = Supplier.objects.all()
    return render(request, 'admin/admin_cd_detail.html', {'cd': cd, 'suppliers': suppliers})

def adminupdatecddetails(request):
    if request.method == 'POST':
        cd_id = request.POST.get('cd_id')
        if not cd_id:
            messages.error(request, "No CD ID provided.")
            return redirect('admincdinventory')

        cd = get_object_or_404(CdInventory, id=cd_id)

        cd.title = request.POST.get('title')
        cd.artist = request.POST.get('artist')
        cd.moviename = request.POST.get('moviename', '')
        cd.release_year = request.POST.get('release_year')
        cd.quantity = request.POST.get('quantity')
        cd.price = request.POST.get('price')
        cd.category = request.POST.get('category')
        cd.subcategory = request.POST.get('subcategory')
        cd.supplier = request.POST.get('supplier')

        cd.save()
        messages.success(request, 'CD details updated successfully!')
        return HttpResponseRedirect(reverse('admin_cd_details') + f'?id={cd.id}')
    else:
        cd_id = request.GET.get('id')
        if not cd_id:
            messages.error(request, "No CD ID provided.")
            return redirect('admincdinventory')
        return HttpResponseRedirect(reverse('admin_cd_details') + f'?id={cd_id}')

def admindeletecdaction(request):
    if request.method == 'POST':
        cd_id = request.POST.get('cd_id')
        if not cd_id:
            messages.error(request, "No CD ID provided.")
            return redirect('admincdinventory')

        title = request.POST.get('title')
        cd = get_object_or_404(CdInventory, id=cd_id)

        if cd.title == title:
            cd.delete()
            messages.success(request, 'CD deleted successfully!')
            return redirect('admincdinventory')  
        else:
            messages.error(request, "Title does not match.")
            return HttpResponseRedirect(reverse('admin_cd_details') + f'?id={cd.id}')
    else:
        cd_id = request.GET.get('id')
        if not cd_id:
            messages.error(request, "No CD ID provided.")
            return redirect('admincdinventory') 
        return HttpResponseRedirect(reverse('admin_cd_details') + f'?id={cd_id}')
    
def adminstocklevels(request):
    low_stock_alerts = StaffLowStockReport.objects.all()
    paginator = Paginator(low_stock_alerts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, 'admin/adminstocklevels.html', context)

def admincreatesupplier(request):
    Suppliers = Supplier.objects.all()
    paginator = Paginator(Suppliers, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, 'admin/admincreatesupplier.html', context)

def admincreatesupplieraction(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        contact = request.POST['contact']

        if Supplier.objects.filter(first_name=first_name).exists():
            messages.error(request, 'Username already exists.')
            return redirect('admincreatesupplier')
        elif Supplier.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('admincreatesupplier')
        else:
            user = Supplier.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                contact = contact,
            )
            user.save()
            messages.success(request, 'Supplier details created successful.')
            return redirect('admincreatesupplier')
    else:
        return redirect('admincreatesupplier')
    
def admin_supplier_detail(request):
    user_id = request.GET.get('id')
    if not user_id:
        messages.error(request, "No user ID provided.")
        return redirect('admincreatestaffaction') 
    user = get_object_or_404(Supplier, id=user_id)
    return render(request, 'admin/admin_supplier_detail.html', {'user': user})

def adminupdatesuplierdetailsaction(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not user_id:
            messages.error(request, "No user ID provided.")
            return redirect('admincreatesupplier')  
        user = get_object_or_404(Supplier, id=user_id)
        new_first_name = request.POST.get('first_name')
        new_last_name = request.POST.get('last_name')
        new_email = request.POST.get('email')
        new_contact = request.POST.get('contact')

        if user.first_name != new_first_name:
            user.first_name = new_first_name
        if user.last_name != new_last_name:
            user.last_name = new_last_name
        if user.email != new_email:
            user.email = new_email
        if user.contact != new_contact:
            user.contact = new_contact

        user.save()
        messages.success(request, 'staff details updated successfully!')
        return HttpResponseRedirect(reverse('admin_supplier_detail') + f'?id={user.id}')
    else:
        return HttpResponseRedirect(reverse('admin_supplier_detail') + f'?id={user_id}')
    
def admindeletesupplieraction(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not user_id:
            messages.error(request, "No user ID provided.")
            return redirect('admincreatesupplier')  

        username = request.POST.get('username')
        user = get_object_or_404(Supplier, id=user_id)

        if user.first_name == username:
            user.delete()
            messages.success(request, 'staff deleted successfully!')
            return redirect('admincreatesupplier')
        else:
            messages.error(request, "Username does not match.")
            return HttpResponseRedirect(reverse('admin_supplier_detail') + f'?id={user.id}')
    else:
        user_id = request.GET.get('id')
        if not user_id:
            messages.error(request, "No user ID provided.")
            return redirect('admincreatesupplier')   
        return HttpResponseRedirect(reverse('admin_supplier_detail') + f'?id={user_id}')

def admintracksales(request):
    sales = Purchase.objects.all().order_by('-date_and_time')

    user_filter = request.GET.get('user')
    title_filter = request.GET.get('title')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if user_filter:
        sales = sales.filter(user__username__icontains=user_filter)
    if title_filter:
        sales = sales.filter(title__icontains=title_filter)
    if date_from and date_to:
        sales = sales.filter(date_and_time__range=[date_from, date_to])
    
    paginator = Paginator(sales, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj, 'user_filter': user_filter, 'title_filter': title_filter, 'date_from': date_from, 'date_to': date_to}
    return render(request, 'admin/admintracksales.html', context)

def download_report(request):
    sales = Purchase.objects.all().order_by('-date_and_time')

    user_filter = request.GET.get('user')
    title_filter = request.GET.get('title')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if user_filter:
        sales = sales.filter(user__username__icontains=user_filter)
    if title_filter:
        sales = sales.filter(title__icontains=title_filter)
    if date_from and date_to:
        sales = sales.filter(date_and_time__range=[date_from, date_to])

    data = [{
        'Customer': f"{sale.first_name} {sale.last_name}",
        'Title': sale.title,
        'Quantity': sale.quantity,
        'Amount': sale.total_price,
        'Date and Time': sale.date_and_time.replace(tzinfo=None) 
    } for sale in sales]
    
    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=sales_report.xlsx'
    df.to_excel(response, index=False, engine='openpyxl')
    
    return response

def adminaddsuplierpurchase(request):
    Supplierpurchase = SupplierPurchase.objects.all().order_by('-created_at')

    paginator = Paginator(Supplierpurchase, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/adminaddsuplierpurchase.html', {'page_obj': page_obj})

def adminaddsupplierpurchaseaction(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        quantity = request.POST.get('quantity')
        category = request.POST.get('category')
        subcategory = request.POST.get('subcategory')

        purchase = SupplierPurchase(
            first_name=first_name,
            last_name=last_name,
            email=email,
            contact=contact,
            quantity=quantity,
            category=category,
            subcategory=subcategory
        )
        purchase.save()

        messages.success(request, 'Supplier purchase added successfully.')
        return redirect('adminaddsuplierpurchase')
    else:
        return redirect('adminaddsuplierpurchase')
    
def update_status(request):
    if request.method == 'POST':
        status_data = request.POST.get('status')
        if status_data:
            status, user_id = status_data.split('-')
            user = get_object_or_404(SupplierPurchase, id=user_id)
            user.status = status
            user.save()
    return redirect('adminaddsuplierpurchase')

def admindailypurchasereport(request):
    today = datetime.now().date()
    purchases = Purchase.objects.filter(date_and_time__date=today).order_by('-date_and_time')
    
    paginator = Paginator(purchases, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin/admindailypurchasereport.html', {'page_obj': page_obj})

def adddsupplierinvoice(request):
    supplier_email = request.GET.get('supplier_email', None)
    latest_purchase = None
    
    if supplier_email:
        latest_purchase = SupplierPurchase.objects.filter(email=supplier_email).order_by('-created_at').first()
    
    return render(request, 'admin/adddsupplierinvoice.html', {'latest_purchase': latest_purchase})

def addsupplierinvoice(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        category = request.POST.get('category')
        subcategory = request.POST.get('subcategory')
        quantity = request.POST.get('quantity')
        total_price = request.POST.get('total_price')

        supplier_invoice = SupplierInvoice(
            first_name=first_name,
            last_name=last_name,
            contact=contact,
            email=email,
            category=category,
            subcategory=subcategory,
            quantity=quantity,
            total_price=total_price
        )
        supplier_invoice.save()

        return redirect('adddsupplierinvoice')  
    else:
        return redirect('adddsupplierinvoice')  
    
def viewsupplierinvoice(request):
    Supplierinvoice = SupplierInvoice.objects.all().order_by('-created_at')

    paginator = Paginator(Supplierinvoice, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/viewsupplierinvoice.html', {'page_obj': page_obj})

def admin_update_supinvoice_detail(request):
    user_id = request.GET.get('id')
    if not user_id:
        messages.error(request, "No user ID provided.")
        return redirect('viewsupplierinvoice') 
    user = get_object_or_404(SupplierInvoice, id=user_id)
    return render(request, 'admin/admin_update_supinvoice_detail.html', {'user': user})

def admin_update_supinvoice_detailaction(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not user_id:
            messages.error(request, "No user ID provided.")
            return redirect('viewsupplierinvoice')

        invoice = get_object_or_404(SupplierInvoice, id=user_id)
        new_first_name = request.POST.get('first_name')
        new_last_name = request.POST.get('last_name')
        new_email = request.POST.get('email')
        new_contact = request.POST.get('contact')
        new_category = request.POST.get('category')
        new_subcategory = request.POST.get('subcategory')
        new_quantity = request.POST.get('quantity')
        new_total_price = request.POST.get('total_price')

        if invoice.first_name != new_first_name:
            invoice.first_name = new_first_name
        if invoice.last_name != new_last_name:
            invoice.last_name = new_last_name
        if invoice.email != new_email:
            invoice.email = new_email
        if invoice.contact != new_contact:
            invoice.contact = new_contact
        if invoice.category != new_category:
            invoice.category = new_category
        if invoice.subcategory != new_subcategory:
            invoice.subcategory = new_subcategory
        if invoice.quantity != new_quantity:
            invoice.quantity = new_quantity
        if invoice.total_price != new_total_price:
            invoice.total_price = new_total_price

        invoice.save()
        messages.success(request, 'Supplier invoice details updated successfully!')
        return HttpResponseRedirect(reverse('admin_update_supinvoice_detail') + f'?id={invoice.id}')
    else:
        return HttpResponseRedirect(reverse('admin_update_supinvoice_detail') + f'?id={user_id}')
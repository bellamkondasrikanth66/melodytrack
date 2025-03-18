from django.urls import path
from .views import *


urlpatterns = [
    path('adminhomepage', adminhomepage, name='adminhomepage'),
    path('admincreatestaff', admincreatestaff, name='admincreatestaff'),
    path('admincreatestaffaction', admincreatestaffaction, name='admincreatestaffaction'),
    path('admin_user_detail', admin_user_detail, name='admin_user_detail'),
    path('adminupdatestaffdetailsaction', adminupdatestaffdetailsaction, name='adminupdatestaffdetailsaction'),
    path('adminresetstaffpasswordaction', adminresetstaffpasswordaction, name='adminresetstaffpasswordaction'),
    path('admindeletestaffaction', admindeletestaffaction, name='admindeletestaffaction'),

    path('adminaddcdcategory', adminaddcdcategory, name='adminaddcdcategory'),
    path('adminaddcdcategoryaction', adminaddcdcategoryaction, name='adminaddcdcategoryaction'),
    path('adminaddnewcd', adminaddnewcd, name='adminaddnewcd'),
    path('load_subcategories', load_subcategories, name='load_subcategories'),
    path('adminaddnewcdaction', adminaddnewcdaction, name='adminaddnewcdaction'),
    path('admin_bulk_add_cd_action', admin_bulk_add_cd_action, name='admin_bulk_add_cd_action'),
    path('admincdinventory', admincdinventory, name='admincdinventory'),
    path('admin_cd_details', admin_cd_details, name='admin_cd_details'),
    path('adminupdatecddetails', adminupdatecddetails, name='adminupdatecddetails'),
    path('admindeletecdaction', admindeletecdaction, name='admindeletecdaction'),
    path('adminstocklevels', adminstocklevels, name='adminstocklevels'),
    path('admincreatesupplier', admincreatesupplier, name='admincreatesupplier'),
    path('admincreatesupplieraction', admincreatesupplieraction, name='admincreatesupplieraction'),
    path('admin_supplier_detail', admin_supplier_detail, name='admin_supplier_detail'),
    path('adminupdatesuplierdetailsaction', adminupdatesuplierdetailsaction, name='adminupdatesuplierdetailsaction'),
    path('admindeletesupplieraction', admindeletesupplieraction, name='admindeletesupplieraction'),
    path('admintracksales', admintracksales, name='admintracksales'),
    path('download_report', download_report, name='download_report'),
    path('download_cd_report', download_cd_report, name='download_cd_report'),
    path('adminaddsuplierpurchase', adminaddsuplierpurchase, name='adminaddsuplierpurchase'),
    path('adminaddsupplierpurchaseaction', adminaddsupplierpurchaseaction, name='adminaddsupplierpurchaseaction'),
    path('update-status/', update_status, name='update_status'),
    path('admindailypurchasereport', admindailypurchasereport, name='admindailypurchasereport'),
    path('adddsupplierinvoice', adddsupplierinvoice, name='adddsupplierinvoice'),
    path('addsupplierinvoice', addsupplierinvoice, name='addsupplierinvoice'),
    path('viewsupplierinvoice', viewsupplierinvoice, name='viewsupplierinvoice'),
    path('admin_update_supinvoice_detail', admin_update_supinvoice_detail, name='admin_update_supinvoice_detail'),
    path('admin_update_supinvoice_detailaction', admin_update_supinvoice_detailaction, name='admin_update_supinvoice_detailaction')
    
]
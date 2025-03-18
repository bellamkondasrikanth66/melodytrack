from django.urls import path
from .views import *

urlpatterns = [
    path('staffhomepage', staffhomepage, name='staffhomepage'),
    path('user_Account', user_Account, name='user_Account'),
    path('staffupdatedetailsaction', staffupdatedetailsaction, name='staffupdatedetailsaction'),
    path('staffchangepasswordaction', staffchangepasswordaction, name='staffchangepasswordaction'),
    path('staffviewcds', staffviewcds, name='staffviewcds'),
    path('staff_addtocart', staff_addtocart, name='staff_addtocart'),

    path('cd_inventory_search_view', cd_inventory_search_view, name='cd_inventory_search_view'),
    path('cd_inventory_filter_view', cd_inventory_filter_view, name='cd_inventory_filter_view'),
    path('cd_inventory_sort_view', cd_inventory_sort_view, name='cd_inventory_sort_view'),
    path('staffcart', staffcart, name='staffcart'),
    path('increment_cart_item', increment_cart_item, name='increment_cart_item'),
    path('decrement_cart_item', decrement_cart_item, name='decrement_cart_item'),
    path('delete_cart_item', delete_cart_item, name='delete_cart_item'),
    path('staffproceedtonext', staffproceedtonext, name='staffproceedtonext'),
    path('staffproceedtocheckout', staffproceedtocheckout, name='staffproceedtocheckout'),
    path('staffgenerateinvoice', staffgenerateinvoice, name='staffgenerateinvoice'),
    path('customerpurchaseaction', customerpurchaseaction, name='customerpurchaseaction'),
    path('staffpurchasereport', staffpurchasereport, name='staffpurchasereport'),
    path('staffupdatestock', staffupdatestock, name='staffupdatestock'),
    path('staff_cd_details', staff_cd_details, name='staff_cd_details'),
    path('staffupdatecddetails', staffupdatecddetails, name='staffupdatecddetails'),
    path('staffreturncd', staffreturncd, name='staffreturncd'),
    path('return_cd', return_cd, name='return_cd'),
    path('staffstockalert', staffstockalert, name='staffstockalert'),
    path('report_admin', report_admin, name='report_admin'),
    
    
]
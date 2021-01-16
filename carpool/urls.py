from django.urls import path
from .views import *

urlpatterns = [
    path('', carpool_home, name='carpool'),
    path('<slug:place_id>/', carpool_home, name='carpool_sel'),
    path('join/<int:pool_id>/', join_pool, name='join'),
    path('add/place/', add_place, name='add_pl'),
    path('add/pool/', add_pool, name='add'),
    path('account/info', account_info, name='ac_info'),
    path('account/info/leave/<int:pool_id>', leave_confirm, name='leave'),
    path('account/info/delete/<int:pool_id>', delete_confirm, name='delete'),
]
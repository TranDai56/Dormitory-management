from django.urls import path
from . import views

urlpatterns = [
    path('', views.danh_sach_khach, name='danh_sach_khach'),
    path('them-khach/', views.them_khach, name='them_khach'),
    path('ghi-nhan-luot-tham/', views.ghi_nhan_luot_tham, name='ghi_nhan_luot_tham'),
    path('xoa-luot-tham/<int:ma_luot>/', views.xoa_luot_tham, name='xoa_luot_tham'),
]

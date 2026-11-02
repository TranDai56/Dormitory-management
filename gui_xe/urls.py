from django.urls import path
from . import views

urlpatterns = [
    path('', views.danh_sach_xe, name='danh_sach_xe'),
    path('dang-ky/', views.dang_ky_xe, name='dang_ky_xe'),
    path('<str:bien_so>/sua/', views.sua_xe, name='sua_xe'),
    path('<str:bien_so>/xoa/', views.xoa_xe, name='xoa_xe'),

    # Lượt gửi xe
    path('luot-gui/', views.danh_sach_luot_gui, name='danh_sach_luot_gui'),
    path('ghi-nhan-luot/', views.ghi_nhan_luot_gui, name='ghi_nhan_luot_gui'),
    path('check-out/<int:ma_luot>/', views.check_out_xe, name='check_out_xe'),
]

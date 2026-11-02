from django.urls import path
from . import views

urlpatterns = [
    path('', views.danh_sach_dich_vu, name='danh_sach_dich_vu'),
    path('them/', views.them_dich_vu, name='them_dich_vu'),
    path('<str:ma_dv>/sua/', views.sua_dich_vu, name='sua_dich_vu'),
    path('<str:ma_dv>/xoa/', views.xoa_dich_vu, name='xoa_dich_vu'),
]

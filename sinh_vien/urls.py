from django.urls import path
from . import views

urlpatterns = [
    path('', views.danh_sach_sinh_vien, name='danh_sach_sinh_vien'),
    path('them/', views.them_sinh_vien, name='them_sinh_vien'),
    path('<str:masv>/', views.chi_tiet_sinh_vien, name='chi_tiet_sinh_vien'),
    path('<str:masv>/sua/', views.sua_sinh_vien, name='sua_sinh_vien'),
    path('<str:masv>/xoa/', views.xoa_sinh_vien, name='xoa_sinh_vien'),
]

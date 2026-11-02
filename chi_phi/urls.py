from django.urls import path
from . import views

urlpatterns = [
    path('', views.danh_sach_chi_phi, name='danh_sach_chi_phi'),
    path('them/', views.them_su_dung_dich_vu, name='them_su_dung_dich_vu'),
    path('<int:ma_lan>/xoa/', views.xoa_su_dung_dich_vu, name='xoa_su_dung_dich_vu'),
]

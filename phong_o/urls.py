from django.urls import path
from . import views

urlpatterns = [
    path('', views.danh_sach_phong, name='danh_sach_phong'),
    path('them/', views.them_phong, name='them_phong'),
    path('xep-phong/', views.xep_phong, name='xep_phong'),
    path('tra-phong/<int:ma_dang_ky>/', views.tra_phong, name='tra_phong'),
    path('<str:so_phong>/', views.chi_tiet_phong, name='chi_tiet_phong'),
    path('<str:so_phong>/sua/', views.sua_phong, name='sua_phong'),
    path('<str:so_phong>/xoa/', views.xoa_phong, name='xoa_phong'),
]

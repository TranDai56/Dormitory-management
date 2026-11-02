"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('bao-cao/', views.bao_cao, name='bao_cao'),
    path('in-hoa-don/<str:masv>/', views.in_hoa_don, name='in_hoa_don'),
    path('tra-cuu/', views.tra_cuu_sinh_vien, name='tra_cuu_sinh_vien'),

    path('admin/', admin.site.urls),
    path('sinh-vien/', include('sinh_vien.urls')),
    path('phong-o/', include('phong_o.urls')),
    path('dich-vu/', include('dich_vu.urls')),
    path('gui-xe/', include('gui_xe.urls')),
    path('khach-tham/', include('khach_tham.urls')),
    path('chi-phi/', include('chi_phi.urls')),

    # Tương thích với các đường dẫn cũ
    path('sinh_vien/', include('sinh_vien.urls')),
    path('phong_o/', include('phong_o.urls')),
    path('dich_vu/', include('dich_vu.urls')),
    path('gui_xe/', include('gui_xe.urls')),
    path('khach_tham/', include('khach_tham.urls')),
    path('chi_phi/', include('chi_phi.urls')),
]

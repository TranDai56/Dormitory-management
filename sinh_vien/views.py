from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from datetime import date
from .models import SinhVien, Nguoi
from phong_o.models import DangKyO
from gui_xe.models import XeThang
from chi_phi.models import SuDungDichVu
from khach_tham.models import LuotTham


def danh_sach_sinh_vien(request):
    """Danh sách sinh viên có tìm kiếm và bộ lọc."""
    tu_khoa = request.GET.get('q', '').strip()
    ds_sinh_vien = SinhVien.objects.select_related('nguoi').all()

    if tu_khoa:
        ds_sinh_vien = ds_sinh_vien.filter(
            Q(masv__icontains=tu_khoa) |
            Q(nguoi__hoten__icontains=tu_khoa) |
            Q(nguoi__socmt__icontains=tu_khoa) |
            Q(lop__icontains=tu_khoa) |
            Q(quequan__icontains=tu_khoa)
        )

    context = {
        'ds_sinh_vien': ds_sinh_vien,
        'tu_khoa': tu_khoa,
        'tong_so': ds_sinh_vien.count(),
    }
    return render(request, 'sinh_vien/sinh_vien.html', context)


def them_sinh_vien(request):
    """Thêm mới sinh viên cùng thông tin người (Transaction an toàn)."""
    if request.method == 'POST':
        socmt = request.POST.get('socmt', '').strip()
        hoten = request.POST.get('hoten', '').strip()
        ngaysinh_str = request.POST.get('ngaysinh', '').strip()
        masv = request.POST.get('masv', '').strip()
        lop = request.POST.get('lop', '').strip()
        quequan = request.POST.get('quequan', '').strip()

        if not socmt or not hoten or not masv:
            messages.error(request, "Vui lòng nhập đầy đủ Số CMT, Họ tên và Mã sinh viên!")
            return render(request, 'sinh_vien/them.html', {'post': request.POST})

        # Kiểm tra trùng CMT
        if Nguoi.objects.filter(socmt=socmt).exists():
            messages.error(request, f"Số CMT/CCCD '{socmt}' đã tồn tại trong hệ thống!")
            return render(request, 'sinh_vien/them.html', {'post': request.POST})

        # Kiểm tra trùng Mã SV
        if SinhVien.objects.filter(masv=masv).exists():
            messages.error(request, f"Mã sinh viên '{masv}' đã tồn tại trong hệ thống!")
            return render(request, 'sinh_vien/them.html', {'post': request.POST})

        ngaysinh = ngaysinh_str if ngaysinh_str else None

        try:
            with transaction.atomic():
                nguoi = Nguoi.objects.create(
                    socmt=socmt,
                    hoten=hoten,
                    ngaysinh=ngaysinh
                )
                SinhVien.objects.create(
                    nguoi=nguoi,
                    masv=masv,
                    lop=lop,
                    quequan=quequan
                )
            messages.success(request, f"Đã thêm thành công sinh viên: {hoten} ({masv})!")
            return redirect('danh_sach_sinh_vien')
        except Exception as e:
            messages.error(request, f"Lỗi khi thêm sinh viên: {str(e)}")
            return render(request, 'sinh_vien/them.html', {'post': request.POST})

    return render(request, 'sinh_vien/them.html')


def sua_sinh_vien(request, masv):
    """Chỉnh sửa thông tin sinh viên."""
    sinh_vien = get_object_or_404(SinhVien.objects.select_related('nguoi'), masv=masv)

    if request.method == 'POST':
        hoten = request.POST.get('hoten', '').strip()
        ngaysinh_str = request.POST.get('ngaysinh', '').strip()
        lop = request.POST.get('lop', '').strip()
        quequan = request.POST.get('quequan', '').strip()

        if not hoten:
            messages.error(request, "Họ tên không được để trống!")
            return render(request, 'sinh_vien/sua.html', {'sv': sinh_vien})

        try:
            with transaction.atomic():
                sinh_vien.nguoi.hoten = hoten
                sinh_vien.nguoi.ngaysinh = ngaysinh_str if ngaysinh_str else None
                sinh_vien.nguoi.save()

                sinh_vien.lop = lop
                sinh_vien.quequan = quequan
                sinh_vien.save()

            messages.success(request, f"Đã cập nhật thông tin sinh viên {sinh_vien.masv} thành công!")
            return redirect('chi_tiet_sinh_vien', masv=sinh_vien.masv)
        except Exception as e:
            messages.error(request, f"Lỗi khi cập nhật: {str(e)}")

    return render(request, 'sinh_vien/sua.html', {'sv': sinh_vien})


def chi_tiet_sinh_vien(request, masv):
    """Xem hồ sơ chi tiết của sinh viên."""
    sinh_vien = get_object_or_404(SinhVien.objects.select_related('nguoi'), masv=masv)
    
    # Lịch sử ở phòng
    lich_su_phong = DangKyO.objects.filter(sinh_vien=sinh_vien).select_related('phong').order_by('-ngaybatdau')
    phong_hien_tai = sinh_vien.phong_hien_tai()

    # Xe tháng
    ds_xe = XeThang.objects.filter(sinh_vien=sinh_vien)

    # Dịch vụ sử dụng
    ds_su_dung = SuDungDichVu.objects.filter(sinh_vien=sinh_vien).select_related('dich_vu').order_by('-thoigiansudung')[:15]

    # Khách thăm
    ds_khach = LuotTham.objects.filter(sinh_vien=sinh_vien).select_related('khach__nguoi').order_by('-thoigianden')[:15]

    context = {
        'sv': sinh_vien,
        'phong_hien_tai': phong_hien_tai,
        'lich_su_phong': lich_su_phong,
        'ds_xe': ds_xe,
        'ds_su_dung': ds_su_dung,
        'ds_khach': ds_khach,
    }
    return render(request, 'sinh_vien/chi_tiet.html', context)


def xoa_sinh_vien(request, masv):
    """Xóa sinh viên."""
    sinh_vien = get_object_or_404(SinhVien.objects.select_related('nguoi'), masv=masv)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                socmt = sinh_vien.nguoi.socmt
                sinh_vien.delete()
                Nguoi.objects.filter(socmt=socmt).delete()
            messages.success(request, f"Đã xóa sinh viên {masv} thành công!")
        except Exception as e:
            messages.error(request, f"Không thể xóa sinh viên do có dữ liệu liên kết ràng buộc: {str(e)}")
        return redirect('danh_sach_sinh_vien')

    return render(request, 'sinh_vien/xoa.html', {'sv': sinh_vien})

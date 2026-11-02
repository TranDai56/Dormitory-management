from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from datetime import datetime
from .models import Khach, LuotTham
from sinh_vien.models import Nguoi, SinhVien


def danh_sach_khach(request):
    """Danh sách khách đến thăm và nhật ký các lượt đến chơi tại KTX."""
    ds_khach = Khach.objects.select_related('nguoi').all()
    ds_luot_tham = LuotTham.objects.select_related('khach__nguoi', 'sinh_vien__nguoi').order_by('-thoigianden')

    # Lọc theo SV nếu có
    masv = request.GET.get('masv', '').strip()
    if masv:
        ds_luot_tham = ds_luot_tham.filter(sinh_vien__masv=masv)

    all_sv = SinhVien.objects.select_related('nguoi').all()

    context = {
        'ds_khach': ds_khach,
        'ds_luot_tham': ds_luot_tham,
        'all_sv': all_sv,
        'selected_masv': masv,
        'tong_khach': ds_khach.count(),
        'tong_luot': ds_luot_tham.count(),
    }
    return render(request, 'khach/khach_tham.html', context)


def them_khach(request):
    """Đăng ký thông tin khách mới đến KTX."""
    if request.method == 'POST':
        socmt = request.POST.get('socmt', '').strip()
        hoten = request.POST.get('hoten', '').strip()
        ngaysinh_str = request.POST.get('ngaysinh', '').strip()
        makhach = request.POST.get('makhach', '').strip()

        if not socmt or not hoten or not makhach:
            messages.error(request, "Vui lòng nhập đầy đủ Số CMT, Họ tên và Mã khách!")
            return render(request, 'khach/them_khach.html', {'post': request.POST})

        if Nguoi.objects.filter(socmt=socmt).exists():
            messages.error(request, f"Số CMT/CCCD '{socmt}' đã tồn tại trong hệ thống!")
            return render(request, 'khach/them_khach.html', {'post': request.POST})

        if Khach.objects.filter(makhach=makhach).exists():
            messages.error(request, f"Mã khách '{makhach}' đã tồn tại!")
            return render(request, 'khach/them_khach.html', {'post': request.POST})

        try:
            with transaction.atomic():
                nguoi = Nguoi.objects.create(
                    socmt=socmt,
                    hoten=hoten,
                    ngaysinh=ngaysinh_str if ngaysinh_str else None
                )
                Khach.objects.create(
                    nguoi=nguoi,
                    makhach=makhach
                )
            messages.success(request, f"Đã đăng ký thông tin khách {hoten} ({makhach}) thành công!")
            return redirect('danh_sach_khach')
        except Exception as e:
            messages.error(request, f"Lỗi khi lưu khách: {str(e)}")

    return render(request, 'khach/them_khach.html')


def ghi_nhan_luot_tham(request):
    """Ghi nhận lượt khách đến thăm sinh viên."""
    all_khach = Khach.objects.select_related('nguoi').all()
    all_sv = SinhVien.objects.select_related('nguoi').all()

    if request.method == 'POST':
        makhach = request.POST.get('makhach', '').strip()
        masv = request.POST.get('masv', '').strip()
        thoigianden_str = request.POST.get('thoigianden', '').strip()

        khach = get_object_or_404(Khach, makhach=makhach)
        sinh_vien = get_object_or_404(SinhVien, masv=masv)

        try:
            thoigianden = datetime.strptime(thoigianden_str, '%Y-%m-%dT%H:%M') if thoigianden_str else datetime.now()
            LuotTham.objects.create(
                khach=khach,
                sinh_vien=sinh_vien,
                thoigianden=thoigianden
            )
            messages.success(request, f"Đã ghi nhận khách {khach.hoten} đến thăm sinh viên {sinh_vien.hoten}!")
            return redirect('danh_sach_khach')
        except Exception as e:
            messages.error(request, f"Lỗi: {str(e)}")

    context = {
        'all_khach': all_khach,
        'all_sv': all_sv,
        'now_str': datetime.now().strftime('%Y-%m-%dT%H:%M'),
    }
    return render(request, 'khach/them_luot_tham.html', context)


def xoa_luot_tham(request, ma_luot):
    """Xóa bản ghi lượt thăm."""
    luot = get_object_or_404(LuotTham, maluottham=ma_luot)
    if request.method == 'POST':
        luot.delete()
        messages.success(request, f"Đã xóa lượt thăm #{ma_luot}!")
        return redirect('danh_sach_khach')

    return render(request, 'khach/xoa_luot_tham.html', {'luot': luot})

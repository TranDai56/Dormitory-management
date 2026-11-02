from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from datetime import datetime
from .models import SuDungDichVu
from sinh_vien.models import SinhVien
from dich_vu.models import DichVu


def danh_sach_chi_phi(request):
    """Danh sách nhật ký sinh viên sử dụng dịch vụ trong KTX."""
    ds_chi_phi = SuDungDichVu.objects.select_related('sinh_vien__nguoi', 'dich_vu').order_by('-thoigiansudung')

    # Lọc theo SV nếu có
    masv = request.GET.get('masv', '').strip()
    if masv:
        ds_chi_phi = ds_chi_phi.filter(sinh_vien__masv=masv)

    # Lọc theo DV nếu có
    madv = request.GET.get('madv', '').strip()
    if madv:
        ds_chi_phi = ds_chi_phi.filter(dich_vu__madichvu=madv)

    all_sv = SinhVien.objects.select_related('nguoi').all()
    all_dv = DichVu.objects.all()

    context = {
        'ds_chi_phi': ds_chi_phi,
        'all_sv': all_sv,
        'all_dv': all_dv,
        'selected_masv': masv,
        'selected_madv': madv,
        'tong_luot': ds_chi_phi.count(),
    }
    return render(request, 'chi_phi/chi_phi.html', context)


def them_su_dung_dich_vu(request):
    """Ghi nhận sinh viên sử dụng một dịch vụ."""
    all_sv = SinhVien.objects.select_related('nguoi').all()
    all_dv = DichVu.objects.all()

    if request.method == 'POST':
        masv = request.POST.get('masv', '').strip()
        madv = request.POST.get('madv', '').strip()
        soluong_str = request.POST.get('soluong', '1').strip()
        thoigian_str = request.POST.get('thoigiansudung', '').strip()

        sinh_vien = get_object_or_404(SinhVien, masv=masv)
        dich_vu = get_object_or_404(DichVu, madichvu=madv)

        try:
            soluong = int(soluong_str)
            if soluong <= 0:
                raise ValueError("Số lượng phải lớn hơn 0")

            if thoigian_str:
                thoigiansudung = datetime.strptime(thoigian_str, '%Y-%m-%dT%H:%M')
            else:
                thoigiansudung = datetime.now()

            sd = SuDungDichVu.objects.create(
                sinh_vien=sinh_vien,
                dich_vu=dich_vu,
                soluong=soluong,
                thoigiansudung=thoigiansudung
            )
            messages.success(
                request,
                f"Đã ghi nhận: {sinh_vien.hoten} dùng '{dich_vu.tendichvu}' x {soluong} = {sd.thanh_tien():,.0f} đ!"
            )
            return redirect('danh_sach_chi_phi')
        except ValueError as e:
            messages.error(request, f"Dữ liệu nhập không hợp lệ: {str(e)}")

    context = {
        'all_sv': all_sv,
        'all_dv': all_dv,
        'now_str': datetime.now().strftime('%Y-%m-%dT%H:%M'),
    }
    return render(request, 'chi_phi/them.html', context)


def xoa_su_dung_dich_vu(request, ma_lan):
    """Xóa bản ghi sử dụng dịch vụ."""
    sd = get_object_or_404(SuDungDichVu, malansudung=ma_lan)
    if request.method == 'POST':
        sd.delete()
        messages.success(request, f"Đã xóa lượt sử dụng dịch vụ #{ma_lan} thành công!")
        return redirect('danh_sach_chi_phi')

    return render(request, 'chi_phi/xoa.html', {'sd': sd})

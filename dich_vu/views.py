from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import DichVu
from chi_phi.models import SuDungDichVu


def danh_sach_dich_vu(request):
    """Danh mục các dịch vụ ký túc xá."""
    ds_dich_vu = DichVu.objects.all()

    context = {
        'ds_dich_vu': ds_dich_vu,
        'tong_so': ds_dich_vu.count(),
    }
    return render(request, 'dich_vu/dich_vu.html', context)


def them_dich_vu(request):
    """Thêm dịch vụ mới."""
    if request.method == 'POST':
        madichvu = request.POST.get('madichvu', '').strip()
        tendichvu = request.POST.get('tendichvu', '').strip()
        dongia_str = request.POST.get('dongia', '').strip()

        if not madichvu or not tendichvu or not dongia_str:
            messages.error(request, "Vui lòng nhập đầy đủ Mã dịch vụ, Tên dịch vụ và Đơn giá!")
            return render(request, 'dich_vu/them.html', {'post': request.POST})

        if DichVu.objects.filter(madichvu=madichvu).exists():
            messages.error(request, f"Mã dịch vụ '{madichvu}' đã tồn tại!")
            return render(request, 'dich_vu/them.html', {'post': request.POST})

        try:
            dongia = int(dongia_str)
            DichVu.objects.create(
                madichvu=madichvu,
                tendichvu=tendichvu,
                dongia=dongia
            )
            messages.success(request, f"Đã thêm dịch vụ '{tendichvu}' thành công!")
            return redirect('danh_sach_dich_vu')
        except ValueError:
            messages.error(request, "Đơn giá phải là số nguyên dương!")

    return render(request, 'dich_vu/them.html')


def sua_dich_vu(request, ma_dv):
    """Chỉnh sửa thông tin dịch vụ."""
    dich_vu = get_object_or_404(DichVu, madichvu=ma_dv)

    if request.method == 'POST':
        tendichvu = request.POST.get('tendichvu', '').strip()
        dongia_str = request.POST.get('dongia', '').strip()

        if not tendichvu or not dongia_str:
            messages.error(request, "Vui lòng nhập đầy đủ Tên dịch vụ và Đơn giá!")
            return render(request, 'dich_vu/sua.html', {'dv': dich_vu})

        try:
            dongia = int(dongia_str)
            dich_vu.tendichvu = tendichvu
            dich_vu.dongia = dongia
            dich_vu.save()
            messages.success(request, f"Đã cập nhật dịch vụ '{tendichvu}' thành công!")
            return redirect('danh_sach_dich_vu')
        except ValueError:
            messages.error(request, "Đơn giá phải là số nguyên hợp lệ!")

    return render(request, 'dich_vu/sua.html', {'dv': dich_vu})


def xoa_dich_vu(request, ma_dv):
    """Xóa dịch vụ."""
    dich_vu = get_object_or_404(DichVu, madichvu=ma_dv)

    if request.method == 'POST':
        if SuDungDichVu.objects.filter(dich_vu=dich_vu).exists():
            messages.error(request, f"Không thể xóa dịch vụ '{dich_vu.tendichvu}' vì đã có sinh viên sử dụng!")
            return redirect('danh_sach_dich_vu')

        try:
            dich_vu.delete()
            messages.success(request, f"Đã xóa dịch vụ '{dich_vu.tendichvu}' thành công!")
        except Exception as e:
            messages.error(request, f"Lỗi khi xóa dịch vụ: {str(e)}")
        return redirect('danh_sach_dich_vu')

    return render(request, 'dich_vu/xoa.html', {'dv': dich_vu})

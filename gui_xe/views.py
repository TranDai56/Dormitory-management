from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from datetime import date, datetime
from .models import XeThang, LuotGuiXe
from sinh_vien.models import SinhVien
from config.services import kiem_tra_so_xe_sinh_vien, tinh_phi_luot_xe_moi


def danh_sach_xe(request):
    """Danh sách các xe vé tháng của sinh viên."""
    today = date.today()
    ds_xe = XeThang.objects.select_related('sinh_vien__nguoi').order_by('-ngaydangky')

    masv = request.GET.get('masv', '').strip()
    if masv:
        ds_xe = ds_xe.filter(sinh_vien__masv=masv)

    context = {
        'ds_xe': ds_xe,
        'today': today,
        'tong_xe': ds_xe.count(),
        'xe_hieu_luc': ds_xe.filter(ngayhethan__gte=today).count(),
    }
    return render(request, 'gui_xe/bien_so.html', context)


def dang_ky_xe(request):
    """
    Đăng ký xe vé tháng mới cho sinh viên.
    RÀNG BUỘC THEO ĐỀ BÀI: Mỗi sinh viên chỉ được đăng ký tối đa 2 xe vé tháng còn hiệu lực.
    """
    today = date.today()
    all_sv = SinhVien.objects.select_related('nguoi').all()

    if request.method == 'POST':
        masv = request.POST.get('masv', '').strip()
        bienso = request.POST.get('bienso', '').strip().upper()
        loaixe = request.POST.get('loaixe', '').strip()
        ngaydangky_str = request.POST.get('ngaydangky', '').strip()
        ngayhethan_str = request.POST.get('ngayhethan', '').strip()
        dongia_str = request.POST.get('dongiathang', '100000').strip()

        sinh_vien = get_object_or_404(SinhVien, masv=masv)

        if not bienso or not ngaydangky_str or not ngayhethan_str:
            messages.error(request, "Vui lòng điền đầy đủ Biển số, Ngày đăng ký và Ngày hết hạn!")
            return render(request, 'gui_xe/dang_ky_xe.html', {'all_sv': all_sv, 'post': request.POST})

        # KIỂM TRA RÀNG BUỘC TỐI ĐA 2 XE
        so_xe, duoc_phep = kiem_tra_so_xe_sinh_vien(sinh_vien)
        if not duoc_phep:
            messages.error(
                request,
                f"LỖI RÀNG BUỘC: Sinh viên {sinh_vien.hoten} ({sinh_vien.masv}) đã đăng ký đủ {so_xe}/2 xe vé tháng còn hiệu lực. Không thể đăng ký thêm!"
            )
            return render(request, 'gui_xe/dang_ky_xe.html', {'all_sv': all_sv, 'post': request.POST})

        # Kiểm tra trùng biển số
        if XeThang.objects.filter(bienso=bienso).exists():
            messages.error(request, f"Biển số xe '{bienso}' đã được đăng ký trong hệ thống!")
            return render(request, 'gui_xe/dang_ky_xe.html', {'all_sv': all_sv, 'post': request.POST})

        try:
            ngaydangky = datetime.strptime(ngaydangky_str, '%Y-%m-%d').date()
            ngayhethan = datetime.strptime(ngayhethan_str, '%Y-%m-%d').date()
            dongia = int(dongia_str)

            if ngayhethan < ngaydangky:
                messages.error(request, "Ngày hết hạn phải sau ngày đăng ký!")
                return render(request, 'gui_xe/dang_ky_xe.html', {'all_sv': all_sv, 'post': request.POST})

            XeThang.objects.create(
                bienso=bienso,
                sinh_vien=sinh_vien,
                loaixe=loaixe,
                ngaydangky=ngaydangky,
                ngayhethan=ngayhethan,
                dongiathang=dongia
            )
            messages.success(request, f"Đã đăng ký thành công xe vé tháng biển số {bienso} cho sinh viên {sinh_vien.hoten}!")
            return redirect('danh_sach_xe')
        except ValueError as e:
            messages.error(request, f"Dữ liệu không hợp lệ: {str(e)}")

    context = {
        'all_sv': all_sv,
        'today': today,
        'default_end': today.replace(year=today.year + 1),
    }
    return render(request, 'gui_xe/dang_ky_xe.html', context)


def sua_xe(request, bien_so):
    """Chỉnh sửa thông tin xe hoặc gia hạn vé tháng."""
    xe = get_object_or_404(XeThang.objects.select_related('sinh_vien__nguoi'), bienso=bien_so)

    if request.method == 'POST':
        loaixe = request.POST.get('loaixe', '').strip()
        ngayhethan_str = request.POST.get('ngayhethan', '').strip()
        dongia_str = request.POST.get('dongiathang', '').strip()

        try:
            xe.loaixe = loaixe
            xe.ngayhethan = datetime.strptime(ngayhethan_str, '%Y-%m-%d').date()
            xe.dongiathang = int(dongia_str)
            xe.save()
            messages.success(request, f"Đã cập nhật thông tin xe {bien_so} thành công!")
            return redirect('danh_sach_xe')
        except ValueError as e:
            messages.error(request, f"Lỗi dữ liệu: {str(e)}")

    return render(request, 'gui_xe/sua_xe.html', {'xe': xe})


def xoa_xe(request, bien_so):
    """Hủy đăng ký xe vé tháng."""
    xe = get_object_or_404(XeThang, bienso=bien_so)

    if request.method == 'POST':
        try:
            xe.delete()
            messages.success(request, f"Đã hủy vé tháng xe {bien_so} thành công!")
        except Exception as e:
            messages.error(request, f"Không thể xóa xe do có dữ liệu lượt gửi phát sinh liên kết: {str(e)}")
        return redirect('danh_sach_xe')

    return render(request, 'gui_xe/xoa_xe.html', {'xe': xe})


# ==========================================
# LƯỢT GỬI / LẤY XE
# ==========================================
def danh_sach_luot_gui(request):
    """Danh sách nhật ký các lượt gửi/lấy xe."""
    ds_luot = LuotGuiXe.objects.select_related('xe_thang__sinh_vien__nguoi').order_by('-ngay', '-thoigianlay', '-maluot')

    # Lọc theo ngày
    ngay_str = request.GET.get('ngay', '').strip()
    if ngay_str:
        try:
            ngay_loc = datetime.strptime(ngay_str, '%Y-%m-%d').date()
            ds_luot = ds_luot.filter(ngay=ngay_loc)
        except ValueError:
            pass

    # Lọc theo biển số
    bienso = request.GET.get('bienso', '').strip()
    if bienso:
        ds_luot = ds_luot.filter(xe_thang__bienso__icontains=bienso)

    context = {
        'ds_luot': ds_luot,
        'ngay_loc': ngay_str,
        'bienso': bienso,
        'tong_so': ds_luot.count(),
    }
    return render(request, 'gui_xe/luot_gui_xe.html', context)


def ghi_nhan_luot_gui(request):
    """
    Ghi nhận lượt gửi/lấy xe vé tháng.
    QUY TẮC TÍNH PHÍ:
    Mỗi ngày xe vé tháng chỉ được lấy ra/gửi vào 2 lần miễn phí.
    Từ lần thứ 3 trong ngày phát sinh 3.000đ/lượt.
    """
    all_xe = XeThang.objects.select_related('sinh_vien__nguoi').filter(ngayhethan__gte=date.today())

    if request.method == 'POST':
        bienso = request.POST.get('bienso', '').strip()
        thoigianlay_str = request.POST.get('thoigianlay', '').strip()
        ngay_str = request.POST.get('ngay', '').strip()

        xe = get_object_or_404(XeThang, bienso=bienso)
        ngay_ghi = datetime.strptime(ngay_str, '%Y-%m-%d').date() if ngay_str else date.today()

        thoigianlay = datetime.strptime(thoigianlay_str, '%Y-%m-%dT%H:%M') if thoigianlay_str else datetime.now()

        # TỰ ĐỘNG TÍNH PHÍ PHÁT SINH
        phi_phat_sinh, stt_luot = tinh_phi_luot_xe_moi(bienso, ngay_ghi)

        LuotGuiXe.objects.create(
            xe_thang=xe,
            ngay=ngay_ghi,
            thoigianlay=thoigianlay,
            thoigiangui=None,
            sotienphatsinh=phi_phat_sinh
        )

        if phi_phat_sinh > 0:
            messages.warning(
                request,
                f"Đã ghi nhận lượt thứ {stt_luot} trong ngày của xe {bienso}. Vượt quá 2 lượt miễn phí -> Tính phí phát sinh: 3.000 đ!"
            )
        else:
            messages.success(
                request,
                f"Đã ghi nhận lượt thứ {stt_luot} trong ngày của xe {bienso} (Miễn phí trong hạn 2 lượt/ngày)!"
            )
        return redirect('danh_sach_luot_gui')

    context = {
        'all_xe': all_xe,
        'now_str': datetime.now().strftime('%Y-%m-%dT%H:%M'),
        'today_str': date.today().strftime('%Y-%m-%d'),
    }
    return render(request, 'gui_xe/them_luot.html', context)


def check_out_xe(request, ma_luot):
    """Ghi nhận thời gian gửi lại xe vào bãi (Check-out)."""
    luot = get_object_or_404(LuotGuiXe, maluot=ma_luot)
    luot.thoigiangui = datetime.now()
    luot.save()
    messages.success(request, f"Đã ghi nhận thời gian gửi xe vào bãi cho lượt #{ma_luot}!")
    return redirect('danh_sach_luot_gui')

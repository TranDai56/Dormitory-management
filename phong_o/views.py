from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count, Q
from datetime import date
from .models import Phong, DangKyO
from sinh_vien.models import SinhVien
from config.services import kiem_tra_suc_chua_phong


def danh_sach_phong(request):
    """Danh sách các phòng ở với thông tin sức chứa và tỷ lệ lấp đầy."""
    today = date.today()
    ds_phong = Phong.objects.all()

    # Thống kê nhanh
    tong_phong = ds_phong.count()
    tong_cho = sum(p.songuoitoida for p in ds_phong)
    dang_o = DangKyO.objects.filter(
        ngaybatdau__lte=today
    ).filter(
        Q(ngayketthuc__isnull=True) | Q(ngayketthuc__gte=today)
    ).count()

    context = {
        'ds_phong': ds_phong,
        'tong_phong': tong_phong,
        'tong_cho': tong_cho,
        'dang_o': dang_o,
        'con_trong': max(0, tong_cho - dang_o),
    }
    return render(request, 'phong_o/phong_o.html', context)


def them_phong(request):
    """Thêm phòng ở mới vào ký túc xá."""
    if request.method == 'POST':
        sophong = request.POST.get('sophong', '').strip()
        loaiphong = request.POST.get('loaiphong', '').strip()
        dongia_str = request.POST.get('dongia', '').strip()
        songuoitoida_str = request.POST.get('songuoitoida', '').strip()

        if not sophong or not dongia_str or not songuoitoida_str:
            messages.error(request, "Vui lòng nhập đầy đủ Số phòng, Đơn giá và Số người tối đa!")
            return render(request, 'phong_o/them.html', {'post': request.POST})

        if Phong.objects.filter(sophong=sophong).exists():
            messages.error(request, f"Phòng số '{sophong}' đã tồn tại!")
            return render(request, 'phong_o/them.html', {'post': request.POST})

        try:
            dongia = int(dongia_str)
            songuoitoida = int(songuoitoida_str)
            if songuoitoida <= 0 or dongia < 0:
                raise ValueError("Số người hoặc đơn giá không hợp lệ")

            Phong.objects.create(
                sophong=sophong,
                loaiphong=loaiphong,
                dongia=dongia,
                songuoitoida=songuoitoida
            )
            messages.success(request, f"Đã thêm thành công Phòng {sophong}!")
            return redirect('danh_sach_phong')
        except ValueError as e:
            messages.error(request, f"Dữ liệu nhập không hợp lệ: {str(e)}")

    return render(request, 'phong_o/them.html')


def sua_phong(request, so_phong):
    """Chỉnh sửa thông tin phòng."""
    phong = get_object_or_404(Phong, sophong=so_phong)

    if request.method == 'POST':
        loaiphong = request.POST.get('loaiphong', '').strip()
        dongia_str = request.POST.get('dongia', '').strip()
        songuoitoida_str = request.POST.get('songuoitoida', '').strip()

        try:
            dongia = int(dongia_str)
            songuoitoida = int(songuoitoida_str)

            # Kiểm tra xem số người tối đa mới có nhỏ hơn số người đang ở hiện tại không
            hien_tai = phong.so_nguoi_hien_tai()
            if songuoitoida < hien_tai:
                messages.error(request, f"Không thể giảm sức chứa xuống {songuoitoida} vì hiện tại đang có {hien_tai} sinh viên ở trong phòng!")
                return render(request, 'phong_o/sua.html', {'phong': phong})

            phong.loaiphong = loaiphong
            phong.dongia = dongia
            phong.songuoitoida = songuoitoida
            phong.save()

            messages.success(request, f"Đã cập nhật Phòng {phong.sophong} thành công!")
            return redirect('chi_tiet_phong', so_phong=phong.sophong)
        except ValueError:
            messages.error(request, "Đơn giá hoặc Số người tối đa phải là số nguyên dương!")

    return render(request, 'phong_o/sua.html', {'phong': phong})


def xoa_phong(request, so_phong):
    """Xóa phòng khỏi hệ thống."""
    phong = get_object_or_404(Phong, sophong=so_phong)

    if request.method == 'POST':
        # Kiểm tra nếu đang có người ở
        if phong.so_nguoi_hien_tai() > 0:
            messages.error(request, f"Phòng {so_phong} hiện đang có sinh viên cư trú, không thể xóa!")
            return redirect('chi_tiet_phong', so_phong=so_phong)

        try:
            phong.delete()
            messages.success(request, f"Đã xóa Phòng {so_phong} thành công!")
            return redirect('danh_sach_phong')
        except Exception as e:
            messages.error(request, f"Không thể xóa phòng do ràng buộc dữ liệu: {str(e)}")
            return redirect('chi_tiet_phong', so_phong=so_phong)

    return render(request, 'phong_o/xoa.html', {'phong': phong})


def chi_tiet_phong(request, so_phong):
    """Chi tiết phòng ở, danh sách sinh viên đang ở và lịch sử cư trú."""
    phong = get_object_or_404(Phong, sophong=so_phong)
    today = date.today()

    # Sinh viên đang ở
    sv_dang_o = DangKyO.objects.filter(
        phong=phong,
        ngaybatdau__lte=today
    ).filter(
        Q(ngayketthuc__isnull=True) | Q(ngayketthuc__gte=today)
    ).select_related('sinh_vien__nguoi')

    # Lịch sử từng ở
    lich_su_o = DangKyO.objects.filter(
        phong=phong
    ).filter(
        ngayketthuc__lt=today
    ).select_related('sinh_vien__nguoi').order_by('-ngayketthuc')

    context = {
        'phong': phong,
        'sv_dang_o': sv_dang_o,
        'lich_su_o': lich_su_o,
        'so_nguoi_hien_tai': phong.so_nguoi_hien_tai(),
        'con_trong': phong.con_trong(),
        'da_day': phong.da_day(),
    }
    return render(request, 'phong_o/chi_tiet.html', context)


def xep_phong(request):
    """
    Phân phòng / Xếp phòng cho sinh viên.
    KIỂM TRA RÀNG BUỘC THEO ĐỀ BÀI:
    1. Số người ở trong phòng không được vượt quá SoNguoiToiDa.
    2. Một sinh viên tại một thời điểm chỉ ở 1 phòng (nếu đang ở phòng khác phải cảnh báo/trả phòng).
    """
    today = date.today()
    ds_phong = Phong.objects.all()
    ds_sinh_vien = SinhVien.objects.select_related('nguoi').all()

    if request.method == 'POST':
        masv = request.POST.get('masv', '').strip()
        sophong = request.POST.get('sophong', '').strip()
        ngaybatdau_str = request.POST.get('ngaybatdau', '').strip()

        sinh_vien = get_object_or_404(SinhVien, masv=masv)
        phong, hien_tai, toi_da, con_trong, da_day = kiem_tra_suc_chua_phong(sophong)

        if not phong:
            messages.error(request, "Phòng được chọn không tồn tại!")
            return redirect('xep_phong')

        # 1. RÀNG BUỘC SỨC CHỨA
        if da_day:
            messages.error(
                request,
                f"LỖI RÀNG BUỘC SỨC CHỨA: Phòng {sophong} đã đủ {hien_tai}/{toi_da} người, không thể xếp thêm sinh viên!"
            )
            return render(request, 'phong_o/xep_phong.html', {
                'ds_phong': ds_phong,
                'ds_sinh_vien': ds_sinh_vien,
                'post': request.POST
            })

        # 2. RÀNG BUỘC 1 SINH VIÊN CHỈ Ở 1 PHÒNG TẠI 1 THỜI ĐIỂM
        phong_cu = sinh_vien.phong_hien_tai()
        if phong_cu:
            # Tự động kết thúc đăng ký phòng cũ trước ngày bắt đầu phòng mới
            messages.warning(
                request,
                f"Sinh viên {sinh_vien.masv} đang ở Phòng {phong_cu.sophong}. Hệ thống đã tự động kết thúc hợp đồng phòng cũ để chuyển sang Phòng {sophong}."
            )
            DangKyO.objects.filter(
                sinh_vien=sinh_vien,
                ngayketthuc__isnull=True
            ).update(ngayketthuc=today)

        try:
            ngaybatdau = datetime.strptime(ngaybatdau_str, '%Y-%m-%d').date() if ngaybatdau_str else today
            DangKyO.objects.create(
                sinh_vien=sinh_vien,
                phong=phong,
                ngaybatdau=ngaybatdau,
                ngayketthuc=None
            )
            messages.success(request, f"Đã xếp thành công sinh viên {sinh_vien.hoten} ({sinh_vien.masv}) vào Phòng {sophong}!")
            return redirect('chi_tiet_phong', so_phong=sophong)
        except Exception as e:
            messages.error(request, f"Lỗi khi xếp phòng: {str(e)}")

    context = {
        'ds_phong': ds_phong,
        'ds_sinh_vien': ds_sinh_vien,
        'today': today,
    }
    return render(request, 'phong_o/xep_phong.html', context)


def tra_phong(request, ma_dang_ky):
    """Thủ tục trả phòng cho sinh viên."""
    dang_ky = get_object_or_404(DangKyO.objects.select_related('sinh_vien__nguoi', 'phong'), madangkyo=ma_dang_ky)
    so_phong = dang_ky.phong.sophong

    if request.method == 'POST':
        dang_ky.ngayketthuc = date.today()
        dang_ky.save()
        messages.success(request, f"Đã hoàn tất thủ tục trả phòng cho sinh viên {dang_ky.sinh_vien.hoten}!")
        return redirect('chi_tiet_phong', so_phong=so_phong)

    return render(request, 'phong_o/tra_phong.html', {'dk': dang_ky})

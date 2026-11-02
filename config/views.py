"""
Root views for Dashboard, Specialized Reports (4 queries), Invoice printing, and Student Portal.
"""

from datetime import date, datetime, timedelta
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Sum, Q

from sinh_vien.models import SinhVien, Nguoi
from phong_o.models import Phong, DangKyO
from dich_vu.models import DichVu
from gui_xe.models import XeThang, LuotGuiXe
from khach_tham.models import Khach, LuotTham
from chi_phi.models import SuDungDichVu

from .services import (
    tinh_chi_phi_sinh_vien_thang,
    thong_ke_su_dung_dich_vu_khoang_tg,
    thong_ke_khach_tham_ky,
    thong_ke_doanh_thu_thang,
    lay_khoang_thoi_gian_thang,
)


def dashboard(request):
    """
    Trang chủ Dashboard tổng quan:
    - Thống kê các chỉ số KPIs (Sinh viên, Phòng, Xe, Khách, Doanh thu).
    - Biểu đồ phân bổ doanh thu & lấp đầy phòng.
    - Danh sách hoạt động mới nhất.
    """
    today = date.today()
    current_month = today.month
    current_year = today.year

    # Thống kê cơ bản
    tong_sinh_vien = SinhVien.objects.count()
    tong_phong = Phong.objects.count()
    tong_xe_thang = XeThang.objects.filter(ngayhethan__gte=today).count()
    tong_khach = Khach.objects.count()

    # Tính toán sức chứa phòng
    phong_list = Phong.objects.all()
    tong_cho_o = sum(p.songuoitoida for p in phong_list)
    so_sv_dang_o = DangKyO.objects.filter(
        ngaybatdau__lte=today
    ).filter(
        Q(ngayketthuc__isnull=True) | Q(ngayketthuc__gte=today)
    ).count()

    cho_con_trong = max(0, tong_cho_o - so_sv_dang_o)
    ti_le_lap_day = int((so_sv_dang_o / tong_cho_o * 100)) if tong_cho_o > 0 else 0

    # Doanh thu tháng hiện tại
    bao_cao_dt = thong_ke_doanh_thu_thang(current_month, current_year)
    tong_doanh_thu_thang = bao_cao_dt['tong_doanh_thu']

    # Hoạt động gần đây
    luot_tham_moi = LuotTham.objects.select_related('khach__nguoi', 'sinh_vien__nguoi').order_by('-thoigianden')[:5]
    luot_xe_moi = LuotGuiXe.objects.select_related('xe_thang__sinh_vien__nguoi').order_by('-thoigianlay', '-maluot')[:5]
    dich_vu_moi = SuDungDichVu.objects.select_related('sinh_vien__nguoi', 'dich_vu').order_by('-thoigiansudung')[:5]

    # Chuẩn bị dữ liệu cho Chart.js
    chart_dv_labels = [item['ten'] for item in bao_cao_dt['danh_sach']]
    chart_dv_data = [item['doanh_thu'] for item in bao_cao_dt['danh_sach']]

    context = {
        'tong_sinh_vien': tong_sinh_vien,
        'tong_phong': tong_phong,
        'tong_cho_o': tong_cho_o,
        'so_sv_dang_o': so_sv_dang_o,
        'cho_con_trong': cho_con_trong,
        'ti_le_lap_day': ti_le_lap_day,
        'tong_xe_thang': tong_xe_thang,
        'tong_khach': tong_khach,
        'tong_doanh_thu_thang': tong_doanh_thu_thang,
        'current_month': current_month,
        'current_year': current_year,
        'luot_tham_moi': luot_tham_moi,
        'luot_xe_moi': luot_xe_moi,
        'dich_vu_moi': dich_vu_moi,
        'chart_dv_labels': chart_dv_labels,
        'chart_dv_data': chart_dv_data,
    }
    return render(request, 'dashboard.html', context)


def bao_cao(request):
    """
    Trang Báo Cáo trung tâm giải quyết trọn vẹn 4 yêu cầu truy vấn của Project 2:
    - Tab 1: Truy vấn 1 - Chi phí sinh viên theo tháng.
    - Tab 2: Truy vấn 2 - Sử dụng dịch vụ theo khoảng thời gian.
    - Tab 3: Truy vấn 3 - Khách thăm theo tuần hoặc tháng.
    - Tab 4: Truy vấn 4 - Doanh thu từng dịch vụ trong tháng.
    """
    today = date.today()
    tab = request.GET.get('tab', 'truyvan1')

    # Xử lý Tab 1: Chi phí sinh viên theo tháng
    t1_month = int(request.GET.get('t1_month', today.month))
    t1_year = int(request.GET.get('t1_year', today.year))
    t1_masv = request.GET.get('t1_masv', '').strip()
    ds_chi_phi_sv = tinh_chi_phi_sinh_vien_thang(t1_month, t1_year, t1_masv if t1_masv else None)
    tong_chi_phi_tat_ca = sum(r['tong_tien'] for r in ds_chi_phi_sv)

    # Xử lý Tab 2: Sử dụng dịch vụ theo khoảng thời gian
    # Mặc định lấy từ đầu tháng trước đến hôm nay
    default_from = (today - timedelta(days=60)).strftime('%Y-%m-%d')
    default_to = today.strftime('%Y-%m-%d')
    t2_tu_ngay_str = request.GET.get('t2_tu_ngay', default_from)
    t2_den_ngay_str = request.GET.get('t2_den_ngay', default_to)
    t2_masv = request.GET.get('t2_masv', '').strip()

    try:
        t2_tu_ngay = datetime.strptime(t2_tu_ngay_str, '%Y-%m-%d').date()
        t2_den_ngay = datetime.strptime(t2_den_ngay_str, '%Y-%m-%d').date()
    except ValueError:
        t2_tu_ngay = today - timedelta(days=60)
        t2_den_ngay = today

    ds_su_dung_dv = thong_ke_su_dung_dich_vu_khoang_tg(t2_tu_ngay, t2_den_ngay, t2_masv if t2_masv else None)
    tong_tien_su_dung_dv = sum(r['tong_tien'] for r in ds_su_dung_dv)

    # Xử lý Tab 3: Khách thăm theo tuần hoặc tháng
    t3_che_do = request.GET.get('t3_che_do', 'thang')  # 'tuan' hoặc 'thang'
    t3_masv = request.GET.get('t3_masv', '').strip()

    if t3_che_do == 'tuan':
        # Người dùng chọn 1 ngày trong tuần, tìm thứ 2 đến chủ nhật
        t3_ngay_chon_str = request.GET.get('t3_ngay', today.strftime('%Y-%m-%d'))
        try:
            t3_ngay_chon = datetime.strptime(t3_ngay_chon_str, '%Y-%m-%d').date()
        except ValueError:
            t3_ngay_chon = today
        # Thứ 2 là weekday 0
        t3_tu_ngay = t3_ngay_chon - timedelta(days=t3_ngay_chon.weekday())
        t3_den_ngay = t3_tu_ngay + timedelta(days=6)
    else:
        # Tháng
        t3_month = int(request.GET.get('t3_month', today.month))
        t3_year = int(request.GET.get('t3_year', today.year))
        t3_tu_ngay, t3_den_ngay, _, _ = lay_khoang_thoi_gian_thang(t3_year, t3_month)

    ds_khach_tham = thong_ke_khach_tham_ky(t3_tu_ngay, t3_den_ngay, t3_masv if t3_masv else None)
    tong_luot_tham = sum(r['so_lan_den'] for r in ds_khach_tham)

    # Xử lý Tab 4: Doanh thu mỗi dịch vụ theo tháng
    t4_month = int(request.GET.get('t4_month', today.month))
    t4_year = int(request.GET.get('t4_year', today.year))
    bao_cao_doanh_thu = thong_ke_doanh_thu_thang(t4_month, t4_year)

    # Danh sách sinh viên cho dropdown tìm kiếm
    all_sinh_vien = SinhVien.objects.select_related('nguoi').all()

    context = {
        'active_tab': tab,
        'today': today,
        'month_choices': list(range(1, 13)),
        'all_sinh_vien': all_sinh_vien,

        # Tab 1
        't1_month': t1_month,
        't1_year': t1_year,
        't1_masv': t1_masv,
        'ds_chi_phi_sv': ds_chi_phi_sv,
        'tong_chi_phi_tat_ca': tong_chi_phi_tat_ca,

        # Tab 2
        't2_tu_ngay': t2_tu_ngay,
        't2_den_ngay': t2_den_ngay,
        't2_masv': t2_masv,
        'ds_su_dung_dv': ds_su_dung_dv,
        'tong_tien_su_dung_dv': tong_tien_su_dung_dv,

        # Tab 3
        't3_che_do': t3_che_do,
        't3_tu_ngay': t3_tu_ngay,
        't3_den_ngay': t3_den_ngay,
        't3_masv': t3_masv,
        'ds_khach_tham': ds_khach_tham,
        'tong_luot_tham': tong_luot_tham,

        # Tab 4
        't4_month': t4_month,
        't4_year': t4_year,
        'bao_cao_doanh_thu': bao_cao_doanh_thu,
    }
    return render(request, 'bao_cao/bao_cao.html', context)


def in_hoa_don(request, masv):
    """
    Trang in hóa đơn chi tiết cho từng sinh viên trong tháng cụ thể.
    Đạt yêu cầu: 'có thể in theo danh sách hoặc theo từng người'.
    """
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    sinh_vien = get_object_or_404(SinhVien, masv=masv)
    ds = tinh_chi_phi_sinh_vien_thang(month, year, masv=masv)

    hoa_don_data = ds[0] if ds else None

    context = {
        'sinh_vien': sinh_vien,
        'month': month,
        'year': year,
        'hoa_don': hoa_don_data,
        'today': today,
    }
    return render(request, 'bao_cao/in_hoa_don.html', context)


def tra_cuu_sinh_vien(request):
    """
    Cổng tra cứu công khai cho Sinh viên:
    Nhập Mã sinh viên hoặc Số CMT để tự xem thông tin phòng, xe, dịch vụ, hóa đơn tháng.
    """
    tu_khoa = request.GET.get('q', '').strip()
    sinh_vien = None
    thong_tin_o = None
    ds_xe = []
    ds_su_dung = []
    ds_khach = []
    hoa_don = None

    today = date.today()
    month = today.month
    year = today.year

    if tu_khoa:
        sinh_vien = SinhVien.objects.filter(masv__iexact=tu_khoa).first()
        if not sinh_vien:
            sinh_vien = SinhVien.objects.filter(nguoi__socmt__iexact=tu_khoa).first()

        if sinh_vien:
            thong_tin_o = DangKyO.objects.filter(
                sinh_vien=sinh_vien
            ).order_by('-ngaybatdau').first()

            ds_xe = XeThang.objects.filter(sinh_vien=sinh_vien)
            ds_su_dung = SuDungDichVu.objects.filter(
                sinh_vien=sinh_vien
            ).order_by('-thoigiansudung')[:10]
            ds_khach = LuotTham.objects.filter(
                sinh_vien=sinh_vien
            ).order_by('-thoigianden')[:10]

            ds_hd = tinh_chi_phi_sinh_vien_thang(month, year, masv=sinh_vien.masv)
            hoa_don = ds_hd[0] if ds_hd else None
        else:
            messages.warning(request, f"Không tìm thấy sinh viên với từ khóa '{tu_khoa}'. Vui lòng kiểm tra lại Mã SV hoặc Số CMT!")

    context = {
        'tu_khoa': tu_khoa,
        'sinh_vien': sinh_vien,
        'thong_tin_o': thong_tin_o,
        'ds_xe': ds_xe,
        'ds_su_dung': ds_su_dung,
        'ds_khach': ds_khach,
        'hoa_don': hoa_don,
        'month': month,
        'year': year,
    }
    return render(request, 'tra_cuu/tra_cuu.html', context)

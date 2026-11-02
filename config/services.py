"""
Services and business logic for Dormitory Management System (Project 2).
Handles fee calculation, constraint validation, and specialized report queries.
"""

from datetime import date, datetime, time, timedelta
import calendar
from django.db.models import Sum, Count, Q
from sinh_vien.models import SinhVien
from phong_o.models import Phong, DangKyO
from dich_vu.models import DichVu
from gui_xe.models import XeThang, LuotGuiXe
from khach_tham.models import Khach, LuotTham
from chi_phi.models import SuDungDichVu


def lay_khoang_thoi_gian_thang(year, month):
    """Trả về (start_date, end_date, start_datetime, end_datetime) của tháng."""
    last_day = calendar.monthrange(year, month)[1]
    start_d = date(year, month, 1)
    end_d = date(year, month, last_day)
    start_dt = datetime.combine(start_d, time.min)
    end_dt = datetime.combine(end_d, time.max)
    return start_d, end_d, start_dt, end_dt


def kiem_tra_suc_chua_phong(so_phong):
    """
    Kiểm tra ràng buộc số người trong phòng.
    Trả về: (phong, so_nguoi_hien_tai, so_nguoi_toi_da, con_trong, da_day)
    """
    phong = Phong.objects.filter(sophong=so_phong).first()
    if not phong:
        return None, 0, 0, 0, True
    hien_tai = phong.so_nguoi_hien_tai()
    toi_da = phong.songuoitoida
    con_trong = max(0, toi_da - hien_tai)
    da_day = hien_tai >= toi_da
    return phong, hien_tai, toi_da, con_trong, da_day


def kiem_tra_so_xe_sinh_vien(sinh_vien):
    """
    Kiểm tra ràng buộc mỗi sinh viên chỉ được đăng ký tối đa 2 xe vé tháng còn hiệu lực.
    Trả về: (so_xe, duoc_dang_ky)
    """
    today = date.today()
    so_xe = XeThang.objects.filter(
        sinh_vien=sinh_vien,
        ngayhethan__gte=today
    ).count()
    return so_xe, so_xe < 2


def tinh_phi_luot_xe_moi(bien_so, ngay_gui=None):
    """
    Quy tắc nghiệp vụ: Mỗi ngày xe vé tháng được lấy ra/gửi vào 2 lần miễn phí.
    Từ lần thứ 3 trong ngày phát sinh 3.000đ/lượt.
    """
    if ngay_gui is None:
        ngay_gui = date.today()
    so_luot_da_co = LuotGuiXe.objects.filter(
        xe_thang_id=bien_so,
        ngay=ngay_gui
    ).count()
    if so_luot_da_co >= 2:
        return 3000, so_luot_da_co + 1
    return 0, so_luot_da_co + 1


# ==========================================
# TRUY VẤN 1: Chi phí sinh viên theo tháng
# (Tiền phòng chẵn tháng + Vé xe tháng + Phát sinh xe + Dịch vụ)
# ==========================================
def tinh_chi_phi_sinh_vien_thang(month, year, masv=None):
    """
    Liệt kê thông tin sinh viên cùng số tiền phải trả cho tất cả các dịch vụ
    (bao gồm cả tiền phòng) trong mỗi tháng.
    """
    start_d, end_d, start_dt, end_dt = lay_khoang_thoi_gian_thang(year, month)

    sv_qs = SinhVien.objects.select_related('nguoi').all()
    if masv:
        sv_qs = sv_qs.filter(masv=masv)

    ket_qua = []

    for sv in sv_qs:
        # 1. Tiền phòng (ở 1 ngày cũng trả cả tháng)
        # Hợp đồng giao nhau với [start_d, end_d]:
        # ngaybatdau <= end_d VÀ (ngayketthuc IS NULL HOẶC ngayketthuc >= start_d)
        dk_o = DangKyO.objects.filter(
            sinh_vien=sv,
            ngaybatdau__lte=end_d
        ).filter(
            Q(ngayketthuc__isnull=True) | Q(ngayketthuc__gte=start_d)
        ).select_related('phong').first()

        tien_phong = dk_o.phong.dongia if dk_o else 0
        phong_info = dk_o.phong if dk_o else None

        # 2. Tiền xe vé tháng (các xe có hiệu lực trong tháng)
        ds_xe = XeThang.objects.filter(
            sinh_vien=sv,
            ngaydangky__lte=end_d,
            ngayhethan__gte=start_d
        )
        tien_xe_thang = sum(x.dongiathang for x in ds_xe)

        # 3. Tiền gửi xe phát sinh trong tháng
        ds_luot_phat_sinh = LuotGuiXe.objects.filter(
            xe_thang__sinh_vien=sv,
            ngay__gte=start_d,
            ngay__lte=end_d,
            sotienphatsinh__gt=0
        ).select_related('xe_thang')
        tien_xe_phat_sinh = sum(lx.sotienphatsinh for lx in ds_luot_phat_sinh)

        # 4. Tiền các dịch vụ khác sử dụng trong tháng
        ds_su_dung_dv = SuDungDichVu.objects.filter(
            sinh_vien=sv,
            thoigiansudung__range=(start_dt, end_dt)
        ).select_related('dich_vu')
        tien_dich_vu = sum(sd.thanh_tien() for sd in ds_su_dung_dv)

        tong_tien = tien_phong + tien_xe_thang + tien_xe_phat_sinh + tien_dich_vu

        # Chỉ thêm nếu sinh viên có ở KTX hoặc có phát sinh chi phí
        if dk_o or tien_xe_thang > 0 or tien_xe_phat_sinh > 0 or tien_dich_vu > 0 or masv:
            ket_qua.append({
                'sinh_vien': sv,
                'phong': phong_info,
                'tien_phong': tien_phong,
                'ds_xe': ds_xe,
                'tien_xe_thang': tien_xe_thang,
                'ds_luot_phat_sinh': ds_luot_phat_sinh,
                'tien_xe_phat_sinh': tien_xe_phat_sinh,
                'ds_su_dung_dv': ds_su_dung_dv,
                'tien_dich_vu': tien_dich_vu,
                'tong_tien': tong_tien,
                'thang': month,
                'nam': year,
            })

    return ket_qua


# ==========================================
# TRUY VẤN 2: Sử dụng dịch vụ theo khoảng thời gian
# ==========================================
def thong_ke_su_dung_dich_vu_khoang_tg(tu_ngay, den_ngay, masv=None):
    """
    Liệt kê thông tin SV cùng tên dịch vụ, tổng giá mỗi dịch vụ
    sử dụng trong khoảng thời gian từ tu_ngay đến den_ngay.
    """
    start_dt = datetime.combine(tu_ngay, time.min)
    end_dt = datetime.combine(den_ngay, time.max)

    qs = SuDungDichVu.objects.filter(
        thoigiansudung__range=(start_dt, end_dt)
    ).select_related('sinh_vien__nguoi', 'dich_vu')

    if masv:
        qs = qs.filter(sinh_vien__masv=masv)

    # Gom nhóm theo (sinh_vien, dich_vu)
    from collections import defaultdict
    nhom = defaultdict(lambda: {'so_luong': 0, 'tong_tien': 0, 'cac_lan': []})

    for item in qs:
        key = (item.sinh_vien, item.dich_vu)
        thanh_tien = item.thanh_tien()
        nhom[key]['so_luong'] += item.soluong
        nhom[key]['tong_tien'] += thanh_tien
        nhom[key]['cac_lan'].append(item)

    ket_qua = []
    for (sv, dv), data in nhom.items():
        ket_qua.append({
            'sinh_vien': sv,
            'dich_vu': dv,
            'tong_so_luong': data['so_luong'],
            'tong_tien': data['tong_tien'],
            'cac_lan': data['cac_lan'],
        })

    # Sắp xếp theo tên sinh viên rồi đến tên dịch vụ
    ket_qua.sort(key=lambda x: (x['sinh_vien'].masv, x['dich_vu'].tendichvu or ''))
    return ket_qua


# ==========================================
# TRUY VẤN 3: Khách đến thăm trong tuần hoặc tháng
# ==========================================
def thong_ke_khach_tham_ky(tu_ngay, den_ngay, masv=None):
    """
    Liệt kê thông tin sinh viên cùng thông tin về các khách đến thăm
    trong khoảng thời gian (tuần/tháng), cùng số lần mỗi khách đến chơi.
    """
    start_dt = datetime.combine(tu_ngay, time.min)
    end_dt = datetime.combine(den_ngay, time.max)

    qs = LuotTham.objects.filter(
        thoigianden__range=(start_dt, end_dt)
    ).select_related('khach__nguoi', 'sinh_vien__nguoi')

    if masv:
        qs = qs.filter(sinh_vien__masv=masv)

    from collections import defaultdict
    nhom = defaultdict(lambda: {'so_lan': 0, 'danh_sach_lan': []})

    for lt in qs:
        key = (lt.sinh_vien, lt.khach)
        nhom[key]['so_lan'] += 1
        nhom[key]['danh_sach_lan'].append(lt.thoigianden)

    ket_qua = []
    for (sv, khach), data in nhom.items():
        ket_qua.append({
            'sinh_vien': sv,
            'khach': khach,
            'so_lan_den': data['so_lan'],
            'danh_sach_lan': data['danh_sach_lan'],
        })

    ket_qua.sort(key=lambda x: (-x['so_lan_den'], x['sinh_vien'].masv))
    return ket_qua


# ==========================================
# TRUY VẤN 4: Doanh thu của mỗi dịch vụ trong tháng
# ==========================================
def thong_ke_doanh_thu_thang(month, year):
    """
    Liệt kê danh mục các dịch vụ cùng doanh thu của mỗi dịch vụ
    trong KTX trong mỗi tháng.
    """
    start_d, end_d, start_dt, end_dt = lay_khoang_thoi_gian_thang(year, month)

    ds_muc_doanh_thu = []

    # 1. Doanh thu tiền phòng
    cac_hop_dong = DangKyO.objects.filter(
        ngaybatdau__lte=end_d
    ).filter(
        Q(ngayketthuc__isnull=True) | Q(ngayketthuc__gte=start_d)
    ).select_related('phong')

    doanh_thu_phong = sum(dk.phong.dongia for dk in cac_hop_dong)
    so_sv_o = cac_hop_dong.count()
    ds_muc_doanh_thu.append({
        'ma': 'TIEN_PHONG',
        'ten': 'Tiền thuê phòng ở',
        'loai': 'Phòng ở',
        'so_luot': so_sv_o,
        'don_vi': 'Sinh viên',
        'doanh_thu': doanh_thu_phong,
    })

    # 2. Doanh thu vé xe tháng
    ds_xe_thang = XeThang.objects.filter(
        ngaydangky__lte=end_d,
        ngayhethan__gte=start_d
    )
    doanh_thu_xe_thang = sum(x.dongiathang for x in ds_xe_thang)
    ds_muc_doanh_thu.append({
        'ma': 'XE_THANG',
        'ten': 'Gửi xe vé tháng',
        'loai': 'Trông giữ xe',
        'so_luot': ds_xe_thang.count(),
        'don_vi': 'Xe tháng',
        'doanh_thu': doanh_thu_xe_thang,
    })

    # 3. Doanh thu gửi xe phát sinh
    luot_ps = LuotGuiXe.objects.filter(
        ngay__gte=start_d,
        ngay__lte=end_d,
        sotienphatsinh__gt=0
    )
    doanh_thu_xe_ps = sum(x.sotienphatsinh for x in luot_ps)
    ds_muc_doanh_thu.append({
        'ma': 'XE_PHAT_SINH',
        'ten': 'Phí gửi xe phát sinh (lượt 3+)',
        'loai': 'Trông giữ xe',
        'so_luot': luot_ps.count(),
        'don_vi': 'Lượt phát sinh',
        'doanh_thu': doanh_thu_xe_ps,
    })

    # 4. Doanh thu từng dịch vụ trong bảng DICH_VU
    tat_ca_dv = DichVu.objects.all()
    for dv in tat_ca_dv:
        su_dung = SuDungDichVu.objects.filter(
            dich_vu=dv,
            thoigiansudung__range=(start_dt, end_dt)
        )
        tong_sl = su_dung.aggregate(Sum('soluong'))['soluong__sum'] or 0
        dt_dv = tong_sl * dv.dongia
        ds_muc_doanh_thu.append({
            'ma': dv.madichvu,
            'ten': dv.tendichvu or dv.madichvu,
            'loai': 'Dịch vụ KTX',
            'so_luot': tong_sl,
            'don_vi': 'Lượt / Đơn vị',
            'doanh_thu': dt_dv,
        })

    tong_doanh_thu = sum(m['doanh_thu'] for m in ds_muc_doanh_thu)

    # Tính tỷ lệ %
    for m in ds_muc_doanh_thu:
        m['ti_le'] = round((m['doanh_thu'] / tong_doanh_thu * 100), 1) if tong_doanh_thu > 0 else 0

    return {
        'thang': month,
        'nam': year,
        'danh_sach': ds_muc_doanh_thu,
        'tong_doanh_thu': tong_doanh_thu,
    }

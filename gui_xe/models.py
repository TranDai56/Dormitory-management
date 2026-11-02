from django.db import models
from datetime import date
from sinh_vien.models import SinhVien


class XeThang(models.Model):
    bienso = models.CharField(
        max_length=50,
        primary_key=True,
        db_column='BienSo'
    )
    sinh_vien = models.ForeignKey(
        SinhVien,
        on_delete=models.CASCADE,
        db_column='SoCMT_SV',
        related_name='ds_xe_thang'
    )
    loaixe = models.CharField(
        max_length=50,
        db_column='LoaiXe',
        null=True,
        blank=True
    )
    ngaydangky = models.DateField(
        db_column='NgayDangKy'
    )
    ngayhethan = models.DateField(
        db_column='NgayHetHan'
    )
    dongiathang = models.BigIntegerField(
        db_column='DonGiaThang'
    )

    class Meta:
        managed = False
        db_table = 'xe_thang'

    def __str__(self):
        return f"{self.bienso} ({self.loaixe or 'Xe'})"

    def con_hieu_luc(self):
        return self.ngayhethan >= date.today()


class LuotGuiXe(models.Model):
    maluot = models.AutoField(
        primary_key=True,
        db_column='MaLuot'
    )
    xe_thang = models.ForeignKey(
        XeThang,
        on_delete=models.CASCADE,
        db_column='BienSo',
        related_name='ds_luot_gui_xe'
    )
    thoigianlay = models.DateTimeField(
        db_column='ThoiGianLay',
        null=True,
        blank=True
    )
    thoigiangui = models.DateTimeField(
        db_column='ThoiGianGui',
        null=True,
        blank=True
    )
    sotienphatsinh = models.BigIntegerField(
        db_column='SoTienPhatSinh',
        default=0
    )
    ngay = models.DateField(
        db_column='Ngay',
        null=True,
        blank=True
    )

    class Meta:
        managed = False
        db_table = 'luot_gui_xe'

    def __str__(self):
        return f"Lượt {self.maluot} - Biển {self.xe_thang_id}"

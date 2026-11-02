from django.db import models
from sinh_vien.models import Nguoi, SinhVien


class Khach(models.Model):
    nguoi = models.OneToOneField(
        Nguoi,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='SoCMT',
        related_name='khach_tham'
    )
    makhach = models.CharField(
        max_length=250,
        unique=True,
        db_column='MaKhach'
    )

    class Meta:
        managed = False
        db_table = 'khach_tham'

    def __str__(self):
        return f"{self.makhach} - {self.nguoi.hoten}"

    @property
    def hoten(self):
        return self.nguoi.hoten

    @property
    def socmt(self):
        return self.nguoi.socmt

    @property
    def ngaysinh(self):
        return self.nguoi.ngaysinh


class LuotTham(models.Model):
    maluottham = models.AutoField(
        primary_key=True,
        db_column='MaLuotTham'
    )
    khach = models.ForeignKey(
        Khach,
        on_delete=models.CASCADE,
        db_column='SoCMT_Khach',
        related_name='ds_luot_tham'
    )
    sinh_vien = models.ForeignKey(
        SinhVien,
        on_delete=models.CASCADE,
        db_column='SoCMT_SV',
        related_name='ds_luot_duoc_tham'
    )
    thoigianden = models.DateTimeField(
        null=True,
        blank=True,
        db_column='ThoiGianDen'
    )

    class Meta:
        managed = False
        db_table = 'luot_tham'

    def __str__(self):
        return f"{self.khach.nguoi.hoten} thăm {self.sinh_vien.masv} lúc {self.thoigianden}"

from django.db import models
from sinh_vien.models import SinhVien
from dich_vu.models import DichVu


class SuDungDichVu(models.Model):
    malansudung = models.AutoField(
        primary_key=True,
        db_column='MaLanSuDung'
    )
    sinh_vien = models.ForeignKey(
        SinhVien,
        on_delete=models.CASCADE,
        db_column='SoCMT_SV',
        related_name='ds_su_dung_dv'
    )
    dich_vu = models.ForeignKey(
        DichVu,
        on_delete=models.CASCADE,
        db_column='MaDichVu',
        related_name='ds_su_dung'
    )
    thoigiansudung = models.DateTimeField(
        db_column='ThoiGianSuDung'
    )
    soluong = models.BigIntegerField(
        db_column='SoLuong'
    )

    class Meta:
        managed = False
        db_table = 'su_dung_dich_vu'

    def __str__(self):
        return f"{self.sinh_vien.masv} dùng {self.dich_vu.tendichvu} x {self.soluong}"

    def thanh_tien(self):
        return self.soluong * (self.dich_vu.dongia if self.dich_vu else 0)

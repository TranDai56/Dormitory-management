from django.db import models
from datetime import date
from sinh_vien.models import SinhVien


class Phong(models.Model):
    sophong = models.CharField(
        max_length=20,
        primary_key=True,
        db_column='SoPhong'
    )
    loaiphong = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        db_column='loaiPhong'
    )
    dongia = models.BigIntegerField(db_column='DonGia')
    songuoitoida = models.IntegerField(db_column='SoNguoiToiDa')

    class Meta:
        managed = False
        db_table = 'phong'

    def __str__(self):
        return f"Phòng {self.sophong} ({self.loaiphong})"

    def so_nguoi_hien_tai(self):
        today = date.today()
        return self.cac_dang_ky_o.filter(
            ngaybatdau__lte=today
        ).filter(
            models.Q(ngayketthuc__isnull=True) | models.Q(ngayketthuc__gte=today)
        ).count()

    def con_trong(self):
        return max(0, self.songuoitoida - self.so_nguoi_hien_tai())

    def da_day(self):
        return self.so_nguoi_hien_tai() >= self.songuoitoida

    def ti_le_lap_day(self):
        if self.songuoitoida <= 0:
            return 0
        return int((self.so_nguoi_hien_tai() / self.songuoitoida) * 100)


class DangKyO(models.Model):
    madangkyo = models.AutoField(
        primary_key=True,
        db_column='MaDangKyO'
    )
    sinh_vien = models.ForeignKey(
        SinhVien,
        on_delete=models.CASCADE,
        db_column='SoCMT_SV',
        related_name='cac_dang_ky_o'
    )
    phong = models.ForeignKey(
        Phong,
        on_delete=models.CASCADE,
        db_column='SoPhong',
        related_name='cac_dang_ky_o'
    )
    ngaybatdau = models.DateField(db_column='NgayBatDau')
    ngayketthuc = models.DateField(
        null=True,
        blank=True,
        db_column='NgayKetThuc'
    )

    class Meta:
        managed = False
        db_table = 'dang_ky_o'

    def __str__(self):
        return f"{self.sinh_vien.masv} - Phòng {self.phong.sophong}"

    def con_hieu_luc(self):
        today = date.today()
        if self.ngaybatdau > today:
            return False
        return self.ngayketthuc is None or self.ngayketthuc >= today

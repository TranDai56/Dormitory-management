from django.db import models


class Nguoi(models.Model):
    socmt = models.CharField(
        max_length=20,
        primary_key=True,
        db_column='SoCMT'
    )
    hoten = models.CharField(
        max_length=250,
        db_column='HoTen'
    )
    ngaysinh = models.DateField(
        null=True,
        blank=True,
        db_column='NgaySinh'
    )

    class Meta:
        managed = False
        db_table = 'nguoi'

    def __str__(self):
        return f"{self.hoten} ({self.socmt})"


class SinhVien(models.Model):
    nguoi = models.OneToOneField(
        Nguoi,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='SoCMT',
        related_name='sinh_vien'
    )
    masv = models.CharField(
        max_length=100,
        unique=True,
        db_column='MaSV'
    )
    lop = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='Lop'
    )
    quequan = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='QueQuan'
    )

    class Meta:
        managed = False
        db_table = 'sinh_vien'

    def __str__(self):
        return f"{self.masv} - {self.nguoi.hoten}"

    @property
    def hoten(self):
        return self.nguoi.hoten

    @property
    def socmt(self):
        return self.nguoi.socmt

    @property
    def ngaysinh(self):
        return self.nguoi.ngaysinh

    def phong_hien_tai(self):
        from datetime import date
        today = date.today()
        dk = self.cac_dang_ky_o.filter(
            ngaybatdau__lte=today
        ).filter(
            models.Q(ngayketthuc__isnull=True) | models.Q(ngayketthuc__gte=today)
        ).first()
        return dk.phong if dk else None

    def so_xe_hieu_luc(self):
        from datetime import date
        today = date.today()
        return self.ds_xe_thang.filter(ngayhethan__gte=today).count()

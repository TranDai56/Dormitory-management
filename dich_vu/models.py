from django.db import models


class DichVu(models.Model):
    madichvu = models.CharField(
        max_length=20,
        primary_key=True,
        db_column='MaDichVu'
    )
    tendichvu = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        db_column='TenDichVu'
    )
    dongia = models.BigIntegerField(
        db_column='DonGia'
    )

    class Meta:
        managed = False
        db_table = 'dich_vu'

    def __str__(self):
        return f"{self.tendichvu} ({self.madichvu}) - {self.dongia:,.0f} đ"

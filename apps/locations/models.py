from django.db import models


class Region(models.Model):
    """Regions of Uzbekistan"""
    name_uz = models.CharField(max_length=100, verbose_name="Nomi (O'zbekcha)")
    name_ru = models.CharField(max_length=100, verbose_name="Nomi (Ruschada)")
    name_en = models.CharField(max_length=100, verbose_name="Name (English)")
    code = models.CharField(max_length=10, unique=True, verbose_name="Code")
    delivery_days_min = models.PositiveIntegerField(default=1, verbose_name="Min delivery days")
    delivery_days_max = models.PositiveIntegerField(default=3, verbose_name="Max delivery days")
    is_active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        db_table = 'locations_region'
        verbose_name = "Region"
        verbose_name_plural = "Regions"
        ordering = ['name_en']

    def __str__(self):
        return self.name_en


class City(models.Model):
    """Cities within regions"""
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='cities', verbose_name="Region")
    name_uz = models.CharField(max_length=100, verbose_name="Nomi (O'zbekcha)")
    name_ru = models.CharField(max_length=100, verbose_name="Nomi (Ruschada)")
    name_en = models.CharField(max_length=100, verbose_name="Name (English)")
    is_hub = models.BooleanField(default=False, verbose_name="Is hub")
    is_active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        db_table = 'locations_city'
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = ['region', 'name_en']
        unique_together = [['region', 'name_en']]

    def __str__(self):
        return f"{self.region.name_en} - {self.name_en}"
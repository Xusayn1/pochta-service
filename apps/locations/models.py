# backend/apps/locations/models.py
from django.db import models
from django.utils import timezone

class Region(models.Model):
    """Viloyatlar (Toshkent, Samarqand, etc.)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Viloyat nomi")
    name_uz = models.CharField(max_length=100, verbose_name="Nomi (O'zbekcha)")
    name_ru = models.CharField(max_length=100, verbose_name="Nomi (Ruschada)")
    code = models.CharField(max_length=10, unique=True, verbose_name="Kod")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'locations_region'
        verbose_name = "Viloyat"
        verbose_name_plural = "Viloyatlar"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class District(models.Model):
    """Tuman/Shaharlar"""
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='districts', verbose_name="Viloyat")
    name = models.CharField(max_length=100, verbose_name="Tuman nomi")
    name_uz = models.CharField(max_length=100, verbose_name="Nomi (O'zbekcha)")
    name_ru = models.CharField(max_length=100, verbose_name="Nomi (Ruschada)")
    code = models.CharField(max_length=20, unique=True, verbose_name="Kod")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'locations_district'
        verbose_name = "Tuman"
        verbose_name_plural = "Tumanlar"
        ordering = ['region', 'name']
        unique_together = [['region', 'name']]
    
    def __str__(self):
        return f"{self.region.name} - {self.name}"

class Branch(models.Model):
    """Filiallar / Pochta bo'limlari"""
    BRANCH_TYPES = [
        ('main', 'Markaziy filial'),
        ('regional', 'Viloyat filiali'),
        ('district', 'Tuman filiali'),
        ('pickup', 'Yetkazib olish punkti'),
        ('dropoff', 'Topshirish punkti'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Filial nomi")
    branch_type = models.CharField(max_length=20, choices=BRANCH_TYPES, default='district', verbose_name="Filial turi")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='branches', verbose_name="Viloyat")
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='branches', verbose_name="Tuman")
    address = models.TextField(verbose_name="Manzil")
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name="Kenglik")
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name="Uzunlik")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    working_hours = models.CharField(max_length=100, default="09:00 - 18:00", verbose_name="Ish vaqti")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'locations_branch'
        verbose_name = "Filial"
        verbose_name_plural = "Filiallar"
        ordering = ['region', 'district', 'name']
    
    def __str__(self):
        return self.name
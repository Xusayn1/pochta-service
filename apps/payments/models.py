from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string


class PaymentMethod(models.TextChoices):
    CASH = "cash", "Cash"
    CARD = "card", "Card"
    CLICK = "click", "Click"
    PAYME = "payme", "Payme"


class TransactionStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    REFUNDED = "refunded", "Refunded"


class GatewayName(models.TextChoices):
    CLICK = "click", "Click"
    PAYME = "payme", "Payme"
    STRIPE = "stripe", "Stripe"


class GatewayEnvironment(models.TextChoices):
    SANDBOX = "sandbox", "Sandbox"
    PRODUCTION = "production", "Production"


class Transaction(models.Model):
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="transactions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
    )
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    payment_url = models.URLField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "payments_transaction"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["transaction_id"])]

    def __str__(self):
        return self.transaction_id or f"Transaction #{self.pk}"

    def save(self, *args, **kwargs):
        if self.status == TransactionStatus.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        if self.status != TransactionStatus.COMPLETED and self.completed_at:
            self.completed_at = None
        super().save(*args, **kwargs)


class Invoice(models.Model):
    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE, related_name="invoice")
    invoice_number = models.CharField(max_length=255, unique=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"), editable=False)
    pdf_file = models.FileField(upload_to="invoices/", null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments_invoice"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["invoice_number"])]

    def __str__(self):
        return self.invoice_number

    @staticmethod
    def generate_invoice_number():
        date_part = timezone.now().strftime("%Y%m%d")
        random_part = get_random_string(6, allowed_chars="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        return f"INV{date_part}{random_part}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            invoice_number = self.generate_invoice_number()
            while Invoice.objects.filter(invoice_number=invoice_number).exists():
                invoice_number = self.generate_invoice_number()
            self.invoice_number = invoice_number

        self.total_amount = (self.amount or Decimal("0.00")) + (self.tax or Decimal("0.00")) - (
            self.discount or Decimal("0.00")
        )

        if self.is_paid and not self.paid_at:
            self.paid_at = timezone.now()
        if not self.is_paid and self.paid_at:
            self.paid_at = None

        super().save(*args, **kwargs)


class PaymentGatewaySettings(models.Model):
    gateway_name = models.CharField(max_length=20, choices=GatewayName.choices)
    api_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    merchant_id = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    environment = models.CharField(max_length=20, choices=GatewayEnvironment.choices)

    class Meta:
        db_table = "payments_gateway_settings"
        ordering = ["gateway_name", "environment"]
        unique_together = [["gateway_name", "environment"]]

    def __str__(self):
        return f"{self.gateway_name} ({self.environment})"

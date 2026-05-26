from django.db import models
from django.conf import settings
from core.models import Currency


class Supplier(models.Model):
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Inactive", "Inactive"),
    ]

    id_supplier = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
        verbose_name="Supplier ID",
    )

    legal_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Legal Name",
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Name",
    )

    tax_id = models.CharField(
        max_length=30,
        verbose_name="Tax ID",
    )

    country = models.CharField(
        max_length=60,
        verbose_name="Country",
    )

    state_province = models.CharField(
        max_length=60,
        verbose_name="State/Province",
    )

    city = models.CharField(
        max_length=100,
        verbose_name="City",
    )

    address = models.CharField(
        max_length=150,
        verbose_name="Address",
    )

    zip_code = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Zip Code",
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Phone",
    )

    email = models.EmailField(
        max_length=150,
        blank=True,
        verbose_name="Email",
    )

    contact_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Contact name",
    )

    contact_role = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Contact role",
    )

    category = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Category",
    )

    payment_terms = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Payment terms",
    )

    currency = models.ForeignKey(
        Currency,
        default=1,
        on_delete=models.PROTECT,
        verbose_name="Currency",
    )

    payment_method = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Payment method",
    )

    bank_account = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Bank account",
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="Active",
        verbose_name="Status",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"

    def __str__(self):
        return self.name
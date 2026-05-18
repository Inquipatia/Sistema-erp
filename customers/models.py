from django.db import models
from django.conf import settings


class Customer(models.Model):
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Inactive", "Inactive"),
    ]

    COUNTRY_CHOICES = [
        ("US", "United States (US)"),
        ("CN", "China (CN)"),
        ("IN", "India (IN)"),
        ("JP", "Japan (JP)"),
        ("DE", "Germany (DE)"),
        ("GB", "United Kingdom (GB)"),
        ("FR", "France (FR)"),
        ("IT", "Italy (IT)"),
        ("CA", "Canada (CA)"),
        ("RU", "Russia (RU)"),
        ("MX", "Mexico (MX)"),
        ("BR", "Brazil (BR)"),
        ("AR", "Argentina (AR)"),
        ("CL", "Chile (CL)"),
        ("CO", "Colombia (CO)"),
        ("PE", "Peru (PE)"),
        ("VE", "Venezuela (VE)"),
        ("EC", "Ecuador (EC)"),
        ("BO", "Bolivia (BO)"),
        ("UY", "Uruguay (UY)"),
        ("PY", "Paraguay (PY)"),
        ("CR", "Costa Rica (CR)"),
        ("DO", "Dominican Republic (DO)"),
        ("GT", "Guatemala (GT)"),
        ("HN", "Honduras (HN)"),
    ]

    CURRENCY_CHOICES = [
        ("USD", "United States Dollar (USD)"),
        ("EUR", "Euro (EUR)"),
        ("GBP", "British Pound Sterling (GBP)"),
        ("JPY", "Japanese Yen (JPY)"),
        ("CNY", "Chinese Yuan Renminbi (CNY)"),
        ("CHF", "Swiss Franc (CHF)"),
        ("CAD", "Canadian Dollar (CAD)"),
        ("BRL", "Brazilian Real (BRL)"),
        ("MXN", "Mexican Peso (MXN)"),
        ("ARS", "Argentine Peso (ARS)"),
        ("CLP", "Chilean Peso (CLP)"),
        ("COP", "Colombian Peso (COP)"),
        ("PEN", "Peruvian Sol (PEN)"),
        ("UYU", "Uruguayan Peso (UYU)"),
        ("PYG", "Paraguayan Guarani (PYG)"),
        ("BOB", "Bolivian Boliviano (BOB)"),
        ("CRC", "Costa Rican Colon (CRC)"),
        ("DOP", "Dominican Peso (DOP)"),
        ("GTQ", "Guatemalan Quetzal (GTQ)"),
        ("HNL", "Honduran Lempira (HNL)"),
    ]

    id_customer = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        unique=True,
        verbose_name="Customer ID"
    )

    legal_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Legal Name"
    )

    name = models.CharField(
        max_length=150,
        verbose_name="Name"
    )

    tax_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Tax ID"
    )

    country = models.CharField(
        max_length=100,
        choices=COUNTRY_CHOICES,
        blank=True,
        verbose_name="Country"
    )

    state_province = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="State/Province"
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="City"
    )

    address = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Address"
    )

    zip_code = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Zip Code"
    )

    phone = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Phone"
    )

    email = models.EmailField(
        max_length=150,
        blank=True,
        verbose_name="Email"
    )

    contact_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Contact Name"
    )

    contact_role = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Contact Role"
    )

    category = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Category"
    )

    payment_terms = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Payment Terms"
    )

    currency = models.CharField(
        max_length=20,
        choices=CURRENCY_CHOICES,
        blank=True,
        verbose_name="Currency"
    )

    payment_method = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Payment Method"
    )

    bank_account = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Bank Account"
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="Active",
        verbose_name="Status"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return self.name
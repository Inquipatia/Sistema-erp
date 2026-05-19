from django.db import models
from django.conf import settings

from core.models import Country, Currency, Status


class AccountNature(models.Model):
    id_account_nature = models.CharField(
        verbose_name="Account Nature ID",
        max_length=10,
        primary_key=True
    )

    name = models.CharField(
        verbose_name="Name",
        max_length=50
    )

    symbol = models.CharField(
        verbose_name="Symbol",
        max_length=10
    )

    effect_on_balance = models.TextField(
        verbose_name="Effect on Balance"
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
        verbose_name = "Account Nature"
        verbose_name_plural = "Account Natures"

    def __str__(self):
        return self.name


class AccountGroup(models.Model):
    id_account_group = models.CharField(
        verbose_name="Account Group ID",
        max_length=10,
        primary_key=True
    )

    name = models.CharField(
        verbose_name="Name",
        max_length=100
    )

    description = models.TextField(
        verbose_name="Description",
        blank=True
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
        verbose_name = "Account Group"
        verbose_name_plural = "Account Groups"

    def __str__(self):
        return self.name


class AccountType(models.Model):
    id_account_type = models.CharField(
        verbose_name="Account Type ID",
        max_length=10,
        primary_key=True
    )

    name = models.CharField(
        verbose_name="Name",
        max_length=50
    )

    description = models.TextField(
        verbose_name="Description",
        blank=True
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
        verbose_name = "Account Type"
        verbose_name_plural = "Account Types"

    def __str__(self):
        return self.name


class AccountAccount(models.Model):
    id_account = models.CharField(
        verbose_name="Account ID",
        max_length=10,
        primary_key=True
    )

    name = models.CharField(
        verbose_name="Name",
        max_length=100
    )

    code = models.CharField(
        verbose_name="Code",
        max_length=20
    )

    description = models.TextField(
        verbose_name="Description",
        blank=True
    )

    account_type = models.ForeignKey(
        AccountType,
        verbose_name="Account Type",
        on_delete=models.PROTECT
    )

    account_group = models.ForeignKey(
        AccountGroup,
        verbose_name="Account Group",
        on_delete=models.PROTECT
    )

    nature = models.ForeignKey(
        AccountNature,
        verbose_name="Account Nature",
        on_delete=models.PROTECT
    )

    currency = models.ForeignKey(
        Currency,
        verbose_name="Currency",
        on_delete=models.PROTECT
    )

    country = models.ForeignKey(
        Country,
        verbose_name="Country",
        on_delete=models.PROTECT
    )

    is_control_account = models.BooleanField(
        verbose_name="Is Control Account",
        default=False
    )

    parent_account = models.ForeignKey(
        "self",
        verbose_name="Parent Account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    status = models.ForeignKey(
        Status,
        default=1,
        on_delete=models.PROTECT,
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
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    def __str__(self):
        return f"{self.code} - {self.name}"
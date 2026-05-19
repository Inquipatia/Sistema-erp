from django.db import models
from django.conf import settings

from core.models import Status
from materials.models import Material, Unit


class MovementType(models.Model):
    name = models.CharField(
        verbose_name="Name",
        max_length=50
    )

    symbol = models.CharField(
        verbose_name="Symbol",
        max_length=10
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
        verbose_name = "Movement Type"
        verbose_name_plural = "Movement Types"

    def __str__(self):
        return f"{self.symbol} - {self.name}"


class LocationInventory(models.Model):
    id_location = models.CharField(
        verbose_name="Location ID",
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

    main_location = models.BooleanField(
        verbose_name="Main Location",
        default=False
    )

    location = models.TextField(
        verbose_name="Address",
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
        verbose_name = "Inventory Location"
        verbose_name_plural = "Inventory Locations"

    def __str__(self):
        return f"{self.code} - {self.name}"


class InventoryMovement(models.Model):
    id_inventory_movement = models.CharField(
        verbose_name="Inventory Movement ID",
        max_length=10,
        primary_key=True
    )

    id_location = models.ForeignKey(
        LocationInventory,
        on_delete=models.PROTECT,
        verbose_name="Location ID"
    )

    id_material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        verbose_name="Material ID"
    )

    movement_type = models.ForeignKey(
        MovementType,
        on_delete=models.PROTECT,
        verbose_name="Movement Type"
    )

    quantity = models.IntegerField(
        verbose_name="Quantity"
    )

    unit_type = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        verbose_name="Unit Type"
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
        verbose_name = "Inventory Movement"
        verbose_name_plural = "Inventory Movements"

    def __str__(self):
        return f"{self.id_material} - {self.quantity} - {self.unit_type}"
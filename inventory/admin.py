from django.contrib import admin
from .models import MovementType, LocationInventory, InventoryMovement


@admin.register(MovementType)
class MovementTypeAdmin(admin.ModelAdmin):
    list_display = (
        "symbol",
        "name",
        "created_by",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "symbol",
        "name",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )


@admin.register(LocationInventory)
class LocationInventoryAdmin(admin.ModelAdmin):
    list_display = (
        "id_location",
        "code",
        "name",
        "main_location",
        "status",
        "created_by",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "id_location",
        "code",
        "name",
        "location",
    )

    list_filter = (
        "main_location",
        "status",
        "created_at",
        "updated_at",
    )


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = (
        "id_inventory_movement",
        "id_location",
        "id_material",
        "movement_type",
        "quantity",
        "unit_type",
        "created_by",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "id_inventory_movement",
        "id_location__name",
        "id_location__code",
        "id_material__name",
        "movement_type__name",
    )

    list_filter = (
        "movement_type",
        "unit_type",
        "created_at",
        "updated_at",
    )
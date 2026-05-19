from django.contrib import admin
from .models import Country, Currency, Status


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
    )

    search_fields = (
        "name",
        "code",
    )


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
    )

    search_fields = (
        "name",
        "code",
    )


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "is_active",
    )
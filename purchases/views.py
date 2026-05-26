import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.db import transaction
from django.db.models import Max
from .models import PurchaseOrder, LinesPurchaseOrder, OrderStatus
from suppliers.models import Supplier
from materials.models import Material, Unit
from core.models import Currency


def get_supplier_details(request, supplier_id):
    supplier = get_object_or_404(Supplier, id_supplier=supplier_id)

    data = {
        "id_supplier": supplier.id_supplier,
        "name": supplier.name,
        "legal_name": supplier.legal_name,
        "tax_id": supplier.tax_id,
        "address": supplier.address,
        "city": supplier.city,
        "state_province": supplier.state_province,
        "country": supplier.country,
        "zip_code": supplier.zip_code,
        "phone": supplier.phone,
        "email": supplier.email,
        "contact_name": supplier.contact_name,
        "payment_terms": supplier.payment_terms,
        "currency": supplier.currency.code if supplier.currency else "",
    }

    return JsonResponse(data)


def get_material_details(request, material_id):
    material = get_object_or_404(Material, id_material=material_id)

    data = {
        "id_material": material.id_material,
        "unit": material.unit.symbol,
        "description": material.description,
    }
    return JsonResponse(data)


def purchase_order_form(request):
    context = {"title": "Create New Purchase Order"}
    return render(request, "purchases/purchase_order_create.html", context)


def purchase_order_list(request):
    purchase_orders = PurchaseOrder.objects.all().order_by("-created_at")

    context = {
        "title": "Purchase Orders List",
        "purchase_orders": purchase_orders,
    }

    return render(request, "purchases/purchase_order_list.html", context)


@csrf_exempt
@require_POST
@transaction.atomic
def create_purchase_order(request):
    try:
        data = json.loads(request.body)

        supplier_id_str = data.get("id_supplier")
        estimated_delivery_date = data.get("estimated_delivery_date")
        lines_data = data.get("lines", [])

        if not supplier_id_str or not estimated_delivery_date or not lines_data:
            return JsonResponse(
                {
                    "error": "Missing required fields: supplier, delivery date or line items."
                },
                status=400,
            )

        try:
            supplier = get_object_or_404(Supplier, id_supplier=supplier_id_str)
            status = get_object_or_404(OrderStatus, pk=2)
        except Exception:
            return JsonResponse(
                {"error": "Invalid Supplier ID or default Order Status not found."},
                status=400,
            )

        max_id_result = PurchaseOrder.objects.aggregate(max_id=Max("id_purchase_order"))
        last_id_str = max_id_result.get("max_id")

        next_po_number = 1

        if last_id_str:
            try:
                next_po_number = int(last_id_str) + 1
            except ValueError:
                print(f"Warning: The last ID '{last_id_str}' is not a number.")
                next_po_number = 1

        next_po_id = str(next_po_number)

        purchase_order = PurchaseOrder.objects.create(
            id_purchase_order=next_po_id,
            id_supplier=supplier,
            estimated_delivery_date=estimated_delivery_date,
            status=status,
            created_by=request.user,
        )

        for i, line_data in enumerate(lines_data, start=1):
            material_id = line_data.get("id_material")
            unit_symbol = line_data.get("unit_material")
            currency_symbol = line_data.get("currency_supplier")
            quantity = line_data.get("quantity")
            price = line_data.get("price")
            position = line_data.get("position", i)

            if (
                not material_id
                or not unit_symbol
                or not currency_symbol
                or not quantity
                or not price
            ):
                raise ValueError(f"Missing information in line {i}.")

            try:
                material = get_object_or_404(Material, id_material=material_id)
                unit_object = get_object_or_404(Unit, symbol__iexact=unit_symbol)
                currency_obj = get_object_or_404(Currency, code__iexact=currency_symbol)
            except Exception:
                raise ValueError(
                    f"Invalid material, unit or currency in line {i}. "
                    f"Material: {material_id}, Unit: {unit_symbol}, Currency: {currency_symbol}"
                )

            line_po_id = f"{next_po_id}-{str(position).zfill(3)}"

            LinesPurchaseOrder.objects.create(
                id_purchase_order_line=line_po_id,
                id_purchase_order=purchase_order,
                id_material=material,
                position=position,
                quantity=quantity,
                unit_material=unit_object,
                price=price,
                currency_supplier=currency_obj,
                received_quantity=0,
                created_by=request.user,
            )

        response_data = {
            "success": True,
            "id_purchase_order": next_po_id,
            "message": f"Purchase Order {next_po_id} created successfully.",
            "redirect_url": "/purchases/list/",
        }

        return JsonResponse(response_data, status=201)

    except ValueError as e:
        return JsonResponse({"error": f"Validation Error: {str(e)}"}, status=400)

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON format in request body."},
            status=400,
        )

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return JsonResponse(
            {"error": f"An unexpected server error occurred: {str(e)}"},
            status=500,
        )

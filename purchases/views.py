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
        "currency": supplier.currency,
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

    context = {"title": "Create New Purchases Order"}

    return render(request, "purchases/purchase_order_create.html", context)


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
                    "error": "Missing required fields (Supplier ID, Delivery Date, or Line Items)."
                },
                status=400,
            )

        try:
            supplier_id_value = supplier_id_str
            supplier = get_object_or_404(Supplier, id_supplier=supplier_id_value)
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
                print(f"Warning: The last ID'{last_id_str}' is not number.")
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
                unit_symbol = lines_data.get("unit_material")
                currency_symbol = line_data.get("currency_supplier")
                quantity = line_data.get("quantity")
                price = line_data.get("price")
                position = line_data("position", i)

                try:
                    material = get_object_or_404(Material, id_material=material_id)
                    unit_object = get_object_or_404(Unit, symbol=currency_symbol)
                    currency_obj = get_object_or_404(Currency, symbol=currency_symbol)
                except Material.DoesNotExist:
                    raise ValueError(
                        f"Material ID '{material_id}' not found for line {i}."
                    )
                except Unit.DoesNotExist:
                    raise ValueError(
                        f"Unit symbol '{unit_symbol}' not found for line {i}."
                    )
                except Currency.DoesNotExist:
                    raise ValueError(
                        f"Currency symbol '{currency_symbol}' not found for line {i}."
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
                    received_quatity=0,
                    created_by=request.user,
                )

            response_data = {
                'success': True,
                'id_purchase_order': next_po_id,
                'message': f"Purchase Order {next_po_id} created succesfully.",
                'redirect_url': '/purchases/list/',
            }
            return JsonResponse(response_data, status=201)

    except ValueError as e:
        return JsonResponse({'error': f'Valiation Error: {str(e)}'}, 
                            status=400)
    except json.JSONDecodeError:
        return JsonResponse(
            {'error': 'Invalid JSON format in request body.'}, 
            status=400)

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return JsonResponse(
        {'error': f'An unexpected server error occurred: {str(e)}'},
        status=500
    )

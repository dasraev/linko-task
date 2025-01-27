from dataclasses import dataclass
from typing import List
from django.shortcuts import get_object_or_404
from django.db.models.functions import ExtractHour
from django.db.models import Sum,F
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order,Product,OrderProduct

@dataclass
class OrderSchema:
    product_id: int
    quantity: int


def bulk_create_order(user, orders :List[OrderSchema]):
    _order = Order.objects.create(
        total_price=0,
        user=user
    )
    total_price = 0
    order_product_list = []
    for order in orders:
        product = get_object_or_404(Product, id=order.quantity)

        order_product_list.append(
            OrderProduct(
                order=_order,
                product=product,
                quantity=order.quantity,
                price=product.price * order.quantity
            )
        )
        total_price += product.price * order.quantity
    OrderProduct.objects.bulk_create(order_product_list)
    _order.total_price = total_price
    _order.save()




class ReportListApiView(APIView):
    def get(self, request):
        product_hour_sales = (
            OrderProduct.objects
            .annotate(hour=ExtractHour(F('order__created_at')))
            .values('product__id', 'product__name', 'hour')
            .annotate(total_quantity=Sum('quantity'),total_price=F('price'))
        )
        data = {}
        for item in product_hour_sales:
            product_id = item['product__id']
            total_quantity = item['total_quantity']
            total_price = item['total_price']

            if product_id in data:
                if data[product_id]['total_quantity'] < total_quantity:
                    data[product_id] = {
                        "product_id": product_id,
                        "product_name": item['product__name'],
                        "hour": item['hour'],
                        "total_quantity": total_quantity,
                        "total_price": total_price,
                    }
            else:
                data[product_id] = {
                    "product_id": product_id,
                    "product_name": item['product__name'],
                    "hour": item['hour'],
                    "total_quantity": total_quantity,
                    "total_price": total_price,
                }

        response_data = sorted(list(data.values()), key=lambda x: x['total_price'], reverse=True)

        return Response(response_data)

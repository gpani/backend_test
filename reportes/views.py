from collections import OrderedDict
from rest_framework import generics, status
from django.http import FileResponse
from rest_framework.response import Response
import pandas as pd
from django.db.models import Sum, F, Aggregate, CharField
from .serializers import FileUploadSerializer
from .models import Customer, Product, Order, OrderProduct


class GroupConcat(Aggregate):
    function = 'GROUP_CONCAT'
    template = '%(function)s(%(expressions)s%(separator)s)'

    def __init__(self, expression, separator=' ', **extra):
        super(GroupConcat, self).__init__(
            expression,
            separator=' , "%s"' % separator,
            output_field=CharField(),
            **extra)


def get_product_count(products):
    count = {}
    for product_id in products.split(' '):
        if product_id in count:
            count[product_id] += 1
        else:
            count[product_id] = 1
    return count


class UploadFileView(generics.CreateAPIView):
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customers_reader = pd.read_csv(serializer.validated_data['customers'])
        products_reader = pd.read_csv(serializer.validated_data['products'])
        orders_reader = pd.read_csv(serializer.validated_data['orders'])

        Customer.objects.all().delete()
        Product.objects.all().delete()
        Order.objects.all().delete()
        OrderProduct.objects.all().delete()

        for _, row in customers_reader.iterrows():
            new_customer = Customer(
                id=row['id'],
                first_name=row['firstname'],
                last_name=row['lastname'],
            )
            new_customer.save()

        for _, row in products_reader.iterrows():
            new_product = Product(
                id=row['id'],
                name=row['name'],
                cost=row['cost'],
            )
            new_product.save()

        for _, row in orders_reader.iterrows():
            new_order = Order(
                id=row['id'],
                customer=Customer.objects.get(pk=row['customer']),
            )
            new_order.save()
            for product_id, count in get_product_count(row['products']).items():
                product = Product.objects.get(pk=product_id)
                OrderProduct(order=new_order, product=product, count=count).save()
        return Response({"status": "success"},
                        status.HTTP_201_CREATED)


class DownloadFileView(generics.RetrieveAPIView):

    def get(self, request, report, *args, **kwargs):
        match report:
            case 1:
                df = pd.DataFrame(list(
                    OrderProduct.objects.annotate(
                        cost=F("product__cost") * F("count")).values("order").order_by(
                        "order").annotate(total=Sum("cost"))))
                df.rename(columns={'order': 'id'}, inplace=True)
                file_name = "order_prices.csv"
            case 2:
                df = pd.DataFrame(list(
                    OrderProduct.objects.values("product").annotate(
                        customer_ids=GroupConcat("order__customer"))
                ))
                df.rename(columns={'product': 'id'}, inplace=True)
                df["customer_ids"] = (df["customer_ids"].str.split().apply(
                    lambda x: OrderedDict.fromkeys(x).keys()).str.join(" "))
                file_name = "product_customers.csv"
            case 3:
                df = pd.DataFrame(list(
                    OrderProduct.objects.annotate(
                        order_cost=F("product__cost") * F("count")).values(
                        "order__customer", "order__customer__first_name", "order__customer__last_name").annotate(
                        total=Sum("order_cost")).order_by('-total')
                ))
                df.rename(columns={
                    'order__customer': 'id',
                    'order__customer__first_name': 'firstname',
                    'order__customer__last_name': 'lastname',
                }, inplace=True)
                file_name = "customer_ranking.csv"
            case _:
                return Response({"status": "fail"},
                                status.HTTP_400_BAD_REQUEST)
        csv_buffer = df.to_csv(index=False)
        response = FileResponse(csv_buffer, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

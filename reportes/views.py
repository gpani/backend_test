from rest_framework import generics, status
import pandas as pd
from rest_framework.response import Response
from .serializers import FileUploadSerializer
from .models import Customer, Product, Order, OrderProduct

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
    file_type = None  # debe ser customers, products, orders

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        reader = pd.read_csv(file)
        match self.file_type:
            case 'customers':
                for _, row in reader.iterrows():
                    new_customer = Customer(
                        id=row['id'],
                        first_name=row['firstname'],
                        last_name=row['lastname'],
                    )
                    new_customer.save()
                return Response({"status": "success"},
                                status.HTTP_201_CREATED)
            case 'products':
                for _, row in reader.iterrows():
                    new_product = Product(
                        id=row['id'],
                        name=row['name'],
                        cost=row['cost'],
                    )
                    new_product.save()
                return Response({"status": "success"},
                                status.HTTP_201_CREATED)
            case 'orders':
                for _, row in reader.iterrows():
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
        return Response({"status": "fail"},
                        status.HTTP_400_BAD_REQUEST)

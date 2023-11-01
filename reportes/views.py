from django.shortcuts import render
from rest_framework import generics, status
import pandas as pd
from rest_framework.response import Response
from .serializers import FileUploadSerializer
from .models import Customer, Product


class UploadFileView(generics.CreateAPIView):
    serializer_class = FileUploadSerializer
    file_type = None # debe ser customers, products, orders

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
                pass
        return Response({"status": "fail"},
                        status.HTTP_400_BAD_REQUEST)

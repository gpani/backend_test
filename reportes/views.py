from django.shortcuts import render
from rest_framework import generics, status
import pandas as pd
from rest_framework.response import Response
from .serializers import FileUploadSerializer
from .models import Customer


class UploadFileView(generics.CreateAPIView):
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        reader = pd.read_csv(file)
        for _, row in reader.iterrows():
            new_customer = Customer(
                id=row['id'],
                first_name=row['firstname'],
                last_name=row['lastname'],
            )
            new_customer.save()
        return Response({"status": "success"},
                        status.HTTP_201_CREATED)

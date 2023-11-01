from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
import tempfile
import pandas as pd
from pandas import testing as tm
from io import BytesIO

CUSTOMERS = b"""
id,firstname,lastname
0,John,Maxwell
1,John,Heisenberg
2,John,Fermi
"""

PRODUCTS = b"""
id,name,cost
0,screwdriver,1
1,wrench,2
2,hammer,3
"""

ORDERS = b"""
id,customer,products
0,0,1 0 1 0
1,2,0 2 0 1 1
2,1,2 1 0
"""


class ReportesTests(TestCase):
    def SetUp(self):
        self.client = APIClient()

    def test_functional(self):
        self.customers_file = tempfile.NamedTemporaryFile(suffix='.csv')
        self.customers_file.write(CUSTOMERS)
        self.customers_file.seek(0)
        self.products_file = tempfile.NamedTemporaryFile(suffix='.csv')
        self.products_file.write(PRODUCTS)
        self.products_file.seek(0)
        self.orders_file = tempfile.NamedTemporaryFile(suffix='.csv')
        self.orders_file.write(ORDERS)
        self.orders_file.seek(0)
        response = self.client.post("/data/", {
            "customers": self.customers_file,
            "products": self.products_file,
            "orders": self.orders_file
        }, format='multipart')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get("/reports/1/")
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        data = b''.join(response.streaming_content)
        df = pd.read_csv(BytesIO(data))
        values = pd.Series([6, 9, 6], name="total")
        tm.assert_series_equal(df["total"], values)

        response = self.client.get("/reports/2/")
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        data = b''.join(response.streaming_content)
        df = pd.read_csv(BytesIO(data))
        values = pd.Series(["0 2 1", "0 2 1", "2 1"], name="customer_ids")
        tm.assert_series_equal(df["customer_ids"], values)

        response = self.client.get("/reports/3/")
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        data = b''.join(response.streaming_content)
        df = pd.read_csv(BytesIO(data))
        values = pd.Series([9, 6, 6], name="total")
        tm.assert_series_equal(df["total"], values)

    def test_upload_missing_file(self):
        self.customers_file = tempfile.NamedTemporaryFile(suffix='.csv')
        self.customers_file.write(CUSTOMERS)
        self.customers_file.seek(0)
        self.products_file = tempfile.NamedTemporaryFile(suffix='.csv')
        self.products_file.write(PRODUCTS)
        self.products_file.seek(0)
        response = self.client.post("/data/", {
            "customers": self.customers_file,
            "products": self.products_file,
        }, format='multipart')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

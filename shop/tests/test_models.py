from datetime import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from shop.models import PromoCode, Product, Purchase
from decimal import Decimal


class ProductTestCase(TestCase):
    def setUp(self):
        Product.objects.create(name="book", price="740")
        Product.objects.create(name="pencil", price="50")

    def test_correctness_types(self):                   
        self.assertIsInstance(Product.objects.get(name="book").name, str)
        self.assertIsInstance(Product.objects.get(name="book").price, int)
        self.assertIsInstance(Product.objects.get(name="pencil").name, str)
        self.assertIsInstance(Product.objects.get(name="pencil").price, int)        

    def test_correctness_data(self):
        self.assertTrue(Product.objects.get(name="book").price == 740)
        self.assertTrue(Product.objects.get(name="pencil").price == 50)


class PurchaseTestCase(TestCase):
    def setUp(self):
        self.product_book = Product.objects.create(name="book", price="740")
        self.datetime = datetime.now()
        Purchase.objects.create(product=self.product_book,
                                person="Ivanov",
                                address="Svetlaya St.")

    def test_correctness_types(self):
        self.assertIsInstance(Purchase.objects.get(product=self.product_book).person, str)
        self.assertIsInstance(Purchase.objects.get(product=self.product_book).address, str)
        self.assertIsInstance(Purchase.objects.get(product=self.product_book).date, datetime)

    def test_correctness_data(self):
        self.assertTrue(Purchase.objects.get(product=self.product_book).person == "Ivanov")
        self.assertTrue(Purchase.objects.get(product=self.product_book).address == "Svetlaya St.")
        self.assertTrue(Purchase.objects.get(product=self.product_book).date.replace(microsecond=0) == \
            self.datetime.replace(microsecond=0))


class PromoCodeTestCase(TestCase):
    def setUp(self):
        """Создаём тестовые промокоды"""
        PromoCode.objects.create(name="SUMMER2024", discount_percent=15)
        PromoCode.objects.create(name="WINTER50", discount_percent=50)

    def test_correctness_types(self):
        """Проверка типов полей промокода"""
        promo = PromoCode.objects.get(name="SUMMER2024")
        self.assertIsInstance(promo.name, str)
        self.assertIsInstance(promo.discount_percent, Decimal)

    def test_correctness_data(self):
        """Проверка корректности значений промокода"""
        promo = PromoCode.objects.get(name="SUMMER2024")
        self.assertEqual(promo.name, "SUMMER2024")
        self.assertEqual(promo.discount_percent, Decimal('15'))

        promo_winter = PromoCode.objects.get(name="WINTER50")
        self.assertEqual(promo_winter.discount_percent, Decimal('50'))

    def test_str_method(self):
        """Проверка строкового представления промокода"""
        promo = PromoCode.objects.get(name="SUMMER2024")
        self.assertEqual(str(promo), "SUMMER2024 - 15%")

        promo_winter = PromoCode.objects.get(name="WINTER50")
        self.assertEqual(str(promo_winter), "WINTER50 - 50%")

    def test_unique_name_constraint(self):
        """Проверка уникальности названия промокода"""
        with self.assertRaises(IntegrityError):
            PromoCode.objects.create(name="SUMMER2024", discount_percent=20)

    def test_discount_percent_max_digits(self):
        """Проверка максимального значения скидки (99%)"""
        promo = PromoCode.objects.create(name="MAX99", discount_percent=99)
        self.assertEqual(promo.discount_percent, Decimal('99'))

    def test_max_length_name(self):
        """Проверка максимальной длины названия (100 символов)"""
        long_name = "A" * 100
        promo = PromoCode.objects.create(name=long_name, discount_percent=10)
        self.assertEqual(len(promo.name), 100)

    def test_max_length_name_exceeded(self):
        """Проверка превышения максимальной длины названия"""
        too_long_name = "A" * 101
        with self.assertRaises(ValidationError):
            promo = PromoCode(name=too_long_name, discount_percent=10)
            promo.full_clean()

    def test_promo_code_deletion_protection(self):
        """Проверка защиты от удаления промокода с существующими покупками"""
        promo = PromoCode.objects.get(name="SUMMER2024")
        product = Product.objects.create(name="Test Product", price=1000)
        Purchase.objects.create(
            product=product,
            person="Test Person",
            address="Test Address",
            promo_code=promo
        )

        from django.db.models import ProtectedError
        with self.assertRaises(ProtectedError):
            promo.delete()

    def test_purchase_without_promo_code(self):
        """Проверка покупки без промокода (null=True, blank=True)"""
        product = Product.objects.create(name="Pencil", price=50)
        purchase = Purchase.objects.create(
            product=product,
            person="Petr",
            address="SPb"
        )

        self.assertIsNone(purchase.promo_code)

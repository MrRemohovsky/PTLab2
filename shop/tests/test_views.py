import json
from django.test import TestCase, Client
from shop.models import Purchase, PromoCode, Product


class PurchaseCreateTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_webpage_accessibility(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class PurchaseCreateViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(name="Book", price=740)
        self.promo = PromoCode.objects.create(name="DISCOUNT10", discount_percent=10)
        self.url = f'/buy/{self.product.id}/'

    def test_purchase_get_status_code(self):
        """Проверка доступности формы покупки"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_purchase_product_in_context(self):
        """Проверка передачи товара в контекст"""
        response = self.client.get(self.url)
        self.assertIn('product', response.context)
        self.assertEqual(response.context['product'], self.product)

    def test_purchase_post_creates_purchase(self):
        """Проверка создания покупки через POST"""
        initial_count = Purchase.objects.count()
        response = self.client.post(self.url, {
            'person': 'Ivanov',
            'address': 'Moscow St.',
            'promo_code': self.promo.id
        })

        self.assertEqual(Purchase.objects.count(), initial_count + 1)
        purchase = Purchase.objects.last()
        self.assertEqual(purchase.person, 'Ivanov')
        self.assertEqual(purchase.address, 'Moscow St.')
        self.assertEqual(purchase.product, self.product)
        self.assertEqual(purchase.promo_code, self.promo)

    def test_purchase_post_without_promo(self):
        """Проверка создания покупки без промокода"""
        response = self.client.post(self.url, {
            'person': 'Petr',
            'address': 'SPb St.'
        })

        purchase = Purchase.objects.last()
        self.assertEqual(purchase.person, 'Petr')
        self.assertIsNone(purchase.promo_code)


class CheckPromocodeViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.promo = PromoCode.objects.create(name="SUMMER50", discount_percent=50)
        self.url = '/check_promo/'

    def test_valid_promocode(self):
        """Проверка валидного промокода"""
        response = self.client.post(
            self.url,
            data=json.dumps({'promo_name': 'SUMMER50'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['valid'])
        self.assertEqual(data['discount_percent'], '50')
        self.assertEqual(data['promo_id'], self.promo.id)

    def test_invalid_promocode(self):
        """Проверка невалидного промокода"""
        response = self.client.post(
            self.url,
            data=json.dumps({'promo_name': 'NONEXISTENT'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['valid'])
        self.assertEqual(data['message'], 'Купон не найден')

    def test_case_insensitive_promocode(self):
        """Проверка нижнего регистра при поиске промокода"""
        response = self.client.post(
            self.url,
            data=json.dumps({'promo_name': 'summer50'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['valid'])
        self.assertEqual(data['discount_percent'], '50')

    def test_invalid_json(self):
        """Проверка некорректного JSON"""
        response = self.client.post(
            self.url,
            data='invalid json',
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['valid'])
        self.assertEqual(data['message'], 'Ошибка сервера')

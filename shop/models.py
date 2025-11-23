from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()

class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    person = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    promo_code = models.ForeignKey('shop.PromoCode', on_delete=models.PROTECT, null=True, blank=True)

class PromoCode(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Промокод")
    discount_percent = models.DecimalField(
        max_digits=2, decimal_places=0,
        verbose_name="Скидка в процентах",
        help_text="Значение скидки в процентах (например, 15)"
    )

    def __str__(self):
        return f"{self.name} - {self.discount_percent}%"

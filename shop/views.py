from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
import json

from .models import Product, Purchase, PromoCode

def index(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'shop/index.html', context)


class PurchaseCreate(CreateView):
    model = Purchase
    fields = ['person', 'address', 'promo_code']
    template_name = 'shop/purchase_form.html'
    success_url = reverse_lazy('shop:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get('product_id')
        context['product'] = get_object_or_404(Product, id=product_id)
        return context

    def form_valid(self, form):
        product_id = self.kwargs.get('product_id')
        form.instance.product_id = product_id
        self.object = form.save()
        return HttpResponse(f'Спасибо за покупку, {self.object.person}!')


@require_http_methods(["POST"])
def check_promocode(request):
    """API для проверки скидочного купона"""
    try:
        data = json.loads(request.body)
        promo_name = data.get('promo_name', '').strip()

        promo_code = PromoCode.objects.get(name__iexact=promo_name)
        return JsonResponse({
            'valid': True,
            'discount_percent': promo_code.discount_percent,
            'promo_id': promo_code.id,
            'message': f'Скидка {promo_code.discount_percent}% применена'
        })
    except PromoCode.DoesNotExist:
        return JsonResponse({'valid': False, 'message': 'Купон не найден'})
    except Exception as e:
        return JsonResponse({'valid': False, 'message': 'Ошибка сервера'})
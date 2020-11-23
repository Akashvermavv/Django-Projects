from django.shortcuts import render
from django.views.generic import ListView,DetailView,View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404,HttpResponse,JsonResponse
from billing.models import BillingProfile
from .models import Order,ProductPurchase



class OrderListView(LoginRequiredMixin,ListView):
    def get_queryset(self):
        return Order.objects.by_request(self.request).not_created()


class OrderDetailView(LoginRequiredMixin,DetailView):

    def get_object(self):
        print('in get object --',self.kwargs)
        # return Order.objects.get(id=self.kwargs.get('id'))
        # return Order.objects.get(slug=self.kwargs.get('slug'))
        qs = Order.objects.by_request(self.request).filter(order_id=self.kwargs.get('order_id'))
        print('qs ---',qs.count())
        if qs.count()==1:
            return qs.first()
        print('end -')
        raise Http404("the error is occur")

    # def get_queryset(self):
    #     return Order.objects.by_request(self.request)

class LibraryView(LoginRequiredMixin,ListView):
    template_name = 'orders/library.html'

    def get_queryset(self):
        print('get queryset data --',ProductPurchase.objects.by_request(self.request).digital())
        # return ProductPurchase.objects.by_request(self.request).digital()
        return ProductPurchase.objects.products_by_request(self.request)


class VerifyOwnership(View):
    def get(self,request,*args,**kwargs):
        if request.is_ajax():
            data = request.GET
            product_id = data.get('product_id',None)
            if product_id is not None:
                product_id = int(product_id)
                ownership_ids = ProductPurchase.objects.products_by_id(request)
                if product_id in ownership_ids:
                    return JsonResponse({'owner':True})
            return JsonResponse({'owner':False})
        raise Http404














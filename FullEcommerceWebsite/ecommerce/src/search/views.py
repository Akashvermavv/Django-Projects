from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView
from products.models import Product

"""
__icontains  = field contains this
__iexact     = fields is exactly this  


"""

class SearchProductView(ListView):
    template_name = "search/view.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SearchProductView,self).get_context_data(**kwargs)
        # context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        # print('context auery is --',context)
        return context

    def get_queryset(self,*args,**kwargs):
        request = self.request
        # return Product.objects.all()
        method_dict = request.GET
        query = method_dict.get('q',None)
        print('query is --',query)



        if query is not None:
            # lookups = Q(title__icontains=query) | Q(description__icontains=query)
            # return Product.objects.filter(lookups).distinct()
            return Product.objects.search(query)
        # return Product.objects.none()
        return Product.objects.featured()






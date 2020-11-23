from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import ListView,DetailView,View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product,ProductFile
from django.http import Http404,HttpResponse,JsonResponse
from carts.models import Cart
from analytics.mixins import ObjectViewedMixin
from django.contrib import  messages
from category.models import Categories



# def  category_wise(request):
#     # def get(self,request,*args,**kwargs):
#     print('ProductCategoryWise  --->')
#     # if request.is_ajax():
#     #     print('ajax call in ProductCategoryWise ')
#     #     data = request.GET
#     #     print('data is ---',data)
#     #     product_id = data.get('product_id',None)
#     #     # if product_id is not None:
#     #     #     product_id = int(product_id)
#     #     #     ownership_ids = ProductPurchase.objects.products_by_id(request)
#     #     #     if product_id in ownership_ids:
#     #     #         return JsonResponse({'owner':True})
#     #     return JsonResponse({'owner':False})
#     # # raise Http404
#     # return HttpResponse('hello all')


class ProductFeaturedListView(ListView):
    template_name = 'products/list.html'

    def get_queryset(self,*args,**kwargs):
        request = self.request
        return Product.objects.featured()

class ProductFeaturedDetailView(ObjectViewedMixin,DetailView):
    queryset = Product.objects.all().featured()
    template_name = 'products/featured-detail.html'

    # def get_queryset(self,*args,**kwargs):
    #     request = self.request
    #     return Product.objects.featured()

class UserProductHistoryView(LoginRequiredMixin,ListView):
    # queryset = Product.objects.all()
    template_name = 'products/user-history.html'

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     context = super(ProductListView,self).get_context_data(**kwargs)
    #     print('context data in class view --',context)
    #     return context

    def get_context_data(self, *args, **kwargs):
        context = super(UserProductHistoryView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context

    def get_queryset(self,*args,**kwargs):
        request = self.request
        views = request.user.objectviewed_set.by_model(Product,model_queryset=False)#all().filter(content_type='product')
        # viewed_ids = [x.object_id for x in views]
        # print('viewed_ids --->',viewed_ids)
        # return Product.objects.filter(pk__in=viewed_ids)
        return views





class ProductListView(ListView):
    # queryset = Product.objects.all()
    # print('queryset in ProductListView --',queryset)
    template_name = 'products/list.html'

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     context = super(ProductListView,self).get_context_data(**kwargs)
    #     print('context data in class view --',context)
    #     return context

    # def get(self, request, *args, **kwargs):
    #     # print('%%% get ProductListView %%%')
    #     # print('in ProductListView')
    #     # print('context data is ', *args, **kwargs)
    #     # context = self.get_context_data()
    #     # print('context data is ', context)
    #     # cart_obj, new_obj = Cart.objects.new_or_get(self.request)
    #     # context['cart'] = cart_obj
    #     # context['categories'] = Categories.objects.all()
    #     # return context
    #     return HttpResponse('<h1>Hello all</h1>')
    #     context={'object_list':Product.objects.all(),}
    #     return context

    def get_context_data(self, *args, **kwargs):
        print('in ProductListView')
        print('context data is ',*args,**kwargs)
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        print('context data is ', context)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        context['categories'] = Categories.objects.all()
        context['count'] = Product.objects.all().count()
        return context

    def get_queryset(self,*args,**kwargs):
        request = self.request
        return Product.objects.all()

def product_list_view(request):
    queryset = Product.objects.all()
    context ={
        "object_list":queryset
    }
    return render(request,"products/list.html",context)


class ProductDetailSlugView(ObjectViewedMixin,DetailView):
    queryset = Product.objects.all()
    template_name = 'products/detail.html'

    # def get(self,*args,**kwargs):
    #     return HttpResponse('<h1>hello all </h1>')

    def get_context_data(self, *args,**kwargs):
        context = super(ProductDetailSlugView,self).get_context_data(*args,**kwargs)
        cart_obj , new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context

    def get_object(self, *args,**kwargs):
        request = self.request
        slug = self.kwargs.get('slug')
        # instance = get_object_or_404(Product,slug=slug,active=True)

        try:
            instance = Product.objects.get(slug=slug,active=True)
        except Product.DoesNotExist:
            raise Http404("Not Found.")
        except Product.MultipleObjectsReturned:
            qs = Product.objects.filter(slug=slug,active=True)
            instance = qs.first()
        except:
            raise Http404("NOOOOOOOOO")
        # object_viewed_signal.send(instance.__class__,instance=instance,request=request)

        return instance

from wsgiref.util import FileWrapper  # this used  in django
from mimetypes import guess_type
from django.conf import settings
import os
from orders.models import ProductPurchase


class ProductDownloadView(View):
    def get(self,request,*args,**kwargs):
        slug = kwargs.get('slug')
        pk = kwargs.get('pk')
        print('slug --##',slug)
        print('pk --##',pk)
        # qs = Product.objects.filter(slug=slug)
        # if qs.count() != 1:
        #     raise Http404("Product not found")
        # product_obj = qs.first()
        # download_qs = product_obj.get_downloads().filter(pk=pk)  # queryset -- ProductFile.objects.filter(product=product_obj)
        # if download_qs.count() !=1:
        #     raise Http404("Download not found")

        downloads_qs = ProductFile.objects.filter(pk=pk,product__slug=slug)
        if downloads_qs.count() !=1:
            raise Http404(" Download not found")
        download_obj = downloads_qs.first()

        # permission checks
        can_download = False
        user_ready = True
        if download_obj.user_required:
            if not request.user.is_authenticated:
                user_ready = False


        purchased_products = Product.objects.none()
        if download_obj.free:
            can_download=True
            user_ready=True
        else:
            # not free
            purchased_products  = ProductPurchase.objects.products_by_request(request)
            print('purchased products qs --',purchased_products)
            print('purchased download_obj.product qs --',download_obj.product)
            if download_obj.product in purchased_products:
                can_download = True
        if not can_download or not user_ready:
            messages.error(request,"You do not have access to download this item")
            return redirect(download_obj.get_default_url())

        file_root = settings.PROTECTED_ROOT
        filepath = download_obj.file.path  # .url /media/
        final_filepath = os.path.join(file_root,filepath)  # where the file is stored
        with open(final_filepath,'rb') as f:
            wrapper = FileWrapper(f)
            mimetype = 'application/force-download'
            gussed_mimetype = guess_type(filepath)[0]  # filename.mp4
            if gussed_mimetype:
                mimetype = gussed_mimetype
            response = HttpResponse(wrapper, content_type=mimetype)
            response['Content-Disposition'] = f"attachment;filename={download_obj.name}"
            response['X-SendFile'] = str(download_obj.name)
            return response
        # return redirect(download_obj.get_default_url())


        # # form the download

        # content = "some text"
        # mimetype = 'text/plain'
        # # response = HttpResponse(download_obj.get_download_url())
        # response = HttpResponse(content,content_type=mimetype)
        # response['Content-Disposition'] = "attachment;filename=SomeText.txt"
        # response['X-SendFile'] = "SomeText.txt"
        # response = HttpResponse("hello")
        # return response



class ProductDetailView(ObjectViewedMixin,DetailView):
    queryset = Product.objects.all()
    template_name = 'products/detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView,self).get_context_data(**kwargs)
        print('context data in detail  class view --',context)
        return context

    # def get_object(self, *args,**kwargs):
    #     request = self.request
    #     pk = self.kwargs.get('pk')
    #     instance = Product.objects.get_by_id(id=pk)
    #     if instance is None:
    #         raise Http404("Product not Found")
    #     return instance

    def get_queryset(self,*args,**kwargs):
        request = self.request
        pk = self.kwargs.get('pk')
        return Product.objects.filter(pk=pk)


def product_detail_view(request,pk=None,*args,**kwargs):
    # queryset = Product.objects.get(pk=pk,featured=True)
    # queryset = Product.objects.all()
    # instance = get_object_or_404(Product,pk=pk)     #  1st option

    instance=''
    # try:                                              # 2nd option
    #     instance = Product.objects.get(id=pk)
    # except Product.DoesNotExist:
    #     print('no product here')
    #     raise Http404("Product  not Found")
    # except:
    #     print("some other error occur")

    # qs = Product.objects.filter(id=pk)                  # 3rd option
    # if qs.exists() and qs.count()==1:
    #     instance = qs.first()
    # else:
    #     raise Http404("Product not Found")


    # 4th option

    instance = Product.objects.get_by_id(id=pk)
    if instance is None:
        raise Http404("Product not Found %%%")

    context ={
        "object":instance
    }
    return render(request,"products/detail.html",context)



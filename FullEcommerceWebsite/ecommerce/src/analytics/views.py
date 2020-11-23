from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse,JsonResponse
from django.views.generic import TemplateView,View
from orders.models import Order
from django.db.models import Count,Sum,Avg
from django.utils import timezone
import datetime
import random


class SalesAjaxView(View):
    def get(self,request,*args,**kwargs):
        data={}
        if request.user.is_staff:
            qs = Order.objects.all().by_weeks_range(week_ago=5,number_of_weeks=5)
            if request.GET.get('type') =="week":
                days = 7
                start_date = timezone.now().today() - datetime.timedelta(days=days-1)

                datetime_list=[]
                labels_list=[]
                sales_items_list=[]
                # sales_items=[]
                # datetime_list =[start_date + datetime.timedelta(days=x) for x in range(0,days) ]
                # [(labels_list.append(e.strftime("%a")),sales_items_list.append(random.randint(10,100000))) for e in datetime_list]
                for x in range(0,days):
                    new_time = start_date + datetime.timedelta(days=x)
                    datetime_list.append(new_time)
                    labels_list.append(new_time.strftime("%a"))
                    new_qs = qs.filter(updated__day=new_time.day,updated__month = new_time.month)
                    day_total = new_qs.totals_data()['total__sum'] or 0
                    # if day_total is None:
                    #     day_total=0
                    sales_items_list.append(day_total)
                print('datetime_list in Sales Ajax View --->',datetime_list)
                print('datetime_list in Sales Ajax View --->',labels_list)
                print('sales in Sales Ajax View --->',sales_items_list)


                # data['labels'] = ['Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun']
                data['labels'] = labels_list
                # data['data'] = [13, 21, 45, 607, 87, 43, 22]
                data['data'] = sales_items_list
            if request.GET.get('type') =="4weeks":
                data['labels'] = ['Four Weeks Ago','Three Weeks Ago','Two Weeks Ago','Last Week','This Week']
                # data['data'] = [123,1231,213,222]
                current = 5
                data['data']  = []
                for i in range(0,5):
                    new_qs = qs.by_weeks_range(week_ago=current,number_of_weeks=1)
                    sales_total = new_qs.totals_data()['total__sum'] or 0
                    print('4 weeks sales total --',sales_total)
                    # if sales_total is None:
                    #     sales_total=0
                    data['data'].append(sales_total)
                    current-=1

                print("data['data'] -->",data['data'])

        return JsonResponse(data)


class SalesView(LoginRequiredMixin,TemplateView):
    template_name = 'analytics/sales.html'

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            # return HttpResponse("Not Allowed",status=401)
            return render(self.request,"400.html",{})
        return super(SalesView,self).dispatch(*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(SalesView,self).get_context_data(**kwargs)
        # two_weeks_ago = timezone.now() - datetime.timedelta(days=14)
        # one_week_ago = timezone.now() - datetime.timedelta(days=6)

        # qs = Order.objects.all().by_range(start_date=two_weeks_ago,end_date=one_week_ago)
        # qs = Order.objects.all()
        # print('count of all objects -->', qs.count())
        qs = Order.objects.all().by_weeks_range(week_ago=10,number_of_weeks=10) #
        # qs = Order.objects.all().by_range(start_date=one_week_ago)
        # qs = Order.objects.all()#.by_range(start_date=one_week_ago)
        print('count of all objects -->',qs.count())
        context['orders']  = qs
        start_date =timezone.now().date()
        print('%%%%  start date -->',start_date)
        today_data = qs.by_range(start_date=start_date).get_sales_breakdown()
        print('%%%%  today data  -->', today_data)
        context['today'] = today_data
        context['this_week'] = qs.by_weeks_range(week_ago=1,number_of_weeks=1).get_sales_breakdown()
        context['this_four_week'] = qs.by_weeks_range(week_ago=5,number_of_weeks=4).get_sales_breakdown()
        # context['recent_orders']  = qs.recent().not_refunded()
        # context['recent_orders_data'] = context['recent_orders'].totals_data()
        # context['recent_orders_cart_data'] = context['recent_orders'].cart_data()
        # context['shipped_orders']  = qs.recent().not_refunded().by_status(status='shipped')
        # context['shipped_orders_data']  = context['shipped_orders'].totals_data()
        # context['paid_orders']  = qs.recent().not_refunded().by_status(status='paid')
        # context['paid_orders_data'] = context['paid_orders'].totals_data()


        # context['recent_cart_data'] = context['recent_orders'].aggregate(Avg("cart__products__price"),Count("cart__products"))

        # cart_price=0
        # for i in context['recent_orders']:
        #     for product in i.cart.products.all():
        #         cart_price += product.price
        # print('cart price total -->',cart_price)
        # print('cart price total -->',context['recent_orders_cart_data'])

        #  qs = Order.objects.all().annotate(product_avg =Avg('cart__products__price'),product_total=Sum('cart__products__price'),product_count=Count('cart__produc
        # ts'))

        #  ann = qs.annotate(product_avg =Avg('cart__products__price'),product_total=Sum('cart__products__price'),product_count=Count('cart__produc
        # ts'))

        return context



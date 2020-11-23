from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.conf import settings
from .models import Cart
from orders.models import Order
from products.models import Product
from accounts.forms import LoginForm,GuestForm
from billing.models import BillingProfile
from accounts.models import GuestEmail
from addresses.forms import AddressForm
from addresses.models import Address
from django.views.decorators.csrf import csrf_exempt

import  stripe

STRIPE_SECRET_KEY  = getattr(settings,"STRIPE_SECRET_KEY","sk_test_51HTjAFHGcIEXy6MZxvpNEUHviHVMMzR3o3MDrfQTQBEfMxu8dUkd6rXjqEgh7MaVgAFtM2iu2Dx8WFOl2qRYHOvk009J3t2eCu")
STRIPE_PUB_KEY  = getattr(settings,"STRIPE_PUB_KEY", "pk_test_51HTjAFHGcIEXy6MZq7tC7yVKQPoTfEgr4wStVSfyYo7MvppcEPyHCRNlPZevZoFjJUJGdbfhjY96Hx0HOJrhNqDA00OAjJoE5H")
stripe.api_key = STRIPE_SECRET_KEY




def cart_detail_api_view(request):
    cart_obj,new_obj = Cart.objects.new_or_get(request)
    products = [{"id":x.id,"url":x.get_absolute_url(),"name":x.name,"price":x.price} for x in cart_obj.products.all()]
    cart_data = {"products":products,"subtotal":cart_obj.subtotal,"total":cart_obj.total}
    return JsonResponse(cart_data)



# def cart_create(user=None):
#     cart_obj = Cart.objects.create(user=user)
#     print('New cart created')
#     return cart_obj


def cart_home(request):
    cart_obj,new_obj = Cart.objects.new_or_get(request)
    print('cart product is digital or not --',cart_obj.is_digital)
    # products = cart_obj.products.all()
    # total = 0
    # for x in products:
    #     total += x.price
    # print('total price is --',total)
    # cart_obj.total = total
    # cart_obj.save()
    return render(request, "carts/home.html", {"cart":cart_obj})

@csrf_exempt
def cart_update(request):
    print('post data --',request.POST)
    product_id = request.POST.get('product_id')
    # product_id = 1
    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print('Show message to user, product is gone?')
            return redirect("carts:home")
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        if product_obj in cart_obj.products.all():
            cart_obj.products.remove(product_obj)
            added = False
        else:
            cart_obj.products.add(product_obj)
            added = True
        # return redirect(product_obj.get_absolute_url())
        request.session['cart_items'] = cart_obj.products.count()

        if request.is_ajax():
            print('%%%%%%%%%%%%%%%%% request is ajax %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            json_data ={
                "added":added,
                "removed":not added,
                "cartItemCount":cart_obj.products.count()
            }
            return JsonResponse(json_data,status=200)
            # return JsonResponse({"message":"Error 400"},status_code=400)

    return redirect("carts:home")

def checkout_home(request):
    cart_obj,cart_created = Cart.objects.new_or_get(request)
    order_obj=None
    if cart_created or cart_obj.products.count() ==0:
        return redirect("carts:home")
    # else:
    #     order_obj,new_order_obj = Order.objects.get_or_create(cart=cart_obj)


    login_form = LoginForm(request=request)
    guest_form = GuestForm(request=request)
    address_form = AddressForm()
    # billing_address_form = AddressForm()
    billing_address_id = request.session.get("billing_address_id",None)

    shipping_address_required = not cart_obj.is_digital

    shipping_address_id = request.session.get("shipping_address_id",None)


    # guest_email_id = request.session.get('guest_email_id')
    #
    # if user.is_authenticated:
    #     'logged in user checkout; remember payment stuff'
    #     billing_profile,billing_profile_created = BillingProfile.objects.get_or_create(
    #                                                                             user=user,
    #                                                                             email= user.email
    #                                                                                 )
    # elif(guest_email_id is not None):
    #     'guest user checkout; auto reloads payment stuff'
    #     guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
    #     billing_profile, billing_guest_profile_created = BillingProfile.objects.get_or_create(
    #                                                                                     email=guest_email_obj.email
    #                                                                                     )
    # else:
    #     pass


    # if billing_profile is not None:
    #     order_qs = Order.objects.filter(cart=cart_obj,active=True)
    #     if order_qs.exists():
    #         order_qs.update(active=False)
    #     else:
    #         order_obj = Order.objects.create(
    #                             billing_profile = billing_profile,
    #                             cart = cart_obj
    #                             )


    billing_profile,billing_profile_created = BillingProfile.objects.new_or_get(request)
    print('billing profile --',billing_profile)
    print(' cart_obj --',cart_obj)
    address_qs = None
    has_card = False
    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile = billing_profile)
        order_obj,order_obj_created = Order.objects.new_or_get(billing_profile,cart_obj)
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(id =shipping_address_id)
            del request.session['shipping_address_id']
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(id =billing_address_id)
            del request.session['billing_address_id']
        if billing_address_id or shipping_address_id:
            order_obj.save()
        has_card = billing_profile.has_card

        """
        ----- next steps -----
        update order_obj to done ,"paid"  
        del request.session['cart_id']
        redirect "success"
        """


    print('@#################     method #############',request.method)
    if request.method=="POST":
        "some check that order is done"
        is_prepared = order_obj.check_done()
        print('is_prepared --',is_prepared)
        if is_prepared:
            did_charge, charge_msg = billing_profile.charge(order_obj)
            if did_charge:
                order_obj.mark_paid()
                request.session['cart_items'] = 0
                del request.session['cart_id']
                if not billing_profile.user:
                    # is this the best spot?
                    billing_profile.set_cards_inactive()
                return redirect("carts:success")
            else:
                print('charge msg --',charge_msg)
                return redirect("carts:checkout")

        #
        # order_qs = Order.objects.filter(billing_profile=billing_profile,cart=cart_obj,active=True)
        # print('order_qs --->',order_qs, order_qs.count())
        # if order_qs.count()==1:
        #     order_obj = order_qs.first()
        # else:
        #     # old_order_qs = Order.objects.exclude(billing_profile=billing_profile).filter(cart=cart_obj,active=True)
        #     # print("old_order_qs --",old_order_qs,old_order_qs.count())
        #     # if old_order_qs.exists():
        #     #     old_order_qs.update(active=False)
        #     order_obj = Order.objects.create(billing_profile=billing_profile,cart=cart_obj)

    context ={
        "object":order_obj,
        "billing_profile":billing_profile,
        "login_form":login_form,
        "guest_form":guest_form,
        "address_form":address_form,
        "address_qs":address_qs,
        "has_card":has_card,
        "publish_key":STRIPE_PUB_KEY,
        'shipping_address_required':shipping_address_required,
        # "billing_address_form":billing_address_form,
    }
    return render(request,"carts/checkout.html",context)

    # cart_id = request.session.get('cart_id',None)
    # print('cart_id is --',cart_id)
    #
    # qs = Cart.objects.filter(id=cart_id)
    # if qs.count() ==1:
    #     print('Cart ID exists')
    #     cart_obj = qs.first()
    #     print('cart_obj.user',cart_obj.user)
    #     if request.user.is_authenticated and cart_obj.user is None:
    #         cart_obj.user  = request.user
    #         cart_obj.save()
    # else:
    #     print('in else request.user is --',request.user)
    #     cart_obj = Cart.objects.new(user=request.user) #cart_create()
    # request.session['cart_id'] = cart_obj.id


    # if cart_id is None :# and isinstance(cart_id,int):
    #     print('------  create new cart ---')
    #     cart_obj = Cart.objects.create(user=None)
    #     print('cart_obj.id is ',cart_obj.id)
    #     request.session['cart_id'] = cart_obj.id
    #     # request.session['cart_id'] = 12
    # else:
    # print('---- cart already exist ---')
    # print('card is --',cart_id)
    # cart_obj = Cart.objects.get(id=cart_id)
    # print('cart obj is ',cart_obj)
    # return render(request, 'carts/home.html', {})

    # return render(request, 'carts/home.html', {})


    # print('session obj --',request.session)
    # print('dir ->',dir(request.session))
    #request.session.set_expiry(300)  # 5 minutes
    # key = request.session.session_key
    # print('key --',key)
    # request.session['cart_id']=12
    # request.session['name']='Akash Verma'
    # request.session['user'] = request.user
    # print("request.session['user'] --",request.session['user'])
    # return render(request,'carts/home.html',{})


def checkout_done_view(request):
    return render(request,"carts/checkout-done.html",context={})



























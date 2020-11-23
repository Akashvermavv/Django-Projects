from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
from django.utils.http import  is_safe_url
from django.conf import settings
from .models import BillingProfile,Card


import  stripe
# stripe.api_key="sk_test_51HTjAFHGcIEXy6MZxvpNEUHviHVMMzR3o3MDrfQTQBEfMxu8dUkd6rXjqEgh7MaVgAFtM2iu2Dx8WFOl2qRYHOvk009J3t2eCu"
# STRIPE_PUB_KEY = "pk_test_51HTjAFHGcIEXy6MZq7tC7yVKQPoTfEgr4wStVSfyYo7MvppcEPyHCRNlPZevZoFjJUJGdbfhjY96Hx0HOJrhNqDA00OAjJoE5H"

STRIPE_SECRET_KEY  = getattr(settings,"STRIPE_SECRET_KEY","sk_test_51HTjAFHGcIEXy6MZxvpNEUHviHVMMzR3o3MDrfQTQBEfMxu8dUkd6rXjqEgh7MaVgAFtM2iu2Dx8WFOl2qRYHOvk009J3t2eCu")
STRIPE_PUB_KEY  = getattr(settings,"STRIPE_PUB_KEY", "pk_test_51HTjAFHGcIEXy6MZq7tC7yVKQPoTfEgr4wStVSfyYo7MvppcEPyHCRNlPZevZoFjJUJGdbfhjY96Hx0HOJrhNqDA00OAjJoE5H")
stripe.api_key = STRIPE_SECRET_KEY


def payment_method_view(request):
    # if request.method =="POST":
    #     print('post data --',request.POST)

    # if request.user.is_authenticated:
    #     billing_profile = request.user.billingprofile
    #     my_customer_id = billing_profile.customer_id

    billing_profile,billing_profile_created = BillingProfile.objects.new_or_get(request)
    if not billing_profile:
        return redirect("/cart")

    next_url=None
    next_ = request.GET.get('next')
    if (is_safe_url(next_,request.get_host())):
        next_url = next_
    return render(request,'billing/payment-method.html',{"publish_key":STRIPE_PUB_KEY,"next_url":next_url })


def payment_method_createview(request):
    if request.method == "POST"  and request.is_ajax():
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)

        if not billing_profile:
            return HttpResponse({"message":"Cannot find this user"},status_code=401)
        print('post data in payment_method_createview', request.POST)
        token = request.POST.get("token")
        if token is not None:
            # customer = stripe.Customer.retrieve(billing_profile.customer_id)
            # card_response = customer.sources.create(source=token)
            # card_response = stripe.Customer.create_source(billing_profile.customer_id,source=token)
            new_card_obj = Card.objects.add_new(billing_profile,token)
            print('new card obj -- --',new_card_obj)

        return JsonResponse({"message":"Success! Your card was added."})
    return HttpResponse("error",status=401)








from django.db import models
from django.db.models.signals import post_save ,pre_save
from django.conf import settings
from django.urls import reverse
from accounts.models import GuestEmail
import  stripe
User = settings.AUTH_USER_MODEL
STRIPE_SECRET_KEY  = getattr(settings,"STRIPE_SECRET_KEY","sk_test_51HTjAFHGcIEXy6MZxvpNEUHviHVMMzR3o3MDrfQTQBEfMxu8dUkd6rXjqEgh7MaVgAFtM2iu2Dx8WFOl2qRYHOvk009J3t2eCu")
STRIPE_PUB_KEY  = getattr(settings,"STRIPE_PUB_KEY", "pk_test_51HTjAFHGcIEXy6MZq7tC7yVKQPoTfEgr4wStVSfyYo7MvppcEPyHCRNlPZevZoFjJUJGdbfhjY96Hx0HOJrhNqDA00OAjJoE5H")
stripe.api_key = STRIPE_SECRET_KEY
# abc@teamcfe.com   --->> 100000 billing profiles
# user abc@teamcfe.com  -- 1 billing profile



class BillingProfileManager(models.Manager):
    def new_or_get(self,request):
        print('in new or get billing profile method --',request.session)
        user = request.user
        guest_email_id = request.session.get('guest_email_id')
        created = False
        obj = None

        if user.is_authenticated:
            'logged in user checkout; remember payment stuff'
            # obj, created = BillingProfile.objects.get_or_create(
            obj, created = self.model.objects.get_or_create(
                user=user,
                email=user.email
            )
        elif (guest_email_id is not None):
            'guest user checkout; auto reloads payment stuff'
            # guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
            guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
            obj, created = self.model.objects.get_or_create(
                email=guest_email_obj.email
            )
        else:
            pass
        return obj,created


class BillingProfile(models.Model):
    # user         = models.ForeignKey(User,unique=True,null=True,blank=True,on_delete=models.CASCADE)
    user         = models.OneToOneField(User,null=True,blank=True,on_delete=models.CASCADE)
    email        = models.EmailField()
    active       = models.BooleanField(default=True)
    update       = models.DateTimeField(auto_now=True)
    timestamp    = models.DateTimeField(auto_now_add=True)
    customer_id  = models.CharField(max_length=120,null=True,blank=True)
    # customer id in Stripe or Braintree

    def __str__(self):
        return self.email

    objects = BillingProfileManager()

    def charge(self,order_obj,card=None):
        return Charge.objects.do(self,order_obj,card)

    def get_cards(self):
        return self.card_set.all() # Card.objects.filter(billing_profile=self,active=True)

    def get_payment_method_url(self):
        return reverse('billing-payment-method')

    @property
    def has_card(self):
        card_qs = self.get_cards()
        return card_qs.exists()

    @property
    def default_card(self):
        default_cards = self.get_cards().filter(active=True,default=True)
        if default_cards.exists():
            return default_cards.first()
        return None

    def set_cards_inactive(self):
        cards_qs = self.get_cards()
        cards_qs.update(active=False)
        return cards_qs.filter(active=True).count()



def billing_profile_created_receiver(sender,instance,*args,**kwargs):
    if not instance.customer_id and instance.email:

        customer = stripe.Customer.create(email = instance.email)
        print('ACTUAL API REQUEST Send to stripe/braintree',customer)
        instance.customer_id =customer.id

pre_save.connect(billing_profile_created_receiver,sender=BillingProfile)

def user_created_receiver(sender,instance,created,*args,**kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance,email=instance.email)

post_save.connect(user_created_receiver,sender=User)

#
# card response -- {
#   "address_city": null,
#   "address_country": null,
#   "address_line1": null,
#   "address_line1_check": null,
#   "address_line2": null,
#   "address_state": null,
#   "address_zip": "42424",
#   "address_zip_check": "pass",
#   "brand": "Visa",
#   "country": "US",
#   "customer": "cus_I3rJnuAJKcwuqm",
#   "cvc_check": "pass",
#   "dynamic_last4": null,
#   "exp_month": 4,
#   "exp_year": 2024,
#   "fingerprint": "eUTR0TQuFFOqF3vB",
#   "funding": "credit",
#   "id": "card_1HUbA0HGcIEXy6MZc25cdyya",
#   "last4": "4242",
#   "metadata": {},
#   "name": null,
#   "object": "card",
#   "tokenization_method": null
# }


class CardManager(models.Manager):

    def all(self,*args,**kwargs): # ModelKlass.objects.all()   ---> ModelKlass.objects.filter(active=True)
        return self.get_queryset().filter(active=True)

    def add_new(self,billing_profile,token):#stripe_card_response):
        # if str(stripe_card_response.object) =="card":
        if token:
            stripe_card_response = stripe.Customer.create_source(billing_profile.customer_id, source=token)
            new_card =  self.model(
                billing_profile = billing_profile,
                stripe_id       = stripe_card_response.id,
                brand           = stripe_card_response.brand,
                country         = stripe_card_response.country,
                exp_month       = stripe_card_response.exp_month,
                exp_year        = stripe_card_response.exp_year,
                last4           = stripe_card_response.last4

            )
            new_card.save()
            return new_card
        return None




class Card(models.Model):
    billing_profile     = models.ForeignKey(BillingProfile,on_delete=models.CASCADE)
    stripe_id           = models.CharField(max_length=120)
    brand               = models.CharField(max_length=120,null=True,blank=True)
    country             = models.CharField(max_length=20,null=True,blank=True)
    exp_month           = models.IntegerField(null=True,blank=True)
    exp_year            = models.IntegerField(null=True,blank=True)
    last4               = models.CharField(max_length=4,null=True,blank=True)
    default             = models.BooleanField(default=True)
    active              = models.BooleanField(default=True)
    timestamp           = models.DateTimeField(auto_now_add=True)

    objects = CardManager()

    def __str__(self):
        return f"{self.brand} {self.last4}"

def  new_card_post_save_receiver(sender,instance,created,*args,**kwargs):
    if instance.default:
        billing_profile = instance.billing_profile
        qs = Card.objects.filter(billing_profile=billing_profile).exclude(pk=instance.pk)
        qs.update(default=False)

post_save.connect(new_card_post_save_receiver,sender=Card)



class ChargeManager(models.Manager):
    def do(self,billing_profile,order_obj,card=None):  #Charge.objects.do()
        card_obj = card
        if card_obj is None:
            cards = billing_profile.card_set.filter(default=True)   # card_obj.billing_profile
            if cards.exists():
                card_obj = cards.first()
        if card_obj is None:
            return False,"No cards available"
        print('cart_obj --',card_obj)
        print('card_obj.stripe_id ------>', card_obj.stripe_id)
        print('############  no error occur $$$$$$$$$$$$$$$$')
        # print('billing_profile.customer_id ------>', billing_profile.customer_id)
        # print('card_obj.stripe_id ------>', card_obj.stripe_id)
        # print('order_obj.order_id ------>', order_obj.order_id)
        # print('int(order_obj.total ) ------>', int(order_obj.total ))


        c = stripe.Charge.create(
            amount= int(order_obj.total ),   # 39.19  --> 3919
            currency ="inr",
            customer = billing_profile.customer_id,
            source = card_obj.stripe_id,
            metadata={"order_id":order_obj.order_id},
        )
        #
        # c = stripe.Charge.create(
        #     amount=1,
        #     currency="inr",
        #     customer='cus_I4yl8rIWt9qz5T',
        #     source='card_1HUrJkHGcIEXy6MZvtdax9LW',
        #     metadata={"order_id":'csifa2tzjn' },
        # )
        print('############  no error occur 1111111111111')

        new_charge_obj = self.model(
            billing_profile = billing_profile,
            stripe_id = c.id,
            paid = c.paid,
            refunded = c.refunded,
            outcome = c.outcome,
            outcome_type = c.outcome['type'],
            seller_message = c.outcome.get('seller_message'),
            risk_level = c.outcome.get('risk_level'),
        )
        print('############  no error occu222222222222222222222')
        new_charge_obj.save()
        return new_charge_obj.paid,"message for seller from stripe"#new_charge_obj.seller_message



class Charge(models.Model):
    billing_profile     = models.ForeignKey(BillingProfile,on_delete=models.CASCADE)
    stripe_id           = models.CharField(max_length=120)
    paid                = models.BooleanField(default=False)
    refunded            = models.BooleanField(default=False)
    outcome             = models.TextField(null=True,blank=True)
    outcome_type        =  models.CharField(max_length=120,null=True,blank=True)
    seller_message      = models.CharField(max_length=120,null=True,blank=True)
    risk_level          = models.CharField(max_length=120,null=True,blank=True)

    objects = ChargeManager()



















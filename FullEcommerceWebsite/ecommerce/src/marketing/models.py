from django.db import models
from django.conf import settings
from django.db.models.signals import post_save,pre_save
from .utils import MailChimp


class MarketingPreference(models.Model):
    user                = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    subscribed          = models.BooleanField(default=True)
    mailchimp_subscribed = models.NullBooleanField(default=True)
    mailchimp_msg       = models.TextField(null=True,blank=True)
    timestamp           = models.DateTimeField(auto_now_add=True)
    updated              = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email


def marketing_pref_create_receiver(sender,instance,created,*args,**kwargs):
    if created:
        # print("add  user to mailchimp")
        print('instance.user.email -->',instance.user.email)
        status_code,response_data = MailChimp().subscribe(instance.user.email)
        print('status code ----',status_code,response_data)

post_save.connect(marketing_pref_create_receiver,sender=MarketingPreference)

def marketing_pref_update_receiver(sender,instance,*args,**kwargs):
    if instance.subscribed != instance.mailchimp_subscribed:
        if instance.subscribed:
            # subscribing user
            status_code,response_data = MailChimp().subscribe(instance.user.email)
        else:
            # unsubscribing user
            status_code, response_data = MailChimp().unsubscribe(instance.user.email)

        if response_data['status'] =='subscribed':
            instance.subscribed             = True
            instance.mailchimp_subscribed   = True
            instance.mailchimp_msg          = response_data
        else:
            instance.subscribed             = False
            instance.mailchimp_subscribed   = False
            instance.mailchimp_msg          = response_data

pre_save.connect(marketing_pref_update_receiver,sender=MarketingPreference)


def make_marketing_pre_receiver(sender,instance,created,*args,**kwargs):
    '''
    USer model
    '''

    if created:
        MarketingPreference.objects.get_or_create(user=instance)

post_save.connect(make_marketing_pre_receiver,sender=settings.AUTH_USER_MODEL)





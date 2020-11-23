from django.shortcuts import render,HttpResponse,redirect
from django.views.generic import UpdateView,View
from django.contrib.messages.views import SuccessMessageMixin
from django.conf import settings
from .forms import MarketingPreferenceForm
from .models import MarketingPreference
from .utils import MailChimp
from .mixins import CsrfExemptMixin



MAILCHIMP_EMAIL_LIST_ID = getattr(settings,"MAILCHIMP_EMAIL_LIST_ID",None)

class MarketingPreferenceUpdateView(SuccessMessageMixin,UpdateView):
    form_class = MarketingPreferenceForm
    template_name = 'base/forms.html'
    success_url = '/settings/email/'
    success_message = 'Your email preferences have been updated. Thank you.'

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_authenticated:
            # return HttpResponse("Not allowed",status=400)
            return redirect("/login/?next=/settings/email/")
        return super(MarketingPreferenceUpdateView,self).dispatch(*args,**kwargs)


    def get_context_data(self, *args,**kwargs):
        context = super(MarketingPreferenceUpdateView,self).get_context_data(*args,**kwargs)
        context['title'] = 'Update Email Preferences'
        return context

    def get_object(self, queryset=None):
        user = self.request.user
        obj,created = MarketingPreference.objects.get_or_create(user=user)  # get_absolute_url
        return obj



'''

{
  "method": "POST",
  "path": "/",
  "query": {},
  "headers": {
    "x-forwarded-for": "35.243.128.190",
    "x-forwarded-proto": "https",
    "x-forwarded-port": "443",
    "host": "0a70b7da28dc29020ead29c318c1c803.m.pipedream.net",
    "x-amzn-trace-id": "Root=1-5f6e466e-b92becf3cb08f3c35ab070fd",
    "content-length": "414",
    "content-type": "application/x-www-form-urlencoded",
    "user-agent": "MailChimp"
  },
  "bodyRaw": "type=subscribe&fired_at=2020-09-25+19%3A35%3A10&data%5Bid%5D=445730cddb&data%5Bemail%5D=akash%40gmail.com&data%5Bemail_type%5D=html&data%5Bip_opt%5D=47.31.155.207&data%5Bweb_id%5D=383619817&data%5Bmerges%5D%5BEMAIL%5D=akash%40gmail.com&data%5Bmerges%5D%5BFNAME%5D=&data%5Bmerges%5D%5BLNAME%5D=&data%5Bmerges%5D%5BADDRESS%5D=&data%5Bmerges%5D%5BPHONE%5D=&data%5Bmerges%5D%5BBIRTHDAY%5D=&data%5Blist_id%5D=a585924ae3",
  "body": {
    "type": "subscribe",
    "fired_at": "2020-09-25 19:35:10",
    "data[id]": "445730cddb",
    "data[email]": "akash@gmail.com",
    "data[email_type]": "html",
    "data[ip_opt]": "47.31.155.207",
    "data[web_id]": "383619817",
    "data[merges][EMAIL]": "akash@gmail.com",
    "data[merges][FNAME]": "",
    "data[merges][LNAME]": "",
    "data[merges][ADDRESS]": "",
    "data[merges][PHONE]": "",
    "data[merges][BIRTHDAY]": "",
    "data[list_id]": "a585924ae3"
  }
}


'''

# class based views

class MailchimpWebhookView(CsrfExemptMixin,View): # if HTTP GET -- def get()
    # def get(self,request,*args,**kwargs):
    #     return HttpResponse("Thank you", status=200)

    def post(self,*args,**kwargs):
        request = self.request
        data = request.POST
        list_id = data.get('data[list_id]')
        if (str(list_id) == str(MAILCHIMP_EMAIL_LIST_ID)):
            hook_type = data.get("type")
            email = data.get('data[email]')
            response_status, response = MailChimp().check_subscription_status(email)
            sub_status = response['status']
            is_subbed = None
            mailchimp_subbed = None

            if sub_status == 'subscribed':
                is_subbed, mailchimp_subbed = (True, True)

            elif sub_status == 'unsubscribed':
                is_subbed, mailchimp_subbed = (False, False)

            if is_subbed is not None and mailchimp_subbed is not None:
                qs = MarketingPreference.objects.filter(user__email__iexact=email)
                if qs.exists():
                    qs.update(
                        subscribed=is_subbed,
                        mailchimp_subscribed=mailchimp_subbed,
                        mailchimp_msg=str(data)
                    )
        return HttpResponse("Thank you", status=200)


#### function based views

def mailchimp_webhook_view(request):
    data = request.POST
    list_id = data.get('data[list_id]')
    if(str(list_id) == str(MAILCHIMP_EMAIL_LIST_ID)):
        hook_type = data.get("type")
        email = data.get('data[email]')
        response_status,response = MailChimp().check_subscription_status(email)
        sub_status = response['status']
        is_subbed = None
        mailchimp_subbed = None

        if sub_status =='subscribed':
            is_subbed,mailchimp_subbed = (True,True)

        elif sub_status =='unsubscribed':
            is_subbed, mailchimp_subbed = (False, False)

        if is_subbed is not None and mailchimp_subbed is not None:
            qs = MarketingPreference.objects.filter(user__email__iexact=email)
            if qs.exists():
                qs.update(
                    subscribed = is_subbed,
                    mailchimp_subscribed = mailchimp_subbed,
                    mailchimp_msg = str(data)
                )
    return HttpResponse("Thank you",status=200)





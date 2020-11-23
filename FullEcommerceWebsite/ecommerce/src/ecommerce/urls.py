from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path,re_path,include
from .views import (
                    home_page,
                    about_page,
                    contact_page,
            category_wise

                    )
from core import views as core_views
from accounts.views import (
                    # login_page,
                    RegisterView,
                    LoginView,
                    # register_page,
                    # guest_register_view
                    GuestRegisterView
                            )

from django.views.generic import  TemplateView,RedirectView
from carts.views import cart_home,cart_detail_api_view
from addresses.views import checkout_address_create_view,checkout_address_reuse_view
from billing.views import payment_method_view,payment_method_createview
from marketing.views import MarketingPreferenceUpdateView,MailchimpWebhookView
from orders.views import LibraryView
from analytics.views import SalesView,SalesAjaxView

# from django.contrib.auth import views as auth_views

urlpatterns = [
    # re_path(r'^$', home_page,name='home'),
    re_path(r'^$', RedirectView.as_view(url='/products'),name='home'),
    # re_path(r'^oauth/', include(('social_django.urls','social'), namespace='social')),
    re_path(r'^about/$', about_page,name='about'),
    # re_path(r'^accounts/login/$',RedirectView.as_view(url='/login/klkl')),
    re_path(r'^accounts/$',RedirectView.as_view(url='/account')),
    re_path(r'^account/', include("accounts.urls")),
    re_path(r'^accounts/', include("accounts.passwords.urls")),
    re_path(r'^products/', include("products.urls")),
    re_path(r'^library/$', LibraryView.as_view(),name='library'),
    re_path(r'^orders/', include("orders.urls")),
    re_path(r'^search/', include("search.urls")),
    re_path(r'^contact/$', contact_page,name='contact'),
    re_path(r'^analytics/sales/$', SalesView.as_view(),name='sales-analytics'),
    re_path(r'^analytics/sales/data/$', SalesAjaxView.as_view(),name='sales-analytics-data'),
    re_path(r'^login/$', LoginView.as_view(),name='login'),
    re_path(r'^checkout/address/create/$', checkout_address_create_view,name='checkout_address_create'),
    re_path(r'^checkout/address/reuse/$', checkout_address_reuse_view,name='checkout_address_reuse'),
    re_path(r'^register/guest/$', GuestRegisterView.as_view(),name='guest_register'),
    re_path(r'^logout/$', LogoutView.as_view(),name='logout'),
    re_path(r'^api/cart/$', cart_detail_api_view,name='api-cart'),
    # re_path(r'^cart/', cart_home,name='cart'),
    re_path(r'^cart/', include('carts.urls')),
    re_path(r'^billing/payment-method/$', payment_method_view,name='billing-payment-method'),
    re_path(r'^billing/payment-method/create/$', payment_method_createview,name='billing-payment-method-endpoint'),

    re_path(r'^register/$', RegisterView.as_view(),name='register'),
    re_path(r'^bootstrap/$', TemplateView.as_view(template_name='bootstrap/example.html')),
    re_path(r'^settings/$',RedirectView.as_view(url='/account')),

    re_path(r'^settings/email/$', MarketingPreferenceUpdateView.as_view(),name='marketing-pref'),
    re_path(r'^webhooks/mailchimp/$', MailchimpWebhookView.as_view(),name='webhooks-mailchimp'),
    # re_path(r'^settings_auth/$', setting_auth, name='settings'),
    re_path(r'^oauth/', include('social_django.urls', namespace='social')),
    re_path(r'^settings/$', core_views.settings, name='settings'),
    path('admin/', admin.site.urls),
    re_path(r'^get_category_wise_/$', category_wise,name='product_category_wise'),



    # re_path(r'^products/$', ProductListView.as_view(),),
    # re_path(r'^featured/$', ProductFeaturedListView.as_view(),),
    # re_path(r'^products-fbv/$', product_list_view,),
    # # re_path(r'^products/(?P<pk>\d+)/$', ProductDetailView.as_view(),),
    # re_path(r'^products/(?P<slug>[\w-]+)/$', ProductDetailSlugView.as_view(),),
    # re_path(r'^featured/(?P<pk>\d+)/$', ProductFeaturedDetailView.as_view(),),
    # re_path(r'^products-fbv/(?P<pk>\d+)/$', product_detail_view,),
]



if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
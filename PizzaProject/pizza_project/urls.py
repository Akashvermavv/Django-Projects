from django.contrib import admin
from django.urls import path,re_path,include
from accounts.views import (
                            login_view,
                            logout_view,
                            register_view,
                            contact_view
                            )
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^api/pizza/', include('pizza.api.urls')),
    path('', include('pizza.urls')),
    re_path(r'^contact/$', contact_view, name='contact_view'),
    re_path(r'^login/$', login_view, name='login'),
    re_path(r'^logout/$', logout_view, name='logout'),
    re_path(r'^register/$', register_view, name='register'),
]


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
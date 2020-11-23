from django.contrib import admin
from django.urls import path,include,re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import  TemplateView,RedirectView
from accounts.views import (
                            login_view,
                            logout_view,
                            register_view,
                            contact_view
                            )
from rest_framework_jwt.views import obtain_jwt_token



urlpatterns = [

re_path(r'^$', RedirectView.as_view(url='/posts'),name='home'),
    path('admin/', admin.site.urls),

    # path('', include('posts.urls')),
    re_path(r'^contact/$',contact_view,name='contact_view'),
    re_path(r'^login/$',login_view,name='login'),
    re_path(r'^logout/$',logout_view,name='logout'),
    path('accounts/', include('allauth.urls')),
    re_path(r'^register/$',register_view,name='register'),
    path('comments/', include('comments.urls')),
    path('posts/', include('posts.urls')),
    re_path(r'^api/auth/token/', obtain_jwt_token),
    re_path(r'^api/users/',include(('accounts.api.urls',"users-api"),namespace="users-api")),
    re_path(r'^api/comments/',include(('comments.api.urls',"comments-api"),namespace="comments-api")),
    re_path(r'^api/posts/',include(('posts.api.urls',"posts-api"),namespace="posts-api")),
    path('oauth/', include('social_django.urls', namespace='social')),  # <-- here

]



if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

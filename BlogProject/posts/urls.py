from django.contrib import admin
from django.urls import path,include,re_path
from .views import (post_list,
                    post_create,
                    post_delete,
                    post_detail,
                    post_update
                    )

app_name='posts'

urlpatterns = [
    re_path(r'^$', post_list,name='posts_list_view'),
    re_path(r'^create/$', post_create,name='posts_create_view'),
    re_path(r'^(?P<slug>[\w-]+)/$', post_detail,name='detail'),
    re_path(r'^(?P<slug>[\w-]+)/edit/$', post_update,name='posts_update_view'),
    re_path(r'^(?P<id>\d+)/delete/$', post_delete,name='posts_delete_view'),
]

from django.shortcuts import render,get_object_or_404
from . models import Blog

# Create your views here.

def allblogs(request):
    blogs=Blog.objects.all
    return render(request,'blog/allblogs.html',{'blogs':blogs})

def detail(request,pk):
    print('In Detail')
    blogdetail=get_object_or_404(Blog, pk=pk)
    return render(request,'blog/detail.html',{'blogdetail':blogdetail})
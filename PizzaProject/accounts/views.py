from django.shortcuts import render,redirect
from django.contrib.auth import (
                        authenticate,
                        get_user_model,
                        login,
                        logout
                    )
from .forms import (
                    UserLoginForm,
                    UserRegisterForm,
                    ContactForm
            )

def login_view(request):
    next = request.GET.get('next')
    title="Login"
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user =authenticate(request,username=username,password=password)
        login(request,user)
        if next:
            return redirect(next)
        return redirect('/')


    return render(request,"accounts/form.html",{'form':form,"title":title})

def register_view(request):
    # print('user is auth or not --',request.user.is_authenticated)
    next = request.GET.get('next')
    form =  UserRegisterForm(request.POST or None)
    title="Register"

    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get("password")
        user.set_password(password)
        user.save()
        new_user = authenticate(username=user.username,password=password)
        login(request,new_user)
        if next:
            return redirect(next)
        return redirect("/")

    context =  {
        "form":form,
        "title":title
    }
    return render(request,"accounts/register.html",context=context)

def logout_view(request):
    logout(request)
    return redirect('/')
    # return render(request,"accounts/form.html",{})

def contact_view(request):
    form = ContactForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("/")
        # name = form.cleaned_data.get("name")
        # email = form.cleaned_data.get("email")
        # phone_number = form.cleaned_data.get("phone_number")
        #
    return render(request,'accounts/contact.html',{'form':form})









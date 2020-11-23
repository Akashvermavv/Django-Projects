from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate,logout,get_user_model
from django.utils.http import is_safe_url
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView,FormView,DetailView,View,UpdateView
from django.views.generic.edit import FormMixin
from django.urls import reverse
from django.contrib import  messages
from django.utils.safestring import mark_safe
from ecommerce.mixins import NextUrlMixin,RequestFormAttachMixin
from .forms import LoginForm,RegisterForm,GuestForm,ReactivateEmailForm,UserDetailChangeForm
from .models import GuestEmail,EmailActivation
from social_django.models import UserSocialAuth
from .signals import user_logged_in


# @login_required  # /accounts/login/?next=/some/path
# def account_home_view(request):
#     return render(request,"accounts/home.html",{})

# class LoginRequiredMixin(object):
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super(LoginRequiredMixin,self).dispatch(request,*args, **kwargs)

# LoginRequiredMixin,


class AccountHomeView(LoginRequiredMixin,DetailView):
    template_name = 'accounts/home.html'
    def get_object(self, queryset=None):
        return self.request.user

    # @method_decorator(login_required)
    # def dispatch(self,  *args, **kwargs):
    #     return super(AccountHomeView,self).dispatch(*args, **kwargs)

class AccountEmailActivateView(FormMixin,View):
    success_url = '/login/'
    form_class = ReactivateEmailForm
    def get(self,request,key=None,*args,**kwargs):
        self.key = key
        if key is not None:
            qs = EmailActivation.objects.filter(key__iexact=key)
            confirm_qs = qs.confirmable()
            if confirm_qs.count()==1:
                obj = confirm_qs.first()
                obj.activate()
                messages.success(request,"Your email has been confirmed. Please login. ")
                return redirect("login")
            else:
                activated_qs = qs.filter(activated= True)
                if activated_qs.exists():
                    reset_link = reverse("password_reset")
                    msg ="""Your email has already been confirmed Do you need to <a href="{link}"> reset your password </a>?""".format(
                        link = reset_link
                    )
                    messages.success(request,mark_safe(msg))
                    return redirect("login")

            # if activated
            # return redirect
            # if already activated
            # return redirect
            # if error
        context ={'form':self.get_form(),'key':key}
        return render(request,'registration/activation-error.html',context)

    def post(self,request,*args,**kwargs):
        print('post data --',request.POST)
        # create form to receive an email
        form = self.get_form()
        print('in post form  is valid --',form.is_valid())
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self,form):
        msg="""  Activation link sent, please check your email."""
        request = self.request
        messages.success(request,msg)
        email = form.cleaned_data.get("email")
        obj = EmailActivation.objects.email_exists(email).first()
        user = obj.user
        new_activation = EmailActivation.objects.create(user=user,email=email)
        new_activation.send_activation()
        return super(AccountEmailActivateView,self).form_valid(form)

    def form_invalid(self,form):
        context = {'form':form,"key":self.key}
        return render(self.request,'registration/activation-error.html',context)



def guest_register_view(request):
    form = GuestForm(request.POST or None)

    context ={
        "form":form
    }
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None

    if form.is_valid():
        email = form.cleaned_data.get("email")
        print('email in guest_register_view -->',email)
        new_guest_email = GuestEmail.objects.create(email=email)
        request.session['guest_email_id'] = new_guest_email.id

        if is_safe_url(redirect_path,request.get_host()):
            return redirect(redirect_path)
        else:
            return redirect("/register/")
    return redirect("/register/")


class GuestRegisterView(NextUrlMixin,RequestFormAttachMixin,FormView):
    form_class = GuestForm
    default_next = '/register/'

    def get_success_url(self):
        return self.get_next_url()

    def form_invalid(self, form):
        return redirect(self.default_next)

    def form_valid(self, form):
        request = self.request
        email = form.cleaned_data.get('email')
        new_guest_email = GuestEmail.objects.create(email=email)
        request.session['guest_email_id'] = new_guest_email.id
        return redirect(self.get_next_url())



# def login_view(request):
#     form = LoginForm(request=request)




class LoginView(NextUrlMixin,RequestFormAttachMixin,FormView):
    form_class = LoginForm
    success_url = '/'
    template_name = 'accounts/login.html'
    default_next ='/'

    # def get_form_kwargs(self):
    #     kwargs = super(LoginView, self).get_form_kwargs()
    #     print('kwargs ---',kwargs)
    #     kwargs['request'] = self.request
    #     return kwargs

    # def get_next_url(self):
    #     request = self.request
    #     next_ = request.GET.get('next')
    #     next_post = request.POST.get('next')
    #     redirect_path = next_ or next_post or None
    #     if is_safe_url(redirect_path, request.get_host()):
    #         return redirect_path
    #     return "/"


    def form_valid(self, form):
        next_path = self.get_next_url()
        return redirect(next_path)


        # email = form.cleaned_data.get("email")
        # password = form.cleaned_data.get("password")
        # user = authenticate(request, username=email, password=password)
        # print('user is auth or not --', request.user.is_authenticated)
        # user = form.user
        # print('user -->', user, type(user))
        # # if user is not None:
        # #     # print('user is auth or not --', request.user.is_authenticated)
        # #     if not user.is_active:
        # #         messages.error(request,"This user is inactive")
        # #         return super(LoginView,self).form_invalid(form)
        # #     login(request, user)
        # if user.is_authenticated:
        #     # user_logged_in.send(user.__class__,instance=user,request=request)
        #     # try:
        #     #     del request.session['guest_email_id']
        #     # except:
        #     #     pass
        #     # redirect to a success page
        #     next_path = self.get_next_url()
        #     return redirect(next_path)
        # return super(LoginView,self).form_invalid(form)


def login_page(request):
    form = LoginForm(request.POST or None)
    print('user is auth or not --',request.user.is_authenticated)
    context ={
        "form":form
    }
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None

    if form.is_valid():
        print('loginform data --',form.cleaned_data)

        username = form.cleaned_data.get("username")
        password  = form.cleaned_data.get("password")
        user = authenticate(request,username=username,password=password)
        # print('user is auth or not --', request.user.is_authenticated)
        print('user -->',user,type(user))
        if user is not None:
            # print('user is auth or not --', request.user.is_authenticated)
            login(request,user)
            try:
                del request.session['guest_email_id']
            except:
                pass
            # redirect to a success page
            if is_safe_url(redirect_path,request.get_host()):
                return redirect(redirect_path)
            else:
                return redirect("/")
        else:
            # return an "invalid login error message.
            print("Error")
        # context['form'] = LoginForm()
    return render(request,"accounts/login.html",context)


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/login/'


class UserDetailUpdateView(LoginRequiredMixin,UpdateView):
    form_class = UserDetailChangeForm
    template_name = 'accounts/detail-update-view.html'

    def get_object(self, queryset=None):
        print('queryset in UserDetailUpdateView ',queryset)
        return self.request.user

    def get_context_data(self,**kwargs):
        context = super(UserDetailUpdateView, self).get_context_data(**kwargs)
        context['title'] = 'Change Your Account Details'
        return context

    def get_success_url(self):
        return reverse("account:home")


# User = get_user_model()
# def register_page(request):
#     form =RegisterForm(request.POST or None)
#     # print('dir(form)--',dir(form))
#     context ={
#         'form':form
#     }
#     print('user is auth or not --',request.user.is_authenticated)
#
#     if form.is_valid():
#         form.save()
#         # print('loginform data --',form.cleaned_data)
#         # username = form.cleaned_data.get("username")
#         # email = form.cleaned_data.get("email")
#         # password = form.cleaned_data.get("password")
#         # new_user = User.objects.create_user(username=username,email=email,password=password)
#         # print('new user --',new_user)
#
#     return render(request,"accounts/register.html",context)




@login_required
def settings(request):
    user = request.user

    try:
        github_login = user.social_auth.get(provider='github')
    except UserSocialAuth.DoesNotExist:
        github_login = None
    try:
        twitter_login = user.social_auth.get(provider='twitter')
    except UserSocialAuth.DoesNotExist:
        twitter_login = None
    try:
        facebook_login = user.social_auth.get(provider='facebook')
    except UserSocialAuth.DoesNotExist:
        facebook_login = None

    can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

    return render(request, 'core/settings.html', {
        'github_login': github_login,
        'twitter_login': twitter_login,
        'facebook_login': facebook_login,
        'can_disconnect': can_disconnect
    })

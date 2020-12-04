from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from .models import (
                    Pizza,
                    Toppings,
                    Sizes
                    )

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import PizzaForm
import json

def home_page(request):
    print('no error ')
    objs = Pizza.objects.all()
    print('exists --',objs.exists())
    if objs.exists():
        context ={'objs':objs}
    else:
        context={'objs':[]}

    return render(request,'pizza/index.html',context)

@csrf_exempt
def add_pizza(request):
    if(request.method=='POST' and request.is_ajax()):
        # post_data = json.loads(request.body())
        new_size = str(request.POST.get('sizes')).strip().title()
        print('post data @@2',)
        Sizes.objects.create(pizza_size=new_size)
        objs = Sizes.objects.all()
        all_size_list=[obj.pizza_size for obj in objs]

        data={'size_data':all_size_list}
        print('ajax request data --',data)

        return JsonResponse(data,safe=False)
    elif(request.method=='POST'):
        print('post data in add_pizza --',request.POST)
        data = request.POST
        pizza_type = str(data.get('selectedType'))
        pizza_size = data.getlist('selectedSize')
        pizza_topping = data.getlist('selectedToppings')
        print('pizza_type',pizza_type)
        print('pizza_size',pizza_size)
        print('pizza_topping',pizza_topping)
        size_obj = Sizes.objects.create(pizza_size=pizza_size[0])
        list_toppings_obj = []
        for e in pizza_topping:
            topping_obj = Toppings.objects.create(topping_name=e)
            list_toppings_obj.append(topping_obj)



        obj = Pizza.objects.create(pizza_type=pizza_type,size_type=size_obj,)
        for e in list_toppings_obj:
            obj.topping_type.add(e)
        messages.success(request, 'Pizza item Created successfully')
        return redirect('pizza:home')





    context ={
        'toppings':Toppings.objects.all(),
        'sizes':Sizes.objects.all(),
        'pizzas':Pizza.objects.all(),
    }
    return render(request,'pizza/add_pizza.html',context)


@csrf_exempt
def add_topping(request):
    if(request.method=='POST' and request.is_ajax()):
        # post_data = json.loads(request.body())
        new_topping = str(request.POST.get('toppings')).strip().title()
        print('post data @@2',)
        Toppings.objects.create(topping_name=new_topping)
        objs = Toppings.objects.all()
        all_topping_list=[obj.topping_name for obj in objs]

        data={'topping_data':all_topping_list}
        print('ajax request data --',data)

        return JsonResponse(data,safe=False)

    context ={
        'toppings':Toppings.objects.all(),
        'sizes':Sizes.objects.all(),
        'pizzas':Pizza.objects.all(),
    }
    return render(request,'pizza/add_pizza.html',context)


def delete_pizza(request,pizza_id=None):
    obj = get_object_or_404(Pizza,id=pizza_id)
    obj.delete()
    messages.success(request,'Pizza item deleted successfully')
    return redirect('pizza:home')
    # objs = Pizza.objects.all()
    # context = {'objs': objs}
    # return render(request,'pizza/index.html',context)


def edit_pizza(request,id=None):
    obj = get_object_or_404(Pizza, id=id)
    pizza_type = obj.pizza_type
    size_type = obj.size_type
    topping_types = obj.topping_type.all()
    form = PizzaForm(request.POST or None, instance=obj, )
    print('pizza type --', pizza_type)
    print('size_type type --', size_type)
    print('topping_types type --', topping_types)

    if form.is_valid():
        print('edit form is valid')
        # instance = form.save(commit=False)
        form.save()
        # instance.save()
        # success message
        messages.success(request, "Item Saved")
        return redirect('pizza:home')
        # return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        # "title": instance.title,
        "instance": obj,
        "form": form,
    }
    # return render(request, "posts/post_form.html", context)
    return render(request, 'pizza/edit.html',context )



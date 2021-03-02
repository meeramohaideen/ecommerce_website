from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import json
import datetime

from .models import *
from .utils import cookieCart,cartData,guestOrder
from .forms import UserLoginForm

# Create your views here.

def store(request):

    print('store')
    data=cartData(request)
    cartItems=data['cartItems']

    products=Product.objects.all()
    context={'products':products,'cartItems':cartItems}
    return render(request, 'store/store.html', context)

def cart(request):

    data=cartData(request)
    cartItems=data['cartItems']
    order=data['order']
    items=data['items']


    context={'items':items,'order':order,'cartItems':cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):

    data=cartData(request)
    cartItems=data['cartItems']
    order=data['order']
    items=data['items']

    context={'items':items,'order':order,'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId= data['productId']
    action= data['action']

    print('productId:', productId)
    print('action:',action)


    customer=request.user.customer
    product=Product.objects.get(id=productId)

    order, created = Order.objects.get_or_create(customer=customer,complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order,product=product)


    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
        print(orderItem.quantity)
    elif action =='remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0 :
        orderItem.delete()


    return JsonResponse("Item was added",safe=False)



def processOrder(request):
    transaction_id=datetime.datetime.now().timestamp()
    data=json.loads(request.body)

    if request.user.is_authenticated:
        customer=request.user.customer       
        order, created = Order.objects.get_or_create(customer=customer,complete=False)

    else:
        customer,order = guestOrder(request,data)

    total=float(data['form']['total'])
    order.transaction_id=transaction_id
    
    if total == float(order.get_cart_total):
        order.complete=True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
        customer=customer,
        order=order,
        address=data['shipping']['address'],
        city=data['shipping']['city'],
        state=data['shipping']['state'],
        zip_code=data['shipping']['zipcode'],
    )


  

    print('Data:',request.body)
    return JsonResponse("Payment Complete",safe=False)


def loginPage(request):

    print ('LOGIN')
    print(request.method)
    if request.method=='POST':
        print ('POST')
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(username=username,password=password)
        print (user)

        if user:
            login(request,user)
            print("loggedin")
            return HttpResponseRedirect(reverse(store))
        else:
            print(username,password)
            user = authenticate(username='username', password='password')
            print(user)
            return HttpResponse("Login Failed")
    else:
        return render(request,'store/login.html')

@login_required()
def UserLogout(request):
    logout(request)
    print("loggedout")
    return HttpResponseRedirect(reverse('store'))

def register(request):

    registered=False
    print('reg')

    if request.method =='POST':
        userForm=UserLoginForm(data=request.POST)
        print('reg')
        # userForm2=UserRegisterForm(data=request.POST)

        if userForm.is_valid():
            #  and userForm2.is_valid():

            user=userForm.save()
            user.set_password(user.password)
            user.save()

            # profile=userForm2.save(commit=False)
            # profile.user=user

            # if 'profile_pics' in request.FILES:
            #     profile.profile_pics=request.FILES['profile_pics']
            # profile.save()
            # user = request.name.user
            print(
                'user.id=',user.id,
                'user.username=',user.username,
                'user.email=',user.email,
                'user=',user
                )
            customer, created = Customer.objects.get_or_create(user=user,name=user.username,email=user.email)
            registered=True
        else:
            print(userForm.errors)

    else:
        print('else')
        userForm = UserLoginForm()
        # userForm2 = UserRegisterForm()
        print(userForm)
    return render(request,'store/registration.html',
                    {
                     'user_Form':userForm,
                    #  'user_Form2':userForm2,
                     'registered':registered
                     }
                )



   
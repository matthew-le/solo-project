from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout

from .forms import CreateUserForm, CityForm
from .models import *
from django.http import JsonResponse
import json
import datetime
from .utils import cookieCart, cartData, guestOrder
import requests

# Create your views here.
def registerPage(request):
    data = cartData(request)
    cartItems = data['cartItems']
    if request.user.is_authenticated:
        return redirect('/')
    else:
        form = CreateUserForm()
        if request.method == "POST":
            form = CreateUserForm(request.POST)
            email = request.POST.get('email')
            if form.is_valid():
                user = form.save()
                Customer.objects.create(user=user, email=email)

                messages.success(request, 'Account was successfully created!')
                return redirect('/login')
        context = {
            'form': form,
            'cartItems': cartItems
        }
        return render(request, 'store/register.html', context)

def loginPage(request):
    data = cartData(request)
    cartItems = data['cartItems']
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == "POST":
            username = request.POST.get('username')
            password =request.POST.get('password')

            user = authenticate(request, username = username, password=password)

            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {
            'cartItems': cartItems
        }
        return render(request, 'store/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('/login')

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {
        'products': products,
        'cartItems': cartItems
    }
    return render(request, 'store/store.html', context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems
        }
    return render(request, 'store/cart.html', context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems
        }
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('action:', action)
    print('productId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else: 
        customer, order = guestOrder(request, data)
    
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()
    
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer = customer,
            order = order,
            address = data['shipping']['address'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            zipcode = data['shipping']['zipcode'],
        )
    return JsonResponse('Payment complete', safe=False)

def favorite(request, product_id):
    if request.user.is_authenticated:
        product = Product.objects.get(id=product_id)
        user = request.user.id
        product.users_who_favorited.add(user)
    return redirect('/')

def unfavorite(request, product_id):
    if request.user.is_authenticated:
        product = Product.objects.get(id=product_id)
        user = request.user.id
        product.users_who_favorited.remove(user)
    return redirect('/')

def like(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    user = request.user.id
    comment.users_who_liked.add(user)
    return redirect('/blog')

def unlike(request, comment_id):
    quote = Comment.objects.get(id=comment_id)
    user = request.user.id
    comment.users_who_liked.remove(user)
    return redirect('/blog')

def customerAccount(request):
    data = cartData(request)
    cartItems = data['cartItems']
    user = request.user.id
    likedItems = request.user.products_user_favorited.all()
    products = Product.objects.all()
    context = {
        'cartItems': cartItems,
        'likedItems': likedItems,
        'products': products,
    }
    return render(request, 'store/customer_account.html', context)

def update_user(request):
    user = request.user.id
    request.user.username = request.POST['username']
    request.user.email = request.POST['email']
    request.user.save()
    messages.success(request, 'Succesfully updated account!')
    return redirect(f'/account')

def blog(request):
    data = cartData(request)
    cartItems = data['cartItems']
    context = {
        'all_comments': Comment.objects.all(),
        'cartItems': cartItems,
    }
    return render(request, 'store/blog.html', context)

def post_comment(request):
    errors = Comment.objects.validator(request.POST)
    if errors: 
        for val in errors.values():
            messages.error(request,val)
    elif request.user.is_authenticated:
        Comment.objects.create(
            content = request.POST['content'],
            creator = User.objects.get(id=request.user.id),
        )
    return redirect('/blog')

def weatherUpdate(request):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=a121802f42532c5c1d61eabf91d72d35'
    if request.method == 'POST':
        form = CityForm(request.POST)
        form.save()

    form = CityForm()

    cities = City.objects.all()

    weather_data = []

    try:
        for city in cities:

            r = requests.get(url.format(city)).json()

            city_weather = {
                'city' : city.name,
                'temperature' : r['main']['temp'],
                'description' : r['weather'][0]['description'],
                'icon' : r['weather'][0]['icon'],
            }
            
            weather_data.append(city_weather)
    except KeyError:
        pass
    except EXCEPTION as e:
        pass

    context = {'weather_data' : weather_data, 'form' : form}
    return render(request, 'store/weather.html', context)
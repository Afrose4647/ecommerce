from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Product, Cart, Order, OrderItem, Category
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import razorpay
from django.conf import settings

# ✅ Login
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('home')
    return redirect('home')


# ✅ Logout
def logout_user(request):
    logout(request)
    return redirect('home')


# ✅ Register
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('home')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('home')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('home')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Registration successful. Please login.')
        return redirect('home')

    return redirect('home')


# ✅ Home Page
def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()[:8]  # Display latest 8 products
    return render(request, 'store/home.html', {'categories': categories, 'products': products})


# ✅ Product List Page
def product(request):
    products = Product.objects.all()
    return render(request, 'store/product.html', {'products': products})


# ✅ Search Functionality
def search(request):
    query = request.GET.get('q')
    products = Product.objects.filter(name__icontains=query) if query else []
    return render(request, 'store/search_results.html', {'products': products, 'query': query})


# ✅ Cart Page
@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum([item.total_price() for item in cart_items])
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})


# ✅ Add to Cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('cart')


def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            count += item.quantity
    return {'cart_count': count}

# ✅ Remove from Cart
@login_required
def remove_from_cart(request, cart_id):
    item = get_object_or_404(Cart, id=cart_id)
    item.delete()
    return redirect('cart')


# ✅ Checkout Page
@login_required

def checkout(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        total = sum(float(item.product.price) * item.quantity for item in cart_items)

        # Razorpay Amount (in paise)
        amount = (total + 40) * 100

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": "1"
        })

        context = {
            'cart_items': cart_items,
            'total': total,
            'payment': payment,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'amount': amount
        }
        return render(request, 'store/checkout.html', context)

    else:
        return redirect('login')
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    amount = (total_amount + 40) * 100  # Amount in paise

    payment = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })

    context = {
        'payment': payment,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': amount,
        'total': total_amount
    }
    return render(request, 'store/checkout.html', context)



@csrf_exempt
def payment_success(request):
    return render(request, 'store/payment_success.html')


# ✅ Place Order
@login_required
def place_order(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')

        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            messages.error(request, "Your cart is empty!")
            return redirect('cart')

        total_price = sum(item.total_price() for item in cart_items) + 40  # +40 for delivery

        # Create Order
        order = Order.objects.create(
            user=request.user,
            name=name,
            phone=phone,
            email=email,
            address=address,
            payment_method=payment_method,
            total_price=total_price,
            status='Pending'
        )

        # Create Order Items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # Clear cart
        cart_items.delete()

        messages.success(request, "Order placed successfully!")
        return redirect('my_orders')

    else:
        return redirect('checkout')

#my orders
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/my_orders.html', {'orders': orders})

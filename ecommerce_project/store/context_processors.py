from .models import Cart

def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            count += item.quantity
    return {'cart_count': count}

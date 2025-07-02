from django.urls import path
from store import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register, name='register'),
    path('cart/', views.cart, name='cart'),
    path('search/', views.search, name='search'),
    path('checkout/', views.checkout, name='checkout'),
    path('product/', views.product, name='product'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('place_order/', views.place_order, name='place_order'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('payment_success/', views.payment_success, name='payment_success'),

]

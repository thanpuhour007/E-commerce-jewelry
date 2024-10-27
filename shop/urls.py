from django.urls import path, include
from . import views

handler404 = views.custom_404_view
urlpatterns = [
    path('', views.home, name='home'),
    path('user_login', views.user_login, name='user_login'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('profile/<int:id>', views.profile, name='profile'),
    path('edit_profile/<int:id>', views.edit_profile, name='edit_profile'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('products', views.products, name='products'),
    path('products/detail/<int:id>/', views.product_detail, name='product_detail'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('remove_cart_item/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('update_cart_item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart', views.cart, name='cart'),
    path('orders/', views.orders, name='orders'),
    path('orders/<int:order_id>/', views.customer_order_details, name='customer_order_details'),

    path('checkout/<int:id>/', views.checkout, name='checkout'),

    path('payment_success/', views.payment_success, name='payment_success'),

]

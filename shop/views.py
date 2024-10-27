import stripe
from django import template
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from Ecommerce import settings
from myadmin.models import (
    Product,
    Category,
    ProductType,
    ProductImage,
    MyUsers,
    CartItem, Order, Stock, Payment, OrderItem
)

stripe.api_key = settings.STRIPE_SECRET_KEY

register = template.Library()


def home(request):
    return render(request, 'shop/home.html')

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        print(username, password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, 'Login successful')
                return redirect('home')
            else:
                messages.error(request, 'Account is inactive. Please contact support.')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'shop/login.html')


# Logout function
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('home')


def sign_up(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if MyUsers.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            elif MyUsers.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
            else:
                user = MyUsers.objects.create_user(username=username, email=email, phone_number=phone_number,
                                                   password=password)
                user.save()
                messages.success(request, 'User created successfully')
                return redirect('user_login')
        else:
            messages.error(request, 'Passwords do not match')

    return render(request, 'shop/sign_up.html')


def base_view(request):
    cart = request.session.get('cart', {})

    # Calculate total items in the cart
    cart_item_count = sum(item['quantity'] for item in cart.values())

    # Pass the cart item count to all templates that extend this view
    return render(request, 'shop/base.html', {
        'cart_item_count': cart_item_count,
    })


@login_required
def profile(request, id):
    user = get_object_or_404(MyUsers, id=id)
    return render(request, 'shop/profile.html', {'user': user})


@login_required
def edit_profile(request, id):
    user = get_object_or_404(MyUsers, id=id)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_picture = request.FILES.get('user_picture')

        if username:
            if MyUsers.objects.filter(username=username).exclude(id=user.id).exists():
                messages.error(request, 'Username already exists.')
            else:
                user.username = username

        # Update email if provided
        if email:
            if MyUsers.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, 'Email already exists.')
            else:
                user.email = email

        # Update phone number if provided
        if phone_number:
            if MyUsers.objects.filter(phone_number=phone_number).exclude(id=user.id).exists():
                messages.error(request, 'Phone number already exists.')
            else:
                user.phone_number = phone_number

        # Update password if provided
        if password:
            if password == confirm_password:
                user.set_password(password)
            else:
                messages.error(request, 'Passwords do not match.')

        # Update profile picture if provided
        if user_picture:
            user.user_picture = user_picture

        # Save the updated user details if no errors
        if not messages.get_messages(request):
            user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile', id=user.id)

    return render(request, 'shop/edit_profile.html', {'user': user})


def products(request):
    # Fetch all categories for the dropdown
    categories = Category.objects.all()

    # Get search query and filter parameters from request
    search_query = request.GET.get('search', '').strip()
    category_id = request.GET.get('category')
    start_price = request.GET.get('startPrice')
    end_price = request.GET.get('endPrice')

    # Start with all products
    products = Product.objects.all()

    # Apply search filter
    if search_query:
        products = products.filter(product_name__icontains=search_query)

    # Apply category filter if a valid category_id is provided
    if category_id and category_id.isdigit():
        products = products.filter(category__id=int(category_id))

    # Apply price range filters if provided
    if start_price and start_price.isdigit():
        products = products.filter(price__gte=int(start_price))
    if end_price and end_price.isdigit():
        products = products.filter(price__lte=int(end_price))

    # Paginate the products list (show 10 products per page)
    paginator = Paginator(products, 16)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    # Include all current query parameters to maintain state in templates
    query_params = request.GET.copy()
    query_params.pop('page', None)  # Remove 'page' parameter to avoid duplication

    context = {
        'categories': categories,
        'products': products,
        'selected_category': category_id,
        'start_price': start_price,
        'end_price': end_price,
        'search_query': search_query,
        'query_params': query_params.urlencode(),  # Encode query parameters for use in URLs
    }
    return render(request, 'shop/products.html', context)


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    categories = Category.objects.all()
    types = ProductType.objects.all()
    product_images = ProductImage.objects.filter(product=product)

    context = {
        'product': product,
        'categories': categories,
        'types': types,
        'product_images': product_images
    }
    return render(request, 'shop/product_detail.html', context)


@login_required
@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            return JsonResponse({'success': False, 'error': 'Invalid quantity.'}, status=400)
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Quantity must be a number.'}, status=400)

    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if created:
        cart_item.cart_quantity = quantity
    else:
        cart_item.increase_quantity(quantity)

    cart_item.save()

    return JsonResponse(
        {'success': True, 'cart_quantity': cart_item.cart_quantity, 'total_price': cart_item.total_price()}
    )


@login_required
@require_POST
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)

    action = request.POST.get('action')
    try:
        if action == 'increase':
            cart_item.increase_quantity()
            messages.success(request, "Increased item quantity.")
        elif action == 'decrease':
            if cart_item.cart_quantity > 1:
                cart_item.decrease_quantity()
                messages.success(request, "Decreased item quantity.")
            else:
                messages.warning(request, "Minimum quantity is 1. Item cannot be reduced further.")
        else:
            quantity = int(request.POST.get('cart_quantity', 1))
            if quantity > 0:
                cart_item.cart_quantity = quantity
                cart_item.save()
                messages.success(request, "Cart updated successfully.")
            else:
                messages.error(request, "Quantity must be greater than zero.")
    except (ValueError, TypeError):
        messages.error(request, "Invalid quantity. Please enter a valid number.")

    return redirect('cart')


@login_required
@require_POST
def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.success(request, "Cart deleted successfully.")
    return redirect('cart')


@login_required
def cart(request):
    cart_items = CartItem.objects.select_related('product').filter(user=request.user)

    cart_subtotal = sum(item.product.price * item.cart_quantity for item in cart_items)

    cart_discount_total = sum(
        (item.product.price - item.product.final_price()) * item.cart_quantity for item in cart_items
    )
    total_amount = cart_subtotal - cart_discount_total
    order = None
    if cart_items.exists():
        order, created = Order.objects.get_or_create(
            user=request.user,
            status='Pending',
            defaults={'total_amount': total_amount}
        )

        if not created:
            order.total_amount = total_amount
            order.save()

    context = {
        'cart_items': cart_items,
        'cart_subtotal': cart_subtotal,
        'cart_discount_total': cart_discount_total,
        'total_amount': total_amount,
        'order': order,
    }

    return render(request, 'shop/cart.html', context)


@login_required
def checkout(request, id):
    order = get_object_or_404(Order, id=id, user=request.user)

    intent = stripe.PaymentIntent.create(
        amount=int(order.total_amount * 100),
        currency='usd',
        metadata={'order_id': order.id}
    )

    context = {
        'client_secret': intent.client_secret,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
        'order': order,
    }
    return render(request, 'shop/checkout.html', context)


@login_required
def payment_success(request):
    card_holder = request.GET.get('card_holder', 'Anonymous')

    # Step 1: Retrieve the most recent pending order for the logged-in user
    order = Order.objects.filter(user=request.user, status='Pending').last()
    if not order:
        messages.error(request, "No pending order found. Please make a valid payment.")
        return redirect('orders')

    try:
        with transaction.atomic():  # Ensures all actions happen as a single transaction
            # Step 2: Move Cart Items to Order Items
            cart_items = CartItem.objects.filter(user=request.user).select_related('product')
            if not cart_items:
                messages.error(request, "No items in the cart to complete the order.")
                return redirect('cart')

            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.cart_quantity,
                    price_at_order=cart_item.product.final_price(),
                )

            # Step 3: Update Order Status to 'Paid'
            order.status = 'Paid'
            order.save()

            # Step 4: Create Payment Record
            payment = Payment.objects.create(
                order=order,
                card_holder=card_holder,
            )
            order.payment = payment  # Link the payment to the order
            order.save()

            # Step 5: Reduce Stock Quantities for Ordered Items
            for item in order.order_items.select_related('product'):
                product_stock = get_object_or_404(Stock, product=item.product)

                # Reduce stock by order quantity if stock is sufficient
                if product_stock.stock_quantity >= item.quantity:
                    product_stock.stock_quantity -= item.quantity
                else:
                    # Warn if stock is insufficient
                    messages.warning(request,
                                     f"Insufficient stock for {item.product.product_name}. "
                                     f"Available: {product_stock.stock_quantity}, Requested: {item.quantity}")
                    product_stock.stock_quantity = 0  # Set to 0 if stock is exhausted

                product_stock.save()

            # Step 6: Clear Cart after successful stock deduction
            cart_items.delete()

            # Step 7: Success message after the process is complete
            messages.success(request, "Your payment was successful! Thank you for your order.")

    except Exception as e:
        messages.error(request, f"An error occurred while processing your order: {str(e)}")
        return redirect('orders')

    # Render success page with order and payment details
    return render(request, 'shop/payment_success.html', {
        'order': order,
        'payment': payment,
    })


@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'shop/orders.html', {'orders': orders})


@login_required
def customer_order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_details.html', {'order': order})


def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    return render(request, 'shop/contact.html')

from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Product, ProductImage, ProductType, Stock, MyUsers, Order
from django.contrib.auth import authenticate, login


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.role_name == 'admin':
                login(request, user)
                messages.success(request, 'Login successfully!')
                return redirect('myadmin')
            else:
                messages.error(request, 'You do not have admin privileges!')
        else:
            messages.error(request, 'Invalid username or password!')
    return render(request, 'myadmin/admin_login.html')

def exit(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('home')


def myadmin(request):
    order_count = Order.objects.count()
    product_count = Product.objects.count()
    category_count = Category.objects.count()

    # Count orders with status "Paid"
    sold_count = Order.objects.filter(status='Paid').count()

    # Count users with role_name equal to "customer"
    customers_count = MyUsers.objects.filter(role_name='customer').count()

    return render(request, 'myadmin/myadmin.html', {
        'order_count': order_count,
        'product_count': product_count,
        'category_count': category_count,
        'sold_count': sold_count,
        'customers_count': customers_count,
    })



def users(request):
    users = MyUsers.objects.all()
    users_count = users.count()
    return render(request, 'myadmin/user/users.html', {'users': users, 'users_count': users_count})


def deleteUsers(request, id):
    users = get_object_or_404(MyUsers, id=id)
    if request.method == 'POST':
        users.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect('users')
    return render(request, 'myadmin/user/add.html')


def category(request):
    categories = Category.objects.all()
    categories_count = categories.count()
    return render(request, 'myadmin/category/category.html', {
        'categories': categories,
        'categories_count': categories_count
    })


def addCategory(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        if category_name:
            Category.objects.create(category_name=category_name)
            messages.success(request, 'Category add successfully!')
        return redirect('category')
    return render(request, 'myadmin/category/add.html')


def editCategory(request, id):
    categories = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        if category_name:
            categories.category_name = category_name
            categories.save()
            messages.success(request, 'Category edit successfully!')
        return redirect('category')
    return render(request, 'myadmin/category/edit.html', {'categories': categories})


def deleteCategory(request, id):
    categories = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        categories.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('category')


def type(request):
    types = ProductType.objects.all()
    types_count = types.count()
    return render(request, 'myadmin/type/type.html', {
        'types': types,
        'types_count': types_count
    })


def addType(request):
    if request.method == 'POST':
        type_name = request.POST.get('type_name')
        if type_name:
            ProductType.objects.create(type_name=type_name)
            messages.success(request, 'Type add successfully!')
        return redirect('type')
    return render(request, 'myadmin/type/add.html')


def editType(request, id):
    types = get_object_or_404(ProductType, id=id)
    if request.method == 'POST':
        type_name = request.POST.get('type_name')
        if type_name:
            types.type_name = type_name
            types.save()
            messages.success(request, 'Type edit successfully!')
        return redirect('type')
    return render(request, 'myadmin/type/edit.html', {'types': types})


def deleteType(request, id):
    types = get_object_or_404(ProductType, id=id)
    if request.method == 'POST':
        types.delete()
        messages.success(request, 'Type deleted successfully!')
        return redirect('type')


def product(request):
    products = Product.objects.all()
    products_count = products.count()
    return render(request, 'myadmin/product/product.html',
                  {'products': products,
                   'products_count': products_count
                   })


def addProduct(request):
    if request.method == 'POST':
        try:
            product_name = request.POST.get('product_name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            discount_rate = request.POST.get('discount_rate')
            category_id = request.POST.get('category')
            type_id = request.POST.get('type')
            product_status = request.POST.get('product_status', 'False') == 'True'

            thumbnail = request.FILES.get('thumbnail')
            images = request.FILES.getlist('images')

            # Ensure that category and product type exist
            category = get_object_or_404(Category, id=category_id)
            product_type = get_object_or_404(ProductType, id=type_id)

            # Create the product
            product = Product.objects.create(
                product_name=product_name,
                description=description,
                price=price,
                discount_rate=discount_rate,
                category=category,
                product_type=product_type,
                product_status=product_status,
                thumbnail=thumbnail
            )

            # Add images to product
            for image in images:
                ProductImage.objects.create(product=product, image=image)

            # Create a Stock entry with a default quantity of 1
            Stock.objects.create(product=product, stock_quantity=1)

            messages.success(request, 'Product and stock added successfully!')
            return redirect('product')
        except Exception as e:
            messages.error(request, f"Error adding product: {str(e)}")
            return redirect('add_product')

    categories = Category.objects.all()
    types = ProductType.objects.all()
    return render(request, 'myadmin/product/add.html', {'categories': categories, 'types': types})


def editProduct(request, id):
    product = get_object_or_404(Product, id=id)  # Get the product based on the ID

    if request.method == 'POST':
        try:
            # Get data from the form
            product_name = request.POST.get('product_name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            discount_rate = request.POST.get('discount_rate')
            category_id = request.POST.get('category')
            type_id = request.POST.get('type')
            product_status = request.POST.get('product_status', 'False') == 'True'

            thumbnail = request.FILES.get('thumbnail')
            images = request.FILES.getlist('images')

            # Ensure that category and product type exist
            category = get_object_or_404(Category, id=category_id)
            product_type = get_object_or_404(ProductType, id=type_id)

            # Update the product details
            product.product_name = product_name
            product.description = description
            product.price = price
            product.discount_rate = discount_rate
            product.category = category
            product.product_type = product_type
            product.product_status = product_status

            # If a new thumbnail is uploaded, replace the old one
            if thumbnail:
                product.thumbnail = thumbnail

            product.save()  # Save the product updates

            # Save additional images
            if images:
                for image in images:
                    ProductImage.objects.create(product=product, image=image)  # This saves the file

            messages.success(request, 'Product updated successfully!')
            return redirect('product')  # Assuming 'product' is a valid URL name
        except Exception as e:
            messages.error(request, f"Error updating product: {str(e)}")
            return redirect('edit_product', id=product.id)

    # If GET request, retrieve categories, product types, and images for rendering in the form
    categories = Category.objects.all()
    types = ProductType.objects.all()
    product_images = ProductImage.objects.filter(product=product)  # Get the additional images for this product

    context = {
        'product': product,
        'categories': categories,
        'types': types,
        'product_images': product_images
    }

    return render(request, 'myadmin/product/edit.html', context)


def deleteProduct(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        ProductImage.objects.filter(product=product).delete()
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('product')


def stock(request):
    stocks = Stock.objects.all()
    stocks_count = stocks.count()
    return render(request, 'myadmin/stock/stock.html', {'stocks': stocks, 'stocks_count': stocks_count})


def addStock(request):
    search_query = request.GET.get('search', '')

    if request.method == 'POST':
        product_id = request.POST.get('product')
        stock_quantity = request.POST.get('stock_quantity')

        if not product_id or not stock_quantity:
            messages.error(request, "Please fill in all the required fields.")
            return redirect('addStock')

        try:
            product = get_object_or_404(Product, id=product_id)
            stock_quantity = int(stock_quantity)
            if stock_quantity <= 0:
                messages.error(request, "Quantity must be greater than 0.")
                return redirect('addStock')

            stock, created = Stock.objects.get_or_create(product=product)
            stock.stock_quantity += stock_quantity
            stock.save()

            messages.success(request, 'Stock successfully updated!')
            return redirect('stock')

        except ValueError:
            messages.error(request, "Invalid quantity value.")
            return redirect('addStock')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('addStock')

    if search_query:
        products = Product.objects.filter(product_name__icontains=search_query)
    else:
        products = Product.objects.all()

    return render(request, 'myadmin/stock/add.html', {'products': products, 'search_query': search_query})


def editStock(request, id):
    stock = get_object_or_404(Stock, id=id)  # Get stock by ID

    if request.method == 'POST':
        stock_quantity = request.POST.get('stock_quantity')

        # Check if quantity is provided
        if not stock_quantity:
            messages.error(request, "Please provide a quantity.")
            return redirect('editStock', id=id)

        try:
            # Validate quantity input
            stock_quantity = int(stock_quantity)
            if stock_quantity <= 0:
                messages.error(request, "Quantity must be greater than 0.")
                return redirect('editStock', id=id)

            # Update stock quantity
            stock.stock_quantity = stock_quantity
            stock.save()

            messages.success(request, 'Stock successfully updated!')
            return redirect('stock')  # Redirect to the stock list after update

        except ValueError:
            messages.error(request, "Invalid quantity value. Please enter a valid number.")
            return redirect('editStock', id=id)

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('editStock', id=id)

    # If GET request, prepopulate the form with existing stock data
    return render(request, 'myadmin/stock/edit.html', {
        'stock': stock,
        'product': stock.product,  # Pass the associated product
    })


def deleteStock(request, id):
    stock = get_object_or_404(Stock, id=id)
    if request.method == 'POST':
        stock.delete()
        messages.success(request, 'Stock deleted successfully!')
        return redirect('stock')


def order(request):
    orders = Order.objects.all()
    orders_count = orders.count()
    return render(request, 'myadmin/order/order.html', {
        'orders': orders,
        'orders_count': orders_count
    })

def order_details(request, id):
    order = get_object_or_404(Order, id=id)
    return render(request, 'myadmin/order/order_details.html', {'order': order})

def deleteOrder(request, id):
    orders = get_object_or_404(Order, id=id)
    if request.method == 'POST':
        orders.delete()
        messages.success(request, 'Order deleted successfully!')
        return redirect('order')

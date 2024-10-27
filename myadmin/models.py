from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.core.validators import MinValueValidator, RegexValidator
from Ecommerce import settings


class MyUserManager(BaseUserManager):
    """Manager class for MyUsers model."""

    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set.')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class MyUsers(AbstractBaseUser, PermissionsMixin):
    """Custom user model."""

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    join_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=False)
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                   message="Phone number must be entered in the format: '+999999999'.")]
    )
    user_picture = models.ImageField(upload_to='user_pictures/', null=True, blank=True)
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )
    role_name = models.CharField(max_length=50, choices=ROLE_CHOICES, default='customer')
    is_staff = models.BooleanField(default=False)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='myadmin_user_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='myadmin_user_set',
        blank=True
    )
    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'my_users'
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username


class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        db_table = "categories"

    def __str__(self):
        return self.category_name


class ProductType(models.Model):
    type_name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Product Types"
        db_table = "product_types"

    def __str__(self):
        return self.type_name


class Product(models.Model):
    product_name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name="products")
    thumbnail = models.ImageField(upload_to='products/thumbnails/')
    product_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Products"
        db_table = "products"

    def __str__(self):
        return self.product_name

    def final_price(self):
        return self.price * (1 - (self.discount_rate / 100))


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='products/images/')

    class Meta:
        verbose_name_plural = "Product Images"
        db_table = "product_images"

    def __str__(self):
        return f"Image for {self.product.product_name}"


class CartItem(models.Model):
    user = models.ForeignKey(MyUsers, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    cart_quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Cart Items"
        db_table = "cart_items"
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.product.product_name} - {self.user.username}"

    def total_price(self):
        return self.product.final_price() * self.cart_quantity

    def increase_quantity(self, quantity=1):
        self.cart_quantity += quantity
        self.save()

    def decrease_quantity(self, quantity=1):
        if self.cart_quantity > quantity:
            self.cart_quantity -= quantity
            self.save()
        else:
            self.delete()



class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="stock")
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    restock_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Stock"
        db_table = "stock"

    def __str__(self):
        return f"{self.product.product_name} - Stock: {self.stock_quantity}"

    def is_in_stock(self):
        return self.stock_quantity > 0

class OrderItem(models.Model):
    """Model to store individual items within an order."""

    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name_plural = "Order Items"
        db_table = "order_items"

    def __str__(self):
        return f"OrderItem: {self.product.product_name} (x{self.quantity})"

    def total_price(self):
        return self.price_at_order * self.quantity


class Order(models.Model):
    """Model to store overall order information."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ], default='Pending')
    payment = models.OneToOneField('Payment', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='order_payment')

    class Meta:
        verbose_name_plural = "Orders"
        db_table = "orders"

    def __str__(self):
        return f"Order #{self.id} - User: {self.user.username} - Status: {self.status}"

    def calculate_total_amount(self):
        """Calculate and update the total amount of the order."""
        self.total_amount = sum(item.total_price() for item in self.order_items.all())
        self.save()

    def add_cart_items(self, cart_items):
        """Create order items based on the current cart items."""
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=self,
                product=cart_item.product,
                quantity=cart_item.cart_quantity,
                price_at_order=cart_item.product.final_price()
            )


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment_order', null=True, blank=True)
    card_holder = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Payments"
        db_table = "payments"

    def __str__(self):
        return f"Payment: {self.card_holder}"

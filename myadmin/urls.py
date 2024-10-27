from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    path('exit/', views.exit, name='exit'),
    path('dashboard', views.myadmin, name='myadmin'),
    path('users', views.users, name='users'),
    path('users/delete/<int:id>', views.deleteUsers, name='deleteUsers'),
    # category
    path('category', views.category, name='category'),
    path('category/add', views.addCategory, name='addCategory'),
    path('category/<int:id>/edit/', views.editCategory, name='editCategory'),
    path('category/<int:id>/delete/', views.deleteCategory, name='deleteCategory'),
    # type
    path('type', views.type, name='type'),
    path('type/add', views.addType, name='addType'),
    path('type/<int:id>/edit/', views.editType, name='editType'),
    path('type/<int:id>/delete/', views.deleteType, name='deleteType'),
    # product
    path('product', views.product, name='product'),
    path('products/add/', views.addProduct, name='addProduct'),
    path('products/edit/<int:id>/', views.editProduct, name='editProduct'),
    path('products/delete/<int:id>/', views.deleteProduct, name='deleteProduct'),
    # stock
    path('stock', views.stock, name='stock'),
    path('stock/add/', views.addStock, name='addStock'),
    path('stock/edit/<int:id>/', views.editStock, name='editStock'),
    path('stock/delete/<int:id>/', views.deleteStock, name='deleteStock'),

    path('order', views.order, name='order'),
    path('order_details/<int:id>', views.order_details, name='order_details'),

    path('order/<int:id>/delete/', views.deleteOrder, name='deleteOrder'),
]

"""laptopsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from CustomerSite.views import *
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path("admin/",admin,name="admin"),
    path("home/",home),
    path('laptops/', LaptopListView.as_view(), name='laptop_list'),
    path('laptops/<int:pk>/', LaptopDetailView.as_view(), name='laptop_detail'),
    path('add_to_cart/<int:laptop_id>/<int:quantity>/',add_to_cart, name='add_to_cart'),
    path('cart/', CartListView.as_view(), name='cart_list'),
    path('modify_cart_quantity/<int:laptop_id>/', modify_cart_quantity, name='modify_cart_quantity'),
    path('remove_item_on_cart/<int:laptop_id>/',  remove_from_cart, name='remove_from_cart'),
    path('add_laptop/', add_laptop, name='add_laptop'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('edit_laptop/<int:pk>/', edit_laptop, name='edit_laptop'),
    path('edit_images/<int:pk>/', edit_images, name='edit_images'),
    path('edit_image/<int:pk>/', edit_image, name='edit_image'),
    path('delete_laptop/<int:pk>/',delete_laptop , name='delete_laptop'),
    
    
    

     
   
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

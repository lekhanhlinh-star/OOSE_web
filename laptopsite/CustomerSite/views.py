from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
# Create your views here.
from .models import Laptop

def home(request):
    return render(request, 'index.html')


class LaptopListView(ListView):
    model = Laptop
    template_name = 'all-product.html'
    
    
class LaptopDetailView(DetailView):
    model = Laptop
    template_name = 'product-page.html'
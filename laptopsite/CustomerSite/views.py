from django.shortcuts import render,redirect
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from .Forms import LaptopForm,CustomerCreationForm,ImageForm
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.contrib import messages
# Create your views here.
from django.contrib.auth import logout
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords')
nltk.download('wordnet')

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()

    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)

    # Tokenize text into individual words
    words = text.split()

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]

    # Lemmatize words
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]

    # Join words back into a single string
    preprocessed_text = ' '.join(words)
    
    return preprocessed_text

import json
from .models import Laptop,Image,Brand,Account, Order, OrderItem

def home(request):
    return render(request, 'index.html')


def admin(request):
    laptops = Laptop.objects.all()
    return render(request, 'admin.html',{'laptops': laptops})
class LaptopListView(ListView):
    model = Laptop
    template_name = 'all-product.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Do some filtering or sorting here if needed
        
         # Retrieve filter parameters from the URL query string
        brand = self.request.GET.get('brand')
        ram_size = self.request.GET.get('ram_size')
        cpu_type = self.request.GET.get('cpu_type')
        sort_by = self.request.GET.get('sort_by')
        search_query = self.request.GET.get('search_query')
        # Add more filter parameters as needed

        # Apply filters if the corresponding parameters exist
        if brand:
            queryset = queryset.filter(brand=brand)
        if ram_size:
            queryset = queryset.filter(ram__contains=ram_size)
        if cpu_type:
            queryset = queryset.filter( processor__contains=cpu_type)
        # Add more filter conditions for additional parameters
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        if search_query:
            # Preprocess the search query (cleaning, lowercasing, etc.)
            preprocessed_query = preprocess_text(search_query)

            # Extract the laptop descriptions
            laptop_descriptions = [
            ' '.join([
                laptop.description,
                laptop.brand.name,
                laptop.ram,
                laptop.VGA,
                laptop.name,
                laptop.processor
            ]) for laptop in queryset
        ]

            # Create a TF-IDF vectorizer and fit it on the laptop descriptions
            vectorizer = TfidfVectorizer()
            laptop_vectors = vectorizer.fit_transform(laptop_descriptions)

            # Transform the query into a vector
            query_vector = vectorizer.transform([preprocessed_query])
            

            # Calculate the similarity scores between the query vector and laptop vectors
            similarities = cosine_similarity(query_vector, laptop_vectors).flatten()
            
            # Sort laptops based on similarity scores in descending order
            laptop_scores = list(zip(queryset, similarities))
            laptop_scores.sort(key=lambda x: x[1], reverse=True)
            

            # Reorder the queryset based on the similarity scores
            queryset = [laptop for laptop, _ in laptop_scores]

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'All Products'
        context['brands'] = Brand.objects.all()
        context['ram_types'] = Laptop.objects.values_list('ram', flat=True).distinct()
        context['ram_gb'] = [ram.split()[0] for ram in context['ram_types']]
        
        return context
    

class LaptopDetailView(DetailView):
    model = Laptop
    template_name = 'product-page.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Retrieve the current laptop object
        current_laptop = self.get_object()
        
        # Retrieve all laptops from the database excluding the current laptop
        all_laptops = Laptop.objects.exclude(pk=current_laptop.pk)
        
        # Extract the laptop descriptions
        laptop_descriptions = [
            ' '.join([
                laptop.description,
                laptop.brand.name,
                laptop.ram,
                laptop.VGA,
                laptop.name,
                laptop.processor
            ]) for laptop in all_laptops
        ]
        
        # Create a TF-IDF vectorizer and fit it on the laptop descriptions
        vectorizer = TfidfVectorizer()
        laptop_vectors = vectorizer.fit_transform(laptop_descriptions)
        
        # Transform the current laptop description into a vector
        current_laptop_vector = vectorizer.transform([' '.join([
            current_laptop.description,
            current_laptop.brand.name,
            current_laptop.ram,
            current_laptop.VGA,
            current_laptop.name,
            current_laptop.processor
        ])])
        
        # Calculate the similarity scores between the current laptop vector and other laptop vectors
        similarity_scores = cosine_similarity(current_laptop_vector, laptop_vectors).flatten()
        laptop_scores = list(zip(all_laptops,   similarity_scores))
        print( laptop_scores)
        laptop_scores.sort(key=lambda x: x[1], reverse=True)
        
        similar_laptops  = [laptop for laptop, _ in laptop_scores]
        similar_laptops=similar_laptops[:6]
        
       
        
        
        context['similar_laptops'] = similar_laptops
        
        return context
   
def add_to_cart(request, laptop_id,quantity=1):
    if request.method == 'GET':
        laptop = Laptop.objects.get(id=laptop_id)
        
        account = request.user.id
        # Assuming the authenticated user has an associated Account instance
        Customer=Account.objects.get(id=account)
        print("account:",Customer)
        quantity = int(quantity)
        
        Check=Customer.add_to_cart(laptop_id, quantity)
        if Check==True:
            messages.success(request, 'Item added to cart successfully!')
        else:
            messages.error(request, 'Item added to cart error ')
            
            
        
    
    return redirect('laptop_detail', pk=laptop_id)
class CartListView(ListView):
    model = OrderItem
    template_name = 'cart.html'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            # Retrieve the cart items for the logged-in user
            order = Order.objects.filter(account=user, complete=False).first()
            if order:
                queryset = order.orderitem_set.all()
                return queryset

        return OrderItem.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        if user.is_authenticated:
            # Retrieve the cart items for the logged-in user
            order = Order.objects.filter(account=user, complete=False).first()
            if order:
                # Create a list of dictionaries that contain the OrderItem object, the quantity,
                # the total price, and the associated Laptop for each item
                item_data = []
                for order_item in order.orderitem_set.all():
                    quantity = order_item.quantity
                    total_price = quantity * order_item.product.price
                    item_data.append({
                        'order_item': order_item,
                        'quantity': quantity,
                        'total_price': total_price,
                        'product': order_item.product,
                    })

                # Add the item data to the context dictionary
                context['items'] = item_data

        return context
    
    
    
def modify_cart_quantity(request, laptop_id):
    if request.method == 'POST':
        print(request.POST.get('quantity'))
        new_quantity = int(request.POST.get('quantity'))

        # Retrieve the logged-in user's cart
        user = request.user
        order = Order.objects.filter(account=user, complete=False).first()
        if order:
            # Get the order item for the given laptop ID
            order_item = get_object_or_404(OrderItem, order=order, product_id=laptop_id)

            # Update the quantity of the order item
            order_item.quantity = new_quantity
            order_item.save()

            messages.success(request, 'Cart quantity updated successfully!')
        else:
            messages.error(request, 'Invalid cart')

    return redirect('cart')
    
def add_laptop(request):
    if request.method == 'POST':
        laptop_form = LaptopForm(request.POST)
        image_form=ImageForm(request.POST)
        
        files=request.FILES.getlist("image")

        if laptop_form.is_valid():
            laptop = laptop_form.save(commit=False)
            laptop.save()
            for file in files:
                Image.objects.create(laptop=laptop,image=file)
            messages.success(request,"New Laptop added")

           
    else:
        laptop_form = LaptopForm()
        image_form=ImageForm()

    return render(request, 'add_product.html', {'laptop_form': laptop_form,"image_form":image_form})

    
def remove_from_cart(request, pk):
    user = request.user
    if user.is_authenticated:
        account = request.user.id
        # Assuming the authenticated user has an associated Account instance
        Customer=Account.objects.get(id=account)
        
        Check= Customer.delete_itemcart(pk)
        if Check==True:
            messages.success(request, 'Item added to cart successfully!')
            return redirect("cart_list")
         
        else:
            messages.error(request, 'Item added to cart error ')
            return redirect("cart_list")
            
    else:
        return redirect("login")      
   








def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('laptop_list')   # redirect somewhere you wants
            else:
                return render(request, 'login.html', {'error': 'Your account is disabled'})
        else:
            return render(request, 'login.html', {'error': 'Invalid login credentials'})
    else:
        return render(request, 'login.html')
    
    
    
def register_view(request):
    if request.method == 'POST':
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomerCreationForm()
    return render(request, 'register.html', {'form': form})



def edit_laptop(request, pk):
    laptop = get_object_or_404(Laptop, pk=pk)
    if request.method == 'POST':
        form = LaptopForm(request.POST, request.FILES, instance=laptop)
        if form.is_valid():
            form.save()
            messages.success(request,"Edit success")
    else:
        form = LaptopForm(instance=laptop)
        

    return render(request, 'edit-product.html', {'form': form})


def delete_laptop(request,pk):
    laptop = get_object_or_404(Laptop, pk=pk)
    laptop.is_active=False
    laptop.save()
    
    return redirect('admin')
    

def edit_images(request, pk):
    laptop = get_object_or_404(Laptop, pk=pk)


    return render(request, 'edit_images.html', { 'laptop': laptop})
def edit_image(request, pk):
    image = get_object_or_404(Image, pk=pk)
    
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            return redirect('edit_image', pk=image.pk)
    else:
        form = ImageForm(instance=image)
    
    return render(request, 'edit-image.html', {'form': form, 'image': image})





def Filter(request):
    Filter_brand=Brand.objects.all()
    return render(request, 'all-product.html', {"Brand":Filter_brand})
    
    
    
def subtract_quantity_cart(request,pk):
    user = request.user
    if user.is_authenticated:
        account = request.user.id
        # Assuming the authenticated user has an associated Account instance
        Customer=Account.objects.get(id=account)
        
        Check= Customer.subtract_quantity_cart(pk)
        if Check==True:
            messages.success(request, 'Item added to cart successfully!')
            return redirect("cart_list")
         
        else:
            messages.error(request, 'Item added to cart error ')
            return redirect("cart_list")
            
    else:
        return redirect("login")  
def add_quantity_cart(request,pk):
    user = request.user
    if user.is_authenticated:
        account = request.user.id
        # Assuming the authenticated user has an associated Account instance
        Customer=Account.objects.get(id=account)
        
        Check= Customer.add_quantity_cart(pk)
        if Check==True:
            messages.success(request, 'Item added to cart successfully!')
            return redirect("cart_list")
         
        else:
            messages.error(request, 'Item added to cart error ')
            return redirect("cart_list")
            
    else:
        return redirect("login")        
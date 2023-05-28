from django.shortcuts import render,redirect
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from .Forms import LaptopForm,CustomerCreationForm,ImageForm
from django.forms import modelformset_factory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.contrib import messages
# Create your views here.
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
from .models import Laptop,Image,Brand

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
    
    
def add_to_cart(request, laptop_id, quantity=1):
    # Check if the laptop_id parameter is null
    if laptop_id is None or laptop_id == '':
        return JsonResponse({'status': 'error', 'message': 'Invalid laptop ID'})

    # Get the laptop and quantity from the request
    laptop = Laptop.objects.get(id=laptop_id)
    quantity = int(quantity)

    # Get the current cart data from the user's cookies
    cart_data = request.COOKIES.get('cart', '{}')
    cart = json.loads(cart_data)

    # Add the new laptop to the cart
    if str(laptop.id) in cart:
        cart[str(laptop.id)] += quantity
    else:
        cart[str(laptop.id)] = quantity

    # Convert the cart data to a JSON string and store it in a cookie
    response=  redirect('laptop_detail', pk=laptop.id)

    # response = JsonResponse({'status': 'success'})
    response.set_cookie('cart', json.dumps(cart))
    messages.success(request, 'Item added to cart successfully!')
   
    return  response
class CartListView(ListView):
    model = Laptop
    template_name = 'cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve the items in the cart from a cookie
        cart_data = self.request.COOKIES.get('cart', '{}')
        cart = json.loads(cart_data)

        # Retrieve the associated Laptop objects from the database
        laptop_ids = [int(id) for id in cart.keys()]
        laptops = Laptop.objects.filter(id__in=laptop_ids)

        # Create a list of dictionaries that contain the Laptop object, the quantity and the total price of each item
        item_data = []
        for laptop in laptops:
            quantity = cart[str(laptop.id)]
            total_price = quantity * laptop.price
            item_data.append({'product': laptop, 'quantity': quantity, 'total_price': total_price})

        # Add the item data to the context dictionary
        context['items'] = item_data

        return context
    
    
    
def modify_cart_quantity(request, laptop_id):
    # Ret9rieve the new quantity from the request
 
    if request.method == 'POST':
        print(request.POST.get('quantity'))
        new_quantity = int(request.POST.get('quantity'))

        # Get the current cart data from the user's cookies
        cart_data = request.COOKIES.get('cart', '{}')
        cart = json.loads(cart_data)

        # Check if the laptop with the given ID is in the cart
        if str(laptop_id) in cart:
            # Update the quantity of the laptop in the cart
            cart[str(laptop_id)] = new_quantity

            # Convert the updated cart data to a JSON string and store it in a cookie
            response = redirect('cart')
            response.set_cookie('cart', json.dumps(cart))
            messages.success(request, 'Cart quantity updated successfully!')
        else:
            messages.error(request, 'Invalid laptop ID')

        return response
    
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

    
def remove_from_cart(request, laptop_id):
    # Check if the laptop_id parameter is null
    if laptop_id is None or laptop_id == '':
        return JsonResponse({'status': 'error', 'message': 'Invalid laptop ID'})

    # Get the current cart data from the user's cookies
    cart_data = request.COOKIES.get('cart', '{}')
    cart = json.loads(cart_data)
    print(cart)
    # Remove the laptop from the cart
    if str(laptop_id) in cart:
        del cart[str(laptop_id)]
    else:
        return JsonResponse({'status': 'error', 'message': 'Laptop not found in cart'})

    # Convert the cart data to a JSON string and store it in a cookie

    response=  redirect('cart_list')

    response.set_cookie('cart', json.dumps(cart))
    messages.success(request, 'Item removed from cart successfully!')

    return response








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
    
    
    
    
    
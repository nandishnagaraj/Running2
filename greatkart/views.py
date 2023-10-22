from django.shortcuts import render
from store.models import Product
import os
import glob

def home(request):
    image_folder = "./static/images/banners"
    image_paths = glob.glob(os.path.join(image_folder, "*.jpg"))  # Adjust the file extension as needed
    
    products = Product.objects.all().filter(is_available=True).order_by('created_date')
    context = {
        'products': products,
        'image_paths': image_paths,
    }
    return render(request, 'home.html', context)

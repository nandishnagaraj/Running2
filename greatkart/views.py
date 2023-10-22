
from django.shortcuts import render
from store.models import Product
import os
import glob

def home(request):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_folder = os.path.join(base_dir, 'greatkart\static\images\\banners')
    image_paths = glob.glob(os.path.join(image_folder, "*.jpg"))
    
    products = Product.objects.all().filter(is_available=True).order_by('created_date')
    context = {
        'products': products,
        'image_paths': image_paths,
    }
    return render(request, 'home.html', context)

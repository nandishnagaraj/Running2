from django.shortcuts import render
from store.models import Product
import os
import glob
from django.conf import settings

def home(request):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(base_dir)
    # Construct the path to the image folder relative to your project directory
    image_folder = 'greatkart/static/images/banners'
    print(image_folder)
    # Get the list of image file names (not absolute paths)
    image_paths = [os.path.join(image_folder, os.path.basename(image)) for image in glob.glob(os.path.join(base_dir, image_folder, "*.jpg"))]

    products = Product.objects.all().filter(is_available=True).order_by('created_date')
    context = {
        'products': products,
        'image_paths': image_paths,
    }
    return render(request, 'home.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from carts.models import CartItem
from carts.views import _cart_id
from orders.models import OrderProduct
from .models import Product, ReviewRating, DownloadRecord  
from category.models import Category
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from accounts.models import Account, Coach

def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)   

    context = {
        'single_product': single_product,
        'in_cart'       : in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'registereduser':request.user.is_authenticated,
    }
    return render(request, 'store/product_detail.html', context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(shortdescription__icontains=keyword) | Q(product_name__icontains=keyword) | Q(longdescription__icontains=keyword))
            product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)

def downloadPDF(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
        # In this example, let's assume you have a 'pdf_file' field in your Product model
    pdf_file = product.pdf_file

    if pdf_file:
            if request.user.is_authenticated:
                user = request.user
            else:
                user = None
            download_record = DownloadRecord.objects.create(user=user, product=product)
            # Set the content type as application/pdf to tell the browser it's a PDF
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            # Set the content disposition to 'attachment' to force download
            response['Content-Disposition'] = f'attachment; filename="{product.product_name}.pdf"'
            return response

        # Handle the case where the PDF file is not available
    return HttpResponse("PDF not available", status=404)

@login_required
def coachDashboard(request):
    coach = request.user.coach  # Assuming a OneToOneField between Account and Coach
    products = OrderProduct.objects.filter(coach=coach, ordered=True)
    user_purchases = []
    for product in products:
        user_purchases.append({
            'user': product.user,
            'product': product.product,
            'quantity': product.quantity,
            'price': product.product_price,
        })
    context = {
        'products': products,
        'user_purchases': user_purchases,
    }

    return render(request, 'coach/coach_product_view.html', context)


def get_products_purchased_by_user_for_coach(user_id, coach_id):
    try:
        user = Account.objects.get(id=user_id)
        coach = Coach.objects.get(id=coach_id)
        
        # Get the OrderProduct instances for the user, coach combination
        order_products = OrderProduct.objects.filter(user=user, coach=coach, ordered=True)

        # Extract product details from OrderProduct instances
        products_purchased = []
        for order_product in order_products:
            product_info = {
                'product_name': order_product.product.product_name,
                'quantity': order_product.quantity,
                'product_price': order_product.product_price,
                'coach_name': order_product.coach.user.username,
            }
            products_purchased.append(product_info)

        return products_purchased

    except Account.DoesNotExist:
        return None
    except Coach.DoesNotExist:
        return None

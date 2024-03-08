from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import razorpay
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings
import random


def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)        
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        for variation in product_variation:
            if(variation.variation_value == 'Generic Event'):
                pdf_file = orderproduct.product.pdf_file
                print(pdf_file)
                if pdf_file:
                    # Send email with the attached PDF
                    mail_subject = 'Thank you for your order!'
                    message = render_to_string('orders/order_recieved_email.html', {
                        'user': request.user,
                        'order': order,
                        'orderproduct': orderproduct,
                        'variationname': variation.variation_value,
                    })
                    to_email = request.user.email

                    send_email = EmailMessage(mail_subject, message, to=[to_email])
                    send_email.attach(f'{orderproduct.product.product_name}{orderproduct.product.coach}{variation.variation_value}.pdf', pdf_file.read(), 'application/pdf')
                    send_email.send()
            else:
                template_path = f"plantemplates/{orderproduct.product.product_name}{orderproduct.product.coach}{variation.variation_value}.html"
                print(template_path)
                template = get_template(template_path)
                interval_runs_result = interval_runs(order.timings, metrics="km")
                strides_runs_result = strides_runs(order.timings, metrics="km")
                fartlek_runs_result = fartlek_runs(order.timings, metrics="km")
                long_runs_result = long_runs(order.timings, metrics="km")
                tempo_runs_result = tempo_runs(order.timings, metrics="km")
                easy_runs_result = easy_runs(order.timings, metrics="km")
                context = {'customerorder':order,'strides_runs_result':strides_runs_result, 'easy_runs_result':easy_runs_result, 'tempo_runs_result':tempo_runs_result, 'interval_runs_result':interval_runs_result,'fartlek_runs_result':fartlek_runs_result,'long_runs_result':long_runs_result}  # Add the necessary context for your template
                html = template.render(context)
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{orderproduct.product.product_name}{orderproduct.product.coach}{variation.variation_value}.pdf"'
                pisa_status = pisa.CreatePDF(html, dest=response)
                if pisa_status.err:
                    return HttpResponse('We had some errors <pre>' + html + '</pre>')

                # Send order recieved email to customer
                mail_subject = 'Thank you for your order!'
                message = render_to_string('orders/order_recieved_email.html', {
                    'user': request.user,
                    'order': order,
                    'orderproduct':orderproduct,
                    'variationname':variation.variation_value,
                })
                to_email = request.user.email
                send_email = EmailMessage(mail_subject, message, to=[to_email])
                send_email.attach(f'{orderproduct.product.product_name}{orderproduct.product.coach}{variation.variation_value}.pdf', response.content, 'application/pdf')
                send_email.send()
            

   # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # send pdf to customer
    

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)

# Create your views here.
def place_order(request, total=0, quantity=0,):
    current_user = request.user

    # Get discount value from the user instance
    discount = current_user.discount

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    total -= (total * discount / 100)
    tax = (12 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']            
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.timingsinMinutes = form.cleaned_data['timingsinMinutes']
            data.timingsinSeconds = form.cleaned_data['timingsinSeconds']
            data.timings = ((data.timingsinMinutes * 60) + data.timingsinSeconds)
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))           
            payment = client.order.create({'amount': int(grand_total * 100), 'currency': 'INR','payment_capture': '1'})            
            payment_id = payment['id']

            # Print or use the payment ID as needed
            
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'grand_total_razorpay': int(grand_total * 100),
                'razorpayid': payment_id,
                'username':current_user,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')
    

def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')


def calculate_runs(total_seconds, distance, adjustment_range=(0.85, 0.92), metrics="km"):
    try:
        # Randomize the adjustment factor within the specified range
        adjustment_factor = random.uniform(*adjustment_range)
        adjusted_total_seconds = total_seconds * adjustment_factor

        # Calculate pace
        pace_seconds = adjusted_total_seconds / distance
        pace_minutes = int(pace_seconds / 60)
        pace_seconds %= 60
        pace_seconds_rounded = round(pace_seconds, 2) 

        # Calculate the pace range
        lower_bound = f"{pace_minutes}:{max(0, int(pace_seconds_rounded - 5)):02d}"
        upper_bound = f"{pace_minutes}:{min(59, int(pace_seconds_rounded + 5)):02d}"

        unit = "mile" if metrics == "miles" else "km"
        runs_result = f"Pace range: {lower_bound} to {upper_bound} per {unit}."

        return runs_result
    except ZeroDivisionError:
        raise ValueError("Distance cannot be zero.")

def interval_runs(total_seconds, metrics="km"):
    return calculate_runs(total_seconds, 5.0, metrics=metrics)

def strides_runs(total_seconds, metrics="km"):
    return calculate_runs(total_seconds, 5.0, adjustment_range=(0.80, 0.90), metrics=metrics)

def tempo_runs(total_seconds, metrics="km"):
    return calculate_runs(total_seconds, 5.0, adjustment_range=(1.06, 1.15), metrics=metrics)

def easy_runs(total_seconds, metrics="km"):
    return calculate_runs(total_seconds, 5.0, adjustment_range=(1.40, 1.65), metrics=metrics)

def long_runs(total_seconds, metrics="km"):
    return calculate_runs(total_seconds, 5.0, adjustment_range=(1.20, 1.35), metrics=metrics)

def fartlek_runs(total_seconds, metrics="km"):
    return calculate_runs(total_seconds, 5.0, adjustment_range=(1.10, 1.20), metrics=metrics)

def extract_seconds(total_time):
    try:
        minutes, seconds = map(int, total_time.split(':'))
        if 0 <= minutes <= 59 and 0 <= seconds <= 59:
            return minutes * 60 + seconds  # Convert minutes to seconds and add to seconds
        else:
            raise ValueError("Invalid minutes or seconds value.")
    except ValueError:
        raise ValueError("Invalid time format. Please use 'mm:ss' format.")

def calculate_pace(total_seconds, distance, metrics="km"):
    try:
        pace_seconds = total_seconds / distance
        pace_minutes = int(pace_seconds / 60)
        pace_seconds %= 60
        pace_seconds_rounded = round(pace_seconds)

        unit = "mile" if metrics == "miles" else "km"
        return pace_minutes, pace_seconds_rounded, unit
    except ZeroDivisionError:
        raise ValueError("Distance cannot be zero.")

def calculate_pace_km(total_seconds):
    return calculate_pace(total_seconds, 5.0)

# def order_in_razorpay(request):
#     order_number = request.GET.get('order_number')
#     transID = request.GET.get('payment_id')
   

#     try:
#         order = Order.objects.get(order_number=order_number, is_ordered=True)
#         ordered_products = OrderProduct.objects.filter(order_id=order.id)

#         subtotal = 0
#         for i in ordered_products:
#             subtotal += i.product_price * i.quantity
        
#         payment = Payment.objects.get(payment_id=transID)
        
#         context = {
#             'order': order,
#             'ordered_products': ordered_products,
#             'order_number': order.order_number,
#             'transID': payment.payment_id,
#             'payment': payment,
#             'subtotal': subtotal,
#         }
#         return render(request, 'orders/order_complete.html', context)
#     except (Payment.DoesNotExist, Order.DoesNotExist):
#         return redirect('home')
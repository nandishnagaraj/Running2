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
                template = get_template(template_path)
                context = {'customerorder':order}  # Add the necessary context for your template
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

            client = razorpay.Client(auth=("rzp_test_yu3IOJAh3QwXPK", "S0EuAjAVYsMMprwVYx2LWjrU"))           
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
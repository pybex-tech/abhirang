from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.contrib import messages
import razorpay
import json

from orders.models import Order
from .models import Payment


# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def initiate_payment(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    if order.payment_status == "paid":
        messages.info(request, "This order has already been paid.")
        return redirect("orders:order_detail", order_number=order_number)
    
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            "user": request.user,
            "payment_method": "razorpay",
            "amount": order.total_amount,
            "currency": "INR",
        }
    )
    
    if not payment.razorpay_order_id:
        try:
            amount_in_paise = int(float(order.total_amount) * 100)
            
            razorpay_order = razorpay_client.order.create({
                "amount": amount_in_paise,
                "currency": "INR",
                "payment_capture": 1,
                "notes": {
                    "order_number": order.order_number,
                    "user_id": str(request.user.id),
                }
            })
            
            payment.razorpay_order_id = razorpay_order["id"]
            payment.transaction_data = razorpay_order
            payment.status = "processing"
            payment.save()
            
        except Exception as e:
            messages.error(request, f"Error initiating payment: {str(e)}")
            return redirect("orders:order_detail", order_number=order_number)
    
    context = {
        "order": order,
        "payment": payment,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": payment.razorpay_order_id,
        "amount": int(float(payment.amount) * 100),
        "currency": payment.currency,
        "callback_url": request.build_absolute_uri("/") + "payments/callback/",
        "user_name": request.user.get_full_name() or request.user.username,
        "user_email": request.user.email,
        "user_phone": order.shipping_phone,
    }
    
    return render(request, "payments/payment_page.html", context)


@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        try:
            razorpay_payment_id = request.POST.get("razorpay_payment_id")
            razorpay_order_id = request.POST.get("razorpay_order_id")
            razorpay_signature = request.POST.get("razorpay_signature")
            
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature
            }
            
            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
                
                payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
                payment.razorpay_payment_id = razorpay_payment_id
                payment.razorpay_signature = razorpay_signature
                payment.mark_as_success()
                
                messages.success(request, "Payment successful! Your order has been confirmed.")
                return redirect("payments:payment_success", order_number=payment.order.order_number)
                
            except razorpay.errors.SignatureVerificationError:
                payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
                payment.mark_as_failed("Payment signature verification failed")
                
                messages.error(request, "Payment verification failed. Please try again.")
                return redirect("payments:payment_failed", order_number=payment.order.order_number)
                
        except Payment.DoesNotExist:
            messages.error(request, "Payment record not found.")
            return redirect("core:index")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect("core:index")
    
    return HttpResponseBadRequest()


@login_required
def payment_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    payment = get_object_or_404(Payment, order=order)
    
    context = {
        "order": order,
        "payment": payment,
    }
    
    return render(request, "payments/payment_success.html", context)


@login_required
def payment_failed(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    payment = get_object_or_404(Payment, order=order)
    
    context = {
        "order": order,
        "payment": payment,
    }
    
    return render(request, "payments/payment_failed.html", context)


@csrf_exempt
def razorpay_webhook(request):
    if request.method == "POST":
        try:
            webhook_body = request.body
            webhook_signature = request.META.get("HTTP_X_RAZORPAY_SIGNATURE", "")
            
            if settings.RAZORPAY_WEBHOOK_SECRET:
                try:
                    razorpay_client.utility.verify_webhook_signature(
                        webhook_body.decode("utf-8"),
                        webhook_signature,
                        settings.RAZORPAY_WEBHOOK_SECRET
                    )
                except razorpay.errors.SignatureVerificationError:
                    return HttpResponseBadRequest("Invalid signature")
            
            event = json.loads(webhook_body)
            event_type = event.get("event")
            
            if event_type == "payment.captured":
                payment_entity = event["payload"]["payment"]["entity"]
                razorpay_order_id = payment_entity["order_id"]
                
                try:
                    payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
                    if payment.status != "success":
                        payment.razorpay_payment_id = payment_entity["id"]
                        payment.mark_as_success()
                except Payment.DoesNotExist:
                    pass
                    
            elif event_type == "payment.failed":
                payment_entity = event["payload"]["payment"]["entity"]
                razorpay_order_id = payment_entity["order_id"]
                
                try:
                    payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
                    reason = payment_entity.get("error_description", "Payment failed")
                    payment.mark_as_failed(reason)
                except Payment.DoesNotExist:
                    pass
            
            return JsonResponse({"status": "ok"})
            
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    
    return HttpResponseBadRequest()

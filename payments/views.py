from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment
from bookings.models import Booking, BookingLog
from bookings.services import allocate_booking_seats_atomic

@login_required
def demo_gateway_view(request, pnr):
    """
    Simulated Demo Payment Gateway. Explicitly labeled for MCA project examination.
    Allows examiner/user to simulate successful or failed payment outcomes.
    """
    booking = get_object_or_404(
        Booking.objects.prefetch_related('passengers', 'train'),
        pnr=pnr
    )
    if booking.user != request.user and not request.user.is_staff:
        messages.error(request, "Unauthorized access.")
        return redirect('core:home')

    if booking.status in ('CONFIRMED', 'WAITLISTED'):
        messages.info(request, f"Booking {booking.pnr} is already processed.")
        return redirect('bookings:ticket_detail', pnr=booking.pnr)

    if request.method == 'POST':
        action = request.POST.get('outcome', 'SUCCESS').strip().upper()
        payment_method = request.POST.get('payment_method', 'DEMO_MOCK')
        txn_id = Payment.generate_txn_id()

        if action == 'SUCCESS':
            # Create successful payment
            payment = Payment.objects.create(
                booking=booking,
                transaction_id=txn_id,
                amount=booking.total_fare,
                payment_method=payment_method,
                status='SUCCESS'
            )

            # Atomically allocate seats
            allocate_booking_seats_atomic(booking)

            BookingLog.objects.create(
                booking=booking,
                action='PAID',
                description=f"Demo payment successful. Txn ID: {txn_id}. Total: Rs. {booking.total_fare}"
            )

            # Simulated console email
            try:
                send_mail(
                    subject=f"RailConnect: Booking Confirmed (PNR: {booking.pnr})",
                    message=f"Dear {booking.user.username},\n\nYour payment of Rs. {booking.total_fare} was successful.\nPNR: {booking.pnr}\nTrain: {booking.train.train_number} - {booking.train.name}\nDate: {booking.journey_date}\n\nThank you for booking with RailConnect!",
                    from_email='tickets@railconnect.local',
                    recipient_list=[booking.contact_email],
                    fail_silently=True,
                )
            except Exception:
                pass

            messages.success(request, f"🎉 Payment of ₹{booking.total_fare} Successful! PNR {booking.pnr} has been generated.")
            return redirect('bookings:ticket_detail', pnr=booking.pnr)
        else:
            # Payment Failure Simulation
            failure_reason = request.POST.get('failure_reason', 'Simulated Insufficient Funds / Bank Network Timeout')
            payment = Payment.objects.create(
                booking=booking,
                transaction_id=txn_id,
                amount=booking.total_fare,
                payment_method=payment_method,
                status='FAILED',
                failure_reason=failure_reason
            )
            booking.status = 'FAILED'
            booking.save()

            BookingLog.objects.create(
                booking=booking,
                action='PAYMENT_FAILED',
                description=f"Demo payment declined. Txn ID: {txn_id}. Reason: {failure_reason}"
            )

            messages.error(request, f"Payment simulation failed: {failure_reason}")
            return redirect('payments:failure', pnr=booking.pnr)

    return render(request, 'payments/gateway.html', {
        'booking': booking,
    })

@login_required
def payment_failure_view(request, pnr):
    """Payment failure page with diagnostics and a retry button."""
    booking = get_object_or_404(Booking, pnr=pnr)
    if booking.user != request.user and not request.user.is_staff:
        messages.error(request, "Unauthorized access.")
        return redirect('core:home')

    payment = Payment.objects.filter(booking=booking, status='FAILED').order_by('-created_at').first()
    return render(request, 'payments/failure.html', {
        'booking': booking,
        'payment': payment,
    })

@login_required
def retry_payment_view(request, pnr):
    """Resets failed booking back to PENDING so user can retry."""
    booking = get_object_or_404(Booking, pnr=pnr, user=request.user)
    if booking.status == 'FAILED':
        booking.status = 'PENDING'
        booking.save()
    return redirect('payments:gateway', pnr=booking.pnr)

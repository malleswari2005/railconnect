from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from datetime import date, datetime
from decimal import Decimal

from bookings.models import Booking, Passenger, Cancellation, JourneyInventory, BookingLog
from bookings.services import cancel_booking_or_passengers
from trains.models import Train, Station

@login_required
def my_bookings_view(request):
    """
    Customer portal displaying current, past, and cancelled bookings
    with one-click access to ticket vouchers and cancellation.
    """
    today = date.today()
    bookings_qs = Booking.objects.filter(user=request.user).prefetch_related(
        'passengers', 'train', 'from_station', 'to_station', 'cancellations'
    ).order_by('-created_at')

    upcoming_bookings = [b for b in bookings_qs if b.journey_date >= today and b.status not in ('CANCELLED', 'FAILED')]
    past_bookings = [b for b in bookings_qs if b.journey_date < today and b.status not in ('CANCELLED', 'FAILED')]
    cancelled_bookings = [b for b in bookings_qs if b.status in ('CANCELLED', 'PARTIALLY_CANCELLED') or b.cancellations.exists()]

    return render(request, 'dashboard/my_bookings.html', {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'cancelled_bookings': cancelled_bookings,
        'total_count': bookings_qs.count(),
        'today': today,
    })

@login_required
def cancel_booking_view(request, pnr):
    """
    Handles cancellation preview with transparent refund tier calculation
    and executes atomic cancellation + waitlist auto-promotion.
    """
    booking = get_object_or_404(
        Booking.objects.prefetch_related('passengers', 'train', 'from_station', 'to_station'),
        pnr=pnr
    )
    if booking.user != request.user and not request.user.is_staff:
        messages.error(request, "Unauthorized access to this booking.")
        return redirect('dashboard:my_bookings')

    if booking.status in ('CANCELLED', 'FAILED'):
        messages.warning(request, "This booking has already been cancelled or is invalid.")
        return redirect('dashboard:my_bookings')

    # Calculate hours before departure for policy preview
    now_dt = timezone.now()
    dep_time = booking.train.departure_time or timezone.datetime.min.time()
    dep_dt = timezone.make_aware(
        datetime.combine(booking.journey_date, dep_time),
        timezone.get_current_timezone()
    )
    hours_before = max((dep_dt - now_dt).total_seconds() / 3600.0, 0)

    if hours_before > 48:
        refund_pct = 90
        clerkage_pct = 10
        tier_label = "> 48 Hours Before Departure (10% Clerkage Retained)"
    elif hours_before >= 12:
        refund_pct = 50
        clerkage_pct = 50
        tier_label = "12 to 48 Hours Before Departure (50% Deduction)"
    else:
        refund_pct = 0
        clerkage_pct = 100
        tier_label = "< 12 Hours Before Departure (Non-Refundable)"

    active_passengers = booking.passengers.filter(status__in=['CONFIRMED', 'WAITLISTED'])

    if request.method == 'POST':
        selected_p_ids = request.POST.getlist('passenger_ids')
        reason = request.POST.get('cancellation_reason', 'Voluntary Passenger Cancellation')

        if selected_p_ids:
            p_ids = [int(pid) for pid in selected_p_ids if pid.isdigit()]
        else:
            p_ids = None # Cancel all

        cancellation = cancel_booking_or_passengers(booking, passenger_ids=p_ids, reason=reason)

        if cancellation:
            messages.success(
                request,
                f"✅ Cancellation processed successfully! Demo refund of ₹{cancellation.refund_amount} has been credited. (Fee: ₹{cancellation.cancellation_fee})"
            )
        else:
            messages.error(request, "No active passengers were selected for cancellation.")

        return redirect('dashboard:my_bookings')

    return render(request, 'dashboard/cancel_confirm.html', {
        'booking': booking,
        'active_passengers': active_passengers,
        'hours_before': round(hours_before, 1),
        'refund_pct': refund_pct,
        'clerkage_pct': clerkage_pct,
        'tier_label': tier_label,
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from datetime import date
from core.decorators import tte_required
from bookings.models import Booking, Passenger
from .models import TTEAssignment, TicketCheck
from .services import create_audit_log

@tte_required
def tte_dashboard_view(request):
    """
    TTE Portal home: displays assigned trains for today, upcoming dates, and past journeys.
    """
    today = date.today()
    user = request.user

    # Superuser sees all assignments, TTE sees their own
    if user.is_superuser:
        assignments_qs = TTEAssignment.objects.all()
    else:
        assignments_qs = TTEAssignment.objects.filter(tte=user)

    assignments_qs = assignments_qs.select_related(
        'train', 'train__source_station', 'train__destination_station', 'tte'
    ).order_by('journey_date', 'train__train_number')

    today_assignments = [a for a in assignments_qs if a.journey_date == today]
    upcoming_assignments = [a for a in assignments_qs if a.journey_date > today]
    past_assignments = [a for a in assignments_qs if a.journey_date < today]

    return render(request, 'tte/dashboard.html', {
        'today': today,
        'today_assignments': today_assignments,
        'upcoming_assignments': upcoming_assignments,
        'past_assignments': past_assignments,
        'total_active': len(today_assignments) + len(upcoming_assignments),
    })


@tte_required
def tte_reservation_chart_view(request, assignment_id):
    """
    Reservation chart for an assigned train journey.
    Lists passengers coach-wise with verification status and check action.
    """
    assignment = get_object_or_404(
        TTEAssignment.objects.select_related(
            'train', 'train__source_station', 'train__destination_station', 'tte'
        ),
        id=assignment_id
    )

    if assignment.tte != request.user and not request.user.is_superuser:
        messages.error(request, "Access denied. This journey assignment is not assigned to your account.")
        return redirect('tte:tte_dashboard')

    # Fetch active bookings for this train and journey date
    bookings = Booking.objects.filter(
        train=assignment.train,
        journey_date=assignment.journey_date,
        status__in=['CONFIRMED', 'WAITLISTED', 'PARTIALLY_CANCELLED']
    ).select_related(
        'from_station', 'to_station', 'user'
    ).prefetch_related(
        'passengers', 'passengers__ticket_checks'
    ).order_by('pnr')

    coach_filter = request.GET.get('coach', '').strip()
    status_filter = request.GET.get('status', '').strip()

    passengers_list = []
    distinct_coaches = set()

    verified_count = 0
    absent_count = 0
    irregular_count = 0
    pending_count = 0

    for b in bookings:
        for p in b.passengers.all():
            if p.status == 'CANCELLED':
                continue
            if p.coach_number:
                distinct_coaches.add(p.coach_number)

            latest_check = p.ticket_checks.first()
            if latest_check:
                if latest_check.result == 'VERIFIED':
                    verified_count += 1
                elif latest_check.result == 'ABSENT':
                    absent_count += 1
                else:
                    irregular_count += 1
            else:
                pending_count += 1

            p_data = {
                'passenger': p,
                'booking': b,
                'latest_check': latest_check,
            }

            # Filter conditions
            if coach_filter and p.coach_number != coach_filter:
                continue
            if status_filter:
                if status_filter == 'PENDING' and latest_check is not None:
                    continue
                elif status_filter == 'CHECKED' and latest_check is None:
                    continue
                elif status_filter in ['VERIFIED', 'ABSENT', 'IRREGULAR', 'WRONG_ID']:
                    if not latest_check or latest_check.result != status_filter:
                        continue

            passengers_list.append(p_data)

    sorted_coaches = sorted(list(distinct_coaches))

    return render(request, 'tte/reservation_chart.html', {
        'assignment': assignment,
        'passengers_list': passengers_list,
        'total_passengers': len(passengers_list),
        'sorted_coaches': sorted_coaches,
        'selected_coach': coach_filter,
        'selected_status': status_filter,
        'verified_count': verified_count,
        'absent_count': absent_count,
        'irregular_count': irregular_count,
        'pending_count': pending_count,
    })


@tte_required
@require_POST
def tte_check_passenger_view(request):
    """
    Records a ticket check event.
    CRITICAL: Never modifies Booking.status or Passenger.status!
    """
    assignment_id = request.POST.get('assignment_id')
    passenger_id = request.POST.get('passenger_id')
    result = request.POST.get('result', 'VERIFIED')
    remarks = request.POST.get('remarks', '').strip()
    next_url = request.POST.get('next_url')

    assignment = get_object_or_404(TTEAssignment, id=assignment_id)
    if assignment.tte != request.user and not request.user.is_superuser:
        messages.error(request, "Unauthorized. You cannot check tickets for a journey not assigned to you.")
        return redirect('tte:tte_dashboard')

    passenger = get_object_or_404(
        Passenger.objects.select_related('booking', 'booking__train'),
        id=passenger_id
    )

    # Verify passenger belongs to the assigned train and date
    if (passenger.booking.train != assignment.train or
        passenger.booking.journey_date != assignment.journey_date):
        messages.error(request, "Passenger does not belong to this assigned train journey.")
        return redirect('tte:tte_chart', assignment_id=assignment.id)

    # Create immutable TicketCheck (DO NOT alter passenger.status or booking.status)
    ticket_check = TicketCheck.objects.create(
        passenger=passenger,
        booking=passenger.booking,
        tte=request.user,
        result=result,
        remarks=remarks
    )

    create_audit_log(
        actor=request.user,
        action='TICKET_CHECKED',
        object_repr=f"Passenger {passenger.name} (PNR: {passenger.booking.pnr})",
        details=f"Result: {ticket_check.get_result_display()}. Remarks: {remarks or 'None'}"
    )

    messages.success(
        request,
        f"Recorded verification for {passenger.name} (Seat {passenger.coach_number or '-'}/{passenger.seat_number or '-'}): {ticket_check.get_result_display()}."
    )

    if next_url:
        return redirect(next_url)
    return redirect('tte:tte_chart', assignment_id=assignment.id)


@tte_required
def tte_pnr_lookup_view(request):
    """
    PNR lookup restricted strictly to journeys assigned to the requesting TTE.
    If not assigned: shows clear error 'Journey not assigned to you.'
    """
    query = request.GET.get('pnr', '').strip().upper()
    booking = None
    passengers_with_checks = []
    error_message = None
    matched_assignment = None

    if query:
        booking = Booking.objects.filter(pnr=query).select_related(
            'train', 'train__source_station', 'train__destination_station', 'from_station', 'to_station'
        ).prefetch_related('passengers', 'passengers__ticket_checks').first()

        if not booking:
            error_message = f"PNR '{query}' not found in the reservation system."
        else:
            # Check assignment
            if request.user.is_superuser:
                matched_assignment = TTEAssignment.objects.filter(
                    train=booking.train, journey_date=booking.journey_date
                ).first()
                is_assigned = True
            else:
                matched_assignment = TTEAssignment.objects.filter(
                    tte=request.user, train=booking.train, journey_date=booking.journey_date
                ).first()
                is_assigned = matched_assignment is not None

            if not is_assigned:
                error_message = "Journey not assigned to you."
                booking = None
            else:
                for p in booking.passengers.all():
                    passengers_with_checks.append({
                        'passenger': p,
                        'latest_check': p.ticket_checks.first()
                    })

    return render(request, 'tte/pnr_lookup.html', {
        'query': query,
        'booking': booking,
        'error_message': error_message,
        'matched_assignment': matched_assignment,
        'passengers_with_checks': passengers_with_checks,
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count, Q, Avg
from decimal import Decimal
from datetime import date, datetime, timedelta

from core.decorators import admin_required, get_user_role
from trains.models import Train, Station
from bookings.models import Booking, Passenger, Cancellation, JourneyInventory
from payments.models import Payment
from .models import TTEAssignment, AuditLog
from .services import create_audit_log

@admin_required
def admin_dashboard_view(request):
    """
    Administrator Control Tower:
    System-wide overview of operations, users, fleet, test revenue, and recent audit activity.
    """
    total_users = User.objects.count()
    total_staff = User.objects.filter(groups__name__in=['TTE', 'Operations', 'Admin']).distinct().count()
    total_bookings = Booking.objects.count()
    total_passengers = Passenger.objects.count()
    active_trains = Train.objects.filter(is_active=True).count()
    active_assignments = TTEAssignment.objects.filter(journey_date__gte=date.today()).count()

    # Revenue
    rev_agg = Booking.objects.filter(status__in=['CONFIRMED', 'WAITLISTED', 'PARTIALLY_CANCELLED']).aggregate(
        rev=Sum('total_fare')
    )
    total_revenue = rev_agg['rev'] or Decimal('0.00')

    ref_agg = Cancellation.objects.aggregate(ref=Sum('refund_amount'))
    total_refunds = ref_agg['ref'] or Decimal('0.00')
    net_revenue = total_revenue - total_refunds

    # Bookings by status
    confirmed_count = Booking.objects.filter(status='CONFIRMED').count()
    waitlist_count = Booking.objects.filter(status='WAITLISTED').count()
    cancelled_count = Booking.objects.filter(status__in=['CANCELLED', 'PARTIALLY_CANCELLED']).count()

    recent_logs = AuditLog.objects.select_related('actor').order_by('-created_at')[:8]
    recent_bookings = Booking.objects.select_related('user', 'train', 'from_station', 'to_station').order_by('-created_at')[:8]

    return render(request, 'admin_portal/dashboard.html', {
        'total_users': total_users,
        'total_staff': total_staff,
        'total_bookings': total_bookings,
        'total_passengers': total_passengers,
        'active_trains': active_trains,
        'active_assignments': active_assignments,
        'total_revenue': total_revenue,
        'total_refunds': total_refunds,
        'net_revenue': net_revenue,
        'confirmed_count': confirmed_count,
        'waitlist_count': waitlist_count,
        'cancelled_count': cancelled_count,
        'recent_logs': recent_logs,
        'recent_bookings': recent_bookings,
    })


@admin_required
def admin_users_view(request):
    """
    Directory of all platform users with role filtering and staff creation link.
    """
    query = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '').strip()

    users_qs = User.objects.prefetch_related('groups').order_by('-date_joined')

    if query:
        users_qs = users_qs.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    users_list = []
    for u in users_qs:
        role = get_user_role(u)
        if role_filter and role != role_filter:
            continue
        users_list.append({
            'user': u,
            'role': role,
        })

    return render(request, 'admin_portal/users.html', {
        'users_list': users_list[:100],
        'total_count': len(users_list),
        'query': query,
        'selected_role': role_filter,
    })


@admin_required
def admin_create_staff_view(request):
    """
    Creates a new TTE or Operations staff user.
    Strictly validates password against Django's configured password validators.
    Never assigns is_staff or is_superuser to TTE or Operations accounts.
    """
    allowed_roles = ['TTE', 'Operations']

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        role = request.POST.get('role', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password:
            messages.error(request, "Username, email, and password are required.")
            return render(request, 'admin_portal/user_create.html', {'roles': allowed_roles})

        if role not in allowed_roles:
            messages.error(request, f"Invalid role selection. Must be one of: {', '.join(allowed_roles)}.")
            return render(request, 'admin_portal/user_create.html', {'roles': allowed_roles})

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'admin_portal/user_create.html', {'roles': allowed_roles})

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, f"Username '{username}' is already taken.")
            return render(request, 'admin_portal/user_create.html', {'roles': allowed_roles})

        # Strict Django Password Validation
        dummy_user = User(username=username, email=email)
        try:
            validate_password(password, user=dummy_user)
        except ValidationError as e:
            for msg in e.messages:
                messages.error(request, f"Password security issue: {msg}")
            return render(request, 'admin_portal/user_create.html', {'roles': allowed_roles})

        # Create user with is_staff=False, is_superuser=False
        new_user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=False,
            is_superuser=False,
        )

        # Assign to Role Group
        target_group, _ = Group.objects.get_or_create(name=role)
        new_user.groups.add(target_group)

        # Update profile
        if hasattr(new_user, 'profile'):
            if phone_number:
                new_user.profile.phone_number = phone_number
            new_user.profile.save()

        create_audit_log(
            actor=request.user,
            action='STAFF_USER_CREATED',
            object_repr=f"User {new_user.username} ({role})",
            details=f"Email: {email}, Name: {first_name} {last_name}, Role: {role}"
        )

        messages.success(request, f"Staff account for {new_user.username} ({role}) created successfully.")
        return redirect('admin_portal:admin_users')

    return render(request, 'admin_portal/user_create.html', {
        'roles': allowed_roles,
    })


@admin_required
def admin_assignments_view(request):
    """
    Manage TTE duty rosters: assign TTEs to train services and dates, view and remove assignments.
    """
    today = date.today()

    if request.method == 'POST':
        tte_id = request.POST.get('tte_id')
        train_id = request.POST.get('train_id')
        journey_date_str = request.POST.get('journey_date')

        tte_user = get_object_or_404(User, id=tte_id)
        train = get_object_or_404(Train, id=train_id)

        try:
            journey_date = datetime.strptime(journey_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, "Valid journey date is required.")
            return redirect('admin_portal:admin_assignments')

        # Check if already assigned
        existing = TTEAssignment.objects.filter(tte=tte_user, train=train, journey_date=journey_date).first()
        if existing:
            messages.warning(request, f"Officer {tte_user.username} is already assigned to Train #{train.train_number} on {journey_date}.")
        else:
            assignment = TTEAssignment.objects.create(
                tte=tte_user,
                train=train,
                journey_date=journey_date
            )
            create_audit_log(
                actor=request.user,
                action='TTE_ASSIGNED',
                object_repr=f"{tte_user.username} to Train {train.train_number}",
                details=f"Date: {journey_date}"
            )
            messages.success(request, f"Successfully assigned {tte_user.username} to Train #{train.train_number} ({train.name}) for {journey_date}.")

        return redirect('admin_portal:admin_assignments')

    assignments_qs = TTEAssignment.objects.select_related(
        'tte', 'train', 'train__source_station', 'train__destination_station'
    ).order_by('-journey_date', 'train__train_number')

    tte_officers = User.objects.filter(groups__name='TTE').order_by('first_name', 'username')
    trains = Train.objects.filter(is_active=True).order_by('train_number')

    return render(request, 'admin_portal/assignments.html', {
        'assignments': assignments_qs[:100],
        'tte_officers': tte_officers,
        'trains': trains,
        'today': today,
    })


@admin_required
@require_POST
def admin_delete_assignment_view(request, assignment_id):
    """
    Removes a TTE duty assignment.
    """
    assignment = get_object_or_404(TTEAssignment, id=assignment_id)
    info = f"{assignment.tte.username} - Train {assignment.train.train_number} on {assignment.journey_date}"
    assignment.delete()

    create_audit_log(
        actor=request.user,
        action='TTE_ASSIGNMENT_DELETED',
        object_repr=info,
        details="Assignment revoked by admin"
    )

    messages.info(request, f"TTE Assignment ({info}) has been removed.")
    return redirect('admin_portal:admin_assignments')


@admin_required
def admin_bookings_view(request):
    """
    System-wide booking search by PNR, passenger name, journey date, or train number.
    """
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    date_filter = request.GET.get('date', '').strip()

    bookings_qs = Booking.objects.select_related(
        'user', 'train', 'from_station', 'to_station'
    ).prefetch_related('passengers', 'cancellations').order_by('-created_at')

    if query:
        bookings_qs = bookings_qs.filter(
            Q(pnr__icontains=query) |
            Q(train__train_number__icontains=query) |
            Q(train__name__icontains=query) |
            Q(passengers__name__icontains=query) |
            Q(user__username__icontains=query)
        ).distinct()

    if status_filter:
        bookings_qs = bookings_qs.filter(status=status_filter)

    if date_filter:
        try:
            parsed_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            bookings_qs = bookings_qs.filter(journey_date=parsed_date)
        except ValueError:
            pass

    return render(request, 'admin_portal/bookings.html', {
        'bookings': bookings_qs[:100],
        'total_count': bookings_qs.count(),
        'query': query,
        'status_filter': status_filter,
        'date_filter': date_filter,
    })


@admin_required
def admin_payments_view(request):
    """
    Payment transaction audit log with test mode identifiers and linked PNRs.
    """
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    payments_qs = Payment.objects.select_related(
        'booking', 'booking__user', 'booking__train'
    ).order_by('-created_at')

    if query:
        payments_qs = payments_qs.filter(
            Q(transaction_id__icontains=query) |
            Q(booking__pnr__icontains=query) |
            Q(booking__user__username__icontains=query)
        )

    if status_filter:
        payments_qs = payments_qs.filter(status=status_filter)

    return render(request, 'admin_portal/payments.html', {
        'payments': payments_qs[:100],
        'total_count': payments_qs.count(),
        'query': query,
        'status_filter': status_filter,
    })


@admin_required
def admin_reports_view(request):
    """
    Operational analytics: revenue breakdown, class distribution, occupancy estimates,
    and waitlist conversion metrics.
    """
    today = date.today()

    # Revenue by Class
    class_revenue = Booking.objects.filter(
        status__in=['CONFIRMED', 'WAITLISTED', 'PARTIALLY_CANCELLED']
    ).values('class_code').annotate(
        total_rev=Sum('total_fare'),
        booking_count=Count('id')
    ).order_by('-total_rev')

    # Top Trains by Bookings
    train_popularity = Booking.objects.values(
        'train__train_number', 'train__name'
    ).annotate(
        booking_count=Count('id'),
        total_rev=Sum('total_fare')
    ).order_by('-booking_count')[:10]

    # Waitlist conversion metrics
    total_confirmed_passengers = Passenger.objects.filter(status='CONFIRMED').count()
    total_waitlisted_passengers = Passenger.objects.filter(status='WAITLISTED').count()
    total_cancelled_passengers = Passenger.objects.filter(status='CANCELLED').count()

    total_passengers = total_confirmed_passengers + total_waitlisted_passengers + total_cancelled_passengers
    wl_ratio = round((total_waitlisted_passengers / total_passengers * 100), 1) if total_passengers > 0 else 0
    confirmed_ratio = round((total_confirmed_passengers / total_passengers * 100), 1) if total_passengers > 0 else 0

    return render(request, 'admin_portal/reports.html', {
        'class_revenue': class_revenue,
        'train_popularity': train_popularity,
        'total_confirmed_passengers': total_confirmed_passengers,
        'total_waitlisted_passengers': total_waitlisted_passengers,
        'total_cancelled_passengers': total_cancelled_passengers,
        'wl_ratio': wl_ratio,
        'confirmed_ratio': confirmed_ratio,
        'today': today,
    })


@admin_required
def admin_audit_logs_view(request):
    """
    System-wide immutable audit trail of staff actions across TTE, Operations, and Admin portals.
    """
    action_filter = request.GET.get('action', '').strip()
    actor_query = request.GET.get('actor', '').strip()

    logs_qs = AuditLog.objects.select_related('actor').order_by('-created_at')

    if action_filter:
        logs_qs = logs_qs.filter(action=action_filter)
    if actor_query:
        logs_qs = logs_qs.filter(actor__username__icontains=actor_query)

    distinct_actions = AuditLog.objects.values_list('action', flat=True).distinct()

    return render(request, 'admin_portal/audit_logs.html', {
        'logs': logs_qs[:150],
        'total_count': logs_qs.count(),
        'distinct_actions': distinct_actions,
        'selected_action': action_filter,
        'actor_query': actor_query,
    })

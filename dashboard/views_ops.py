from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from datetime import date, datetime
from core.decorators import operations_required
from trains.models import Train, Station
from .models import TrainStatusUpdate, OperationalNotice
from .services import create_audit_log

@operations_required
def ops_dashboard_view(request):
    """
    Operations Control Center Dashboard:
    Live status overview of all running trains, operational updates, and active system alerts.
    """
    today = date.today()
    trains_qs = Train.objects.filter(is_active=True).select_related(
        'source_station', 'destination_station'
    ).prefetch_related('status_updates', 'stops__station').order_by('train_number')

    train_data = []
    on_time_count = 0
    delayed_count = 0
    cancelled_count = 0
    diverted_count = 0

    for t in trains_qs:
        latest = t.status_updates.filter(journey_date=today).order_by('-updated_at').first()
        status_code = latest.status if latest else 'ON_TIME'
        delay_mins = latest.delay_minutes if latest else 0

        if status_code == 'ON_TIME':
            on_time_count += 1
        elif status_code == 'DELAYED':
            delayed_count += 1
        elif status_code == 'CANCELLED':
            cancelled_count += 1
        elif status_code in ['DIVERTED', 'RESCHEDULED']:
            diverted_count += 1

        train_data.append({
            'train': t,
            'latest_update': latest,
            'effective_status': status_code,
            'delay_minutes': delay_mins,
        })

    active_notices = OperationalNotice.objects.all().select_related('posted_by').order_by('-is_active', '-created_at')[:10]
    stations = Station.objects.all().order_by('name')

    return render(request, 'operations/dashboard.html', {
        'today': today,
        'train_data': train_data,
        'total_trains': len(train_data),
        'on_time_count': on_time_count,
        'delayed_count': delayed_count,
        'cancelled_count': cancelled_count,
        'diverted_count': diverted_count,
        'active_notices': active_notices,
        'stations': stations,
    })


@operations_required
@require_POST
def ops_update_status_view(request):
    """
    Broadcasts a new real-time train status update.
    Directly feeds into passenger-facing /trains/live-status/.
    """
    train_id = request.POST.get('train_id')
    current_station_id = request.POST.get('current_station_id')
    status = request.POST.get('status', 'ON_TIME')
    delay_minutes = request.POST.get('delay_minutes', '0')
    remarks = request.POST.get('remarks', '').strip()
    journey_date_str = request.POST.get('journey_date')

    train = get_object_or_404(Train, id=train_id)
    station = get_object_or_404(Station, id=current_station_id)

    if journey_date_str:
        try:
            journey_date = datetime.strptime(journey_date_str, '%Y-%m-%d').date()
        except ValueError:
            journey_date = date.today()
    else:
        journey_date = date.today()

    try:
        delay_int = max(int(delay_minutes), 0)
    except (ValueError, TypeError):
        delay_int = 0

    update = TrainStatusUpdate.objects.create(
        train=train,
        journey_date=journey_date,
        current_station=station,
        status=status,
        delay_minutes=delay_int,
        updated_by=request.user,
        remarks=remarks
    )

    create_audit_log(
        actor=request.user,
        action='TRAIN_STATUS_UPDATED',
        object_repr=f"Train {train.train_number} ({journey_date})",
        details=f"Status: {update.get_status_display()}, Station: {station.code}, Delay: {delay_int}m, Remarks: {remarks}"
    )

    messages.success(
        request,
        f"Broadcasted status update for Train #{train.train_number} ({train.name}): {update.get_status_display()} at {station.name}."
    )
    return redirect('operations:ops_dashboard')


@operations_required
def ops_history_view(request):
    """
    Searchable audit trail and history of all operational updates.
    """
    train_query = request.GET.get('train', '').strip()
    date_query = request.GET.get('date', '').strip()

    updates_qs = TrainStatusUpdate.objects.select_related(
        'train', 'current_station', 'updated_by'
    ).order_by('-created_at')

    if train_query:
        updates_qs = updates_qs.filter(train__train_number__icontains=train_query)
    if date_query:
        try:
            parsed_date = datetime.strptime(date_query, '%Y-%m-%d').date()
            updates_qs = updates_qs.filter(journey_date=parsed_date)
        except ValueError:
            pass

    return render(request, 'operations/history.html', {
        'updates': updates_qs[:100],
        'train_query': train_query,
        'date_query': date_query,
        'total_count': updates_qs.count(),
    })


@operations_required
@require_POST
def ops_create_notice_view(request):
    """
    Publishes a new operational broadcast notice.
    """
    title = request.POST.get('title', '').strip()
    message = request.POST.get('message', '').strip()
    priority = request.POST.get('priority', 'NORMAL')

    if not title or not message:
        messages.error(request, "Title and message are required to issue an operational notice.")
        return redirect('operations:ops_dashboard')

    notice = OperationalNotice.objects.create(
        title=title,
        message=message,
        priority=priority,
        is_active=True,
        posted_by=request.user
    )

    create_audit_log(
        actor=request.user,
        action='OPERATIONAL_NOTICE_CREATED',
        object_repr=f"Notice: {title}",
        details=f"Priority: {priority}. Content: {message[:100]}"
    )

    messages.success(request, f"Operational notice '{title}' published successfully.")
    return redirect('operations:ops_dashboard')


@operations_required
@require_POST
def ops_toggle_notice_view(request, notice_id):
    """
    Toggles the active state of an operational notice.
    """
    notice = get_object_or_404(OperationalNotice, id=notice_id)
    notice.is_active = not notice.is_active
    notice.save()

    state_str = "activated" if notice.is_active else "archived"
    create_audit_log(
        actor=request.user,
        action='OPERATIONAL_NOTICE_TOGGLED',
        object_repr=f"Notice: {notice.title}",
        details=f"Notice {state_str}."
    )

    messages.info(request, f"Notice '{notice.title}' has been {state_str}.")
    return redirect('operations:ops_dashboard')

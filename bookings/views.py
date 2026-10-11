from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.utils import timezone
from datetime import datetime, date
from decimal import Decimal
import io
import qrcode

# ReportLab imports for PDF Generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from .models import Booking, Passenger, JourneyInventory, AllocatedJourneySeat, BookingLog
from .services import (
    generate_unique_pnr,
    get_or_create_inventory,
    calculate_fare,
    allocate_booking_seats_atomic,
)
from .forms import PassengerEntryForm, BookingContactForm, PassengerFormSet
from trains.models import Train, Station, TrainClass

@login_required
def booking_new_view(request):
    """Initializes new booking and accepts passenger entries (1-6 passengers)."""
    train_number = request.GET.get('train', '').strip()
    class_code = request.GET.get('class_code', '').strip()
    date_str = request.GET.get('journey_date', '').strip()
    from_code = request.GET.get('from_station', '').strip()
    to_code = request.GET.get('to_station', '').strip()

    if not all([train_number, class_code, date_str, from_code, to_code]):
        messages.error(request, "Missing required booking details. Please search trains first.")
        return redirect('core:home')

    try:
        journey_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, "Invalid journey date.")
        return redirect('core:home')

    train = get_object_or_404(Train, train_number=train_number, is_active=True)
    from_station = get_object_or_404(Station, code=from_code)
    to_station = get_object_or_404(Station, code=to_code)

    # Ensure inventory exists
    inventory = get_or_create_inventory(train, journey_date, class_code)
    single_fare, distance_km = calculate_fare(train, class_code, from_station, to_station)

    # Pre-fill contact info from user profile
    initial_contact = {
        'contact_email': request.user.email or f"{request.user.username}@example.com",
        'contact_phone': getattr(request.user.profile, 'phone_number', '') or '9876543210'
    }

    if request.method == 'POST':
        contact_form = BookingContactForm(request.POST)
        formset = PassengerFormSet(request.POST)

        if contact_form.is_valid() and formset.is_valid():
            passengers_data = [f.cleaned_data for f in formset if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]

            if not passengers_data:
                messages.error(request, "Please add at least one passenger.")
            elif len(passengers_data) > 6:
                messages.error(request, "A maximum of 6 passengers is permitted per booking.")
            else:
                passenger_count = len(passengers_data)
                total_fare = single_fare * Decimal(passenger_count)

                # Generate PNR and create Pending Booking
                pnr = generate_unique_pnr()
                booking = Booking.objects.create(
                    pnr=pnr,
                    user=request.user,
                    train=train,
                    from_station=from_station,
                    to_station=to_station,
                    journey_date=journey_date,
                    class_code=class_code,
                    status='PENDING',
                    total_fare=total_fare,
                    contact_email=contact_form.cleaned_data['contact_email'],
                    contact_phone=contact_form.cleaned_data['contact_phone']
                )

                # Create passenger records
                for p_data in passengers_data:
                    Passenger.objects.create(
                        booking=booking,
                        name=p_data['name'],
                        age=p_data['age'],
                        gender=p_data['gender'],
                        berth_preference=p_data.get('berth_preference', 'NONE'),
                        fare=single_fare,
                        status='CONFIRMED'
                    )

                BookingLog.objects.create(
                    booking=booking,
                    action='CREATED',
                    description=f"Draft booking created for {passenger_count} passenger(s). Pending payment."
                )

                return redirect('bookings:review', pnr=booking.pnr)
        else:
            messages.error(request, "Please correct the passenger details.")
    else:
        contact_form = BookingContactForm(initial=initial_contact)
        # Default with 1 passenger (logged-in user's name)
        initial_passenger = [{
            'name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'age': 28,
            'gender': 'M',
            'berth_preference': 'NONE'
        }]
        formset = PassengerFormSet(initial=initial_passenger)

    return render(request, 'bookings/booking_form.html', {
        'train': train,
        'from_station': from_station,
        'to_station': to_station,
        'journey_date': journey_date,
        'date_str': date_str,
        'class_code': class_code,
        'inventory': inventory,
        'single_fare': single_fare,
        'distance_km': distance_km,
        'contact_form': contact_form,
        'formset': formset,
    })

@login_required
def booking_review_view(request, pnr):
    """Pre-payment review summary page."""
    booking = get_object_or_404(
        Booking.objects.prefetch_related('passengers'),
        pnr=pnr,
        user=request.user
    )
    passengers = booking.passengers.all()
    inventory = get_or_create_inventory(booking.train, booking.journey_date, booking.class_code)

    return render(request, 'bookings/review.html', {
        'booking': booking,
        'passengers': passengers,
        'inventory': inventory,
    })

def pnr_lookup_view(request):
    """
    Public sanitized PNR inquiry (zero privacy leakage: masks phone/email, shows only seat & status).
    """
    pnr_query = request.GET.get('pnr', '').strip()
    booking = None

    if pnr_query:
        booking = Booking.objects.filter(pnr=pnr_query).prefetch_related('passengers', 'train').first()
        if not booking:
            messages.error(request, f"No booking found for PNR: {pnr_query}. Please check the 10-digit number.")

    return render(request, 'bookings/pnr_lookup.html', {
        'pnr_query': pnr_query,
        'booking': booking,
    })

@login_required
def ticket_detail_view(request, pnr):
    """Private e-ticket view with boarding pass layout and QR verification code."""
    booking = get_object_or_404(
        Booking.objects.prefetch_related('passengers__allocated_seat__coach', 'train', 'from_station', 'to_station'),
        pnr=pnr
    )
    # Ownership guard (unless staff)
    if booking.user != request.user and not request.user.is_staff:
        raise Http404("You are not authorized to view this booking.")

    # Generate QR Code image base64 or inline data
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    verify_url = request.build_absolute_uri(f"/bookings/pnr-lookup/?pnr={booking.pnr}")
    qr.add_data(verify_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    import base64
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render(request, 'bookings/ticket_detail.html', {
        'booking': booking,
        'passengers': booking.passengers.all(),
        'qr_base64': qr_base64,
    })

@login_required
def ticket_pdf_view(request, pnr):
    """Generates official downloadable PDF e-ticket using ReportLab."""
    booking = get_object_or_404(
        Booking.objects.prefetch_related('passengers__allocated_seat__coach', 'train', 'from_station', 'to_station'),
        pnr=pnr
    )
    if booking.user != request.user and not request.user.is_staff:
        raise Http404("Unauthorized")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    # Title Banner
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#0b2545'),
        alignment=1, # Center
        spaceAfter=10
    )
    story.append(Paragraph("<b>RailConnect Electronic Reservation Slip (ERS)</b>", title_style))
    story.append(Paragraph(f"PNR: <b>{booking.pnr}</b> | Status: <b>{booking.get_status_display()}</b>", ParagraphStyle('Sub', alignment=1, fontSize=12, textColor=colors.HexColor('#ff7a00'))))
    story.append(Spacer(1, 15))

    # Journey Details Table
    journey_data = [
        ['Train Number & Name:', f"{booking.train.train_number} - {booking.train.name}", 'Booking Date:', booking.created_at.strftime('%d-%b-%Y %H:%M')],
        ['From Station:', f"{booking.from_station.name} ({booking.from_station.code})", 'To Station:', f"{booking.to_station.name} ({booking.to_station.code})"],
        ['Date of Journey:', booking.journey_date.strftime('%d-%b-%Y'), 'Class:', booking.class_code],
        ['Total Fare:', f"Rs. {booking.total_fare}", 'Booked By:', booking.user.username],
    ]
    t_journey = Table(journey_data, colWidths=[130, 160, 100, 150])
    t_journey.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0b2545')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    story.append(t_journey)
    story.append(Spacer(1, 15))

    # Passenger Table
    passenger_header = ['#', 'Passenger Name', 'Age', 'Gender', 'Booking Status', 'Coach / Seat']
    passenger_rows = [passenger_header]
    for idx, p in enumerate(booking.passengers.all(), start=1):
        seat_desc = f"{p.allocated_seat.coach.coach_code}/{p.allocated_seat.seat_number} ({p.allocated_seat.get_berth_type_display()})" if p.allocated_seat else f"Waitlist #{p.waitlist_number}"
        passenger_rows.append([str(idx), p.name, str(p.age), p.get_gender_display(), p.get_status_display(), seat_desc])

    t_passengers = Table(passenger_rows, colWidths=[25, 170, 45, 55, 110, 135])
    t_passengers.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0b2545')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#94a3b8')),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (3, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_passengers)
    story.append(Spacer(1, 20))

    # Important Instructions
    notice_text = """
    <b>Important Instructions for Passengers:</b><br/>
    1. One passenger in the ticket must carry original Government ID proof (Aadhaar, Passport, Driving License, PAN).<br/>
    2. Educational Demo System: This ticket is generated for educational evaluation purposes.<br/>
    3. Cancellation Refund Policy: >48 hrs before departure: 90% refund; 12-48 hrs: 50% refund; <12 hrs: non-refundable.
    """
    story.append(Paragraph(notice_text, ParagraphStyle('Notice', fontSize=8, textColor=colors.HexColor('#475569'), leading=11)))

    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="RailConnect_Ticket_{booking.pnr}.pdf"'
    return response

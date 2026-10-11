import random
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import Coach, Seat, JourneyInventory, Booking, Passenger, AllocatedJourneySeat, WaitlistEntry, BookingLog
from trains.models import Train, TrainStop, TrainClass

def generate_unique_pnr():
    """Generates a unique 10-digit numeric PNR code."""
    while True:
        # 10-digit number not starting with 0
        pnr = str(random.randint(2000000000, 9999999999))
        if not Booking.objects.filter(pnr=pnr).exists():
            return pnr

def get_or_create_coaches_and_seats(train, class_code):
    """Ensures coaches and physical seats exist for the train and class."""
    tc = TrainClass.objects.filter(train=train, class_code=class_code).first()
    coaches_count = tc.total_coaches if tc else 2
    seats_per_coach = tc.seats_per_coach if tc else 72

    coach_prefix_map = {
        '1A': 'H',
        '2A': 'A',
        '3A': 'B',
        'SL': 'S',
        'CC': 'C',
        '2S': 'D',
    }
    prefix = coach_prefix_map.get(class_code, 'B')

    coaches = []
    for c_idx in range(1, coaches_count + 1):
        c_code = f"{prefix}{c_idx}"
        coach, created = Coach.objects.get_or_create(
            train=train,
            coach_code=c_code,
            defaults={'travel_class': class_code, 'total_seats': seats_per_coach}
        )
        coaches.append(coach)

        if created or coach.seats.count() < seats_per_coach:
            # Generate seats with standard layout
            existing_seat_numbers = set(coach.seats.values_list('seat_number', flat=True))
            seats_to_create = []
            for s_num in range(1, seats_per_coach + 1):
                if s_num in existing_seat_numbers:
                    continue
                # Determine berth type by standard 8-berth modulo pattern in Indian coaches
                mod = s_num % 8
                if mod in (1, 4):
                    b_type = 'LOWER'
                elif mod in (2, 5):
                    b_type = 'MIDDLE'
                elif mod in (3, 6):
                    b_type = 'UPPER'
                elif mod == 7:
                    b_type = 'SIDE_LOWER'
                else:
                    b_type = 'SIDE_UPPER'

                if class_code in ('CC', '2S'):
                    b_type = 'WINDOW' if (s_num % 3 == 1) else 'AISLE'

                seats_to_create.append(Seat(coach=coach, seat_number=s_num, berth_type=b_type))
            if seats_to_create:
                Seat.objects.bulk_create(seats_to_create)

    return coaches

def get_or_create_inventory(train, journey_date, class_code):
    """Fetches or initializes the JourneyInventory for the given train, date, and class."""
    # Ensure physical coaches exist
    get_or_create_coaches_and_seats(train, class_code)

    tc = TrainClass.objects.filter(train=train, class_code=class_code).first()
    total_capacity = (tc.total_seats if tc else 72)

    inventory, created = JourneyInventory.objects.get_or_create(
        train=train,
        journey_date=journey_date,
        class_code=class_code,
        defaults={
            'total_seats': total_capacity,
            'booked_seats': 0,
            'available_seats': total_capacity,
            'waitlist_count': 0,
            'max_waitlist': 50,
            'is_booking_open': True,
        }
    )
    return inventory

def calculate_fare(train, class_code, from_station, to_station):
    """Calculates single passenger fare for the given stations and travel class."""
    stops = list(train.stops.filter(station__in=[from_station, to_station]))
    from_stop = next((s for s in stops if s.station_id == from_station.id), None)
    to_stop = next((s for s in stops if s.station_id == to_station.id), None)

    distance_km = 300 # fallback default
    if from_stop and to_stop:
        distance_km = max(abs(to_stop.distance_from_source_km - from_stop.distance_from_source_km), 50)

    tc = TrainClass.objects.filter(train=train, class_code=class_code).first()
    if tc:
        base = float(tc.base_fare)
        rate = float(tc.per_km_rate)
    else:
        base = 250.0
        rate = 1.20

    fare = base + (rate * distance_km)
    # Add superfast charge if train is superfast/rajdhani
    if train.train_type in ('RAJDHANI', 'SHATABDI', 'VANDE_BHARAT'):
        fare += 75.0
    elif train.train_type == 'SUPERFAST':
        fare += 45.0

    return Decimal(str(round(fare, 2))), distance_km

def allocate_booking_seats_atomic(booking):
    """
    Executes concurrency-safe seat allocation inside transaction.atomic with select_for_update.
    Allocates seats or moves overflow passengers to waitlist.
    """
    with transaction.atomic():
        # 1. Lock the inventory row to prevent concurrent race conditions
        inventory = JourneyInventory.objects.select_for_update().get(
            train=booking.train,
            journey_date=booking.journey_date,
            class_code=booking.class_code
        )

        passengers = list(booking.passengers.all())
        has_waitlist = False
        has_confirmed = False

        for passenger in passengers:
            if inventory.available_seats > 0:
                # Find available physical seat
                # Seat must not have an AllocatedJourneySeat on this journey_date
                occupied_seat_ids = AllocatedJourneySeat.objects.filter(
                    journey_date=booking.journey_date,
                    seat__coach__train=booking.train,
                    seat__coach__travel_class=booking.class_code
                ).values_list('seat_id', flat=True)

                candidate_seat = Seat.objects.filter(
                    coach__train=booking.train,
                    coach__travel_class=booking.class_code
                ).exclude(id__in=occupied_seat_ids).first()

                if candidate_seat:
                    # Create seat lock record
                    AllocatedJourneySeat.objects.create(
                        seat=candidate_seat,
                        journey_date=booking.journey_date,
                        passenger=passenger,
                        booking=booking
                    )
                    passenger.allocated_seat = candidate_seat
                    passenger.status = 'CONFIRMED'
                    passenger.save()

                    inventory.available_seats -= 1
                    inventory.booked_seats += 1
                    has_confirmed = True
                else:
                    # Edge case: physical seat mismatch -> waitlist
                    inventory.waitlist_count += 1
                    passenger.status = 'WAITLISTED'
                    passenger.waitlist_number = inventory.waitlist_count
                    passenger.save()

                    WaitlistEntry.objects.create(
                        booking=booking,
                        passenger=passenger,
                        inventory=inventory,
                        position=inventory.waitlist_count
                    )
                    has_waitlist = True
            else:
                # Add to Waitlist
                inventory.waitlist_count += 1
                passenger.status = 'WAITLISTED'
                passenger.waitlist_number = inventory.waitlist_count
                passenger.save()

                WaitlistEntry.objects.create(
                    booking=booking,
                    passenger=passenger,
                    inventory=inventory,
                    position=inventory.waitlist_count
                )
                has_waitlist = True

        inventory.save()

        # Update booking overall status
        if has_confirmed and not has_waitlist:
            booking.status = 'CONFIRMED'
        elif has_waitlist and not has_confirmed:
            booking.status = 'WAITLISTED'
        else:
            booking.status = 'CONFIRMED' # Mixed/Partially waitlisted treated as confirmed with WL
        booking.save()

        BookingLog.objects.create(
            booking=booking,
            action='SEAT_ALLOCATED',
            description=f"Seats allocated atomically. Confirmed: {booking.confirmed_passengers_count}, Waitlisted: {booking.waitlisted_passengers_count}"
        )

        return booking

def promote_waitlist_on_seat_release(train, journey_date, class_code, released_seat):
    """
    Promotes the next eligible waitlisted passenger to the released seat and renumbers queue.
    """
    with transaction.atomic():
        inventory = JourneyInventory.objects.select_for_update().get(
            train=train,
            journey_date=journey_date,
            class_code=class_code
        )

        # Get first active waitlist entry in FIFO order
        next_entry = WaitlistEntry.objects.select_for_update().filter(
            inventory=inventory,
            is_promoted=False,
            passenger__status='WAITLISTED'
        ).order_by('position').first()

        if next_entry:
            passenger = next_entry.passenger
            passenger.status = 'CONFIRMED'
            passenger.allocated_seat = released_seat
            passenger.waitlist_number = None
            passenger.save()

            # Create seat lock for promoted passenger
            AllocatedJourneySeat.objects.create(
                seat=released_seat,
                journey_date=journey_date,
                passenger=passenger,
                booking=passenger.booking
            )

            next_entry.is_promoted = True
            next_entry.promoted_at = timezone.now()
            next_entry.save()

            # Update booking status if needed
            booking = passenger.booking
            if booking.status == 'WAITLISTED':
                booking.status = 'CONFIRMED'
                booking.save()

            # Decrement waitlist count
            if inventory.waitlist_count > 0:
                inventory.waitlist_count -= 1
            inventory.save()

            # Shift position of remaining waitlist entries forward
            subsequent_entries = WaitlistEntry.objects.filter(
                inventory=inventory,
                is_promoted=False,
                position__gt=next_entry.position
            )
            for entry in subsequent_entries:
                entry.position -= 1
                entry.save()
                entry.passenger.waitlist_number = entry.position
                entry.passenger.save()

            BookingLog.objects.create(
                booking=passenger.booking,
                action='WAITLIST_PROMOTED',
                description=f"Passenger {passenger.name} promoted from waitlist to Confirmed seat {released_seat}."
            )
            return passenger
        else:
            # No waitlist passenger: release seat back to available inventory
            inventory.available_seats += 1
            if inventory.booked_seats > 0:
                inventory.booked_seats -= 1
            inventory.save()
            return None

def cancel_booking_or_passengers(booking, passenger_ids=None, reason=""):
    """
    Cancels specified or all passengers, calculates tiered refund,
    releases physical seats, and triggers waitlist auto-promotion.
    """
    with transaction.atomic():
        now_dt = timezone.now()
        dep_time = booking.train.departure_time or timezone.datetime.min.time()
        # Localize or combine date and time
        dep_dt = timezone.make_aware(
            timezone.datetime.combine(booking.journey_date, dep_time),
            timezone.get_current_timezone()
        )
        
        hours_before = (dep_dt - now_dt).total_seconds() / 3600.0

        # Refund tier calculation
        if hours_before > 48:
            refund_rate = Decimal('0.90') # 90% refund, 10% clerkage
        elif hours_before >= 12:
            refund_rate = Decimal('0.50') # 50% refund
        else:
            refund_rate = Decimal('0.00') # 0% refund

        if passenger_ids:
            passengers_to_cancel = booking.passengers.filter(id__in=passenger_ids, status__in=['CONFIRMED', 'WAITLISTED'])
        else:
            passengers_to_cancel = booking.passengers.filter(status__in=['CONFIRMED', 'WAITLISTED'])

        if not passengers_to_cancel.exists():
            return None

        total_cancelled_fare = sum(p.fare for p in passengers_to_cancel)
        refund_amount = round(total_cancelled_fare * refund_rate, 2)
        cancellation_fee = total_cancelled_fare - refund_amount
        cancelled_count = passengers_to_cancel.count()

        for passenger in passengers_to_cancel:
            if passenger.status == 'CONFIRMED' and passenger.allocated_seat:
                seat = passenger.allocated_seat
                # Remove physical lock
                AllocatedJourneySeat.objects.filter(
                    seat=seat,
                    journey_date=booking.journey_date,
                    passenger=passenger
                ).delete()
                passenger.allocated_seat = None
                passenger.status = 'CANCELLED'
                passenger.save()

                # Trigger auto-promotion for released seat
                promote_waitlist_on_seat_release(booking.train, booking.journey_date, booking.class_code, seat)
            elif passenger.status == 'WAITLISTED':
                passenger.status = 'CANCELLED'
                passenger.save()
                # Remove from waitlist queue
                if hasattr(passenger, 'waitlist_entry'):
                    wl_entry = passenger.waitlist_entry
                    wl_pos = wl_entry.position
                    wl_inv = wl_entry.inventory
                    wl_entry.delete()

                    # Shift subsequent waitlist positions forward
                    subs = WaitlistEntry.objects.filter(inventory=wl_inv, position__gt=wl_pos, is_promoted=False)
                    for s in subs:
                        s.position -= 1
                        s.save()
                        s.passenger.waitlist_number = s.position
                        s.passenger.save()

                    if wl_inv.waitlist_count > 0:
                        wl_inv.waitlist_count -= 1
                        wl_inv.save()

        # Update booking overall status
        remaining_active = booking.passengers.filter(status__in=['CONFIRMED', 'WAITLISTED']).count()
        if remaining_active == 0:
            booking.status = 'CANCELLED'
        else:
            booking.status = 'PARTIALLY_CANCELLED'
        booking.save()

        from .models import Cancellation
        cancellation = Cancellation.objects.create(
            booking=booking,
            cancelled_passengers_count=cancelled_count,
            original_fare=total_cancelled_fare,
            cancellation_fee=cancellation_fee,
            refund_amount=refund_amount,
            refund_status='COMPLETED',
            cancellation_reason=reason
        )

        BookingLog.objects.create(
            booking=booking,
            action='CANCELLED',
            description=f"Cancelled {cancelled_count} passenger(s). Original fare: Rs. {total_cancelled_fare}, Refund: Rs. {refund_amount} (Fee: Rs. {cancellation_fee}). Policy Tier: {int(refund_rate*100)}% refund."
        )

        return cancellation


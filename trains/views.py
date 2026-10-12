from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from datetime import datetime, date, timedelta, time
from .models import Station, Train, TrainStop, TrainClass

import re
import difflib

STATION_ALIAS_MAP = {
    'VIJAYWADA': 'BZA',
    'VIJAYAWADA': 'BZA',
    'BEZWADA': 'BZA',
    'TIRUPATHI': 'TPTY',
    'TIRUPATI': 'TPTY',
    'VIZAG': 'VSKP',
    'VISAKHAPATNAM': 'VSKP',
    'VISHAKHAPATNAM': 'VSKP',
    'VISAKHA': 'VSKP',
    'BANGLORE': 'SBC',
    'BANGALORE': 'SBC',
    'BENGALURU': 'SBC',
    'CHENNAI': 'MAS',
    'MADRAS': 'MAS',
    'HYDERABAD': 'SC',
    'SECUNDERABAD': 'SC',
    'KURNOOL': 'KRNT',
    'CUDDAPAH': 'HX',
    'KADAPA': 'HX',
}

def get_station_suggestions(query_str):
    """Returns up to 3 closest matching station names/codes using difflib."""
    if not query_str:
        return []
    raw = query_str.strip()
    all_stations = list(Station.objects.all())
    
    name_map = {}
    candidate_keys = []
    
    for s in all_stations:
        for key in (s.name, s.code, s.city, f"{s.name} ({s.code})"):
            candidate_keys.append(key)
            name_map[key.lower()] = s
            
    for alias, code in STATION_ALIAS_MAP.items():
        title_alias = alias.title()
        candidate_keys.append(title_alias)
        st = next((s for s in all_stations if s.code == code), None)
        if st:
            name_map[title_alias.lower()] = st

    matches = difflib.get_close_matches(raw, candidate_keys, n=6, cutoff=0.35)
    suggestions = []
    seen = set()
    for m in matches:
        st = name_map.get(m.lower())
        if st and st.code not in seen:
            seen.add(st.code)
            suggestions.append(f"{st.name} ({st.code})")
            if len(suggestions) >= 3:
                break
    return suggestions

def get_station_by_query(query_str):
    """
    Resolves a Station from various inputs case-insensitively:
    - Station code (e.g. 'BZA', 'bza')
    - Exact name (e.g. 'Vijayawada Jn')
    - 'Name (CODE)' format (e.g. 'Vijayawada (BZA)', 'Vijayawada Jn (BZA)')
    - Partial name (e.g. 'Vijayawada', 'Tirupati')
    - Alias map / common alternate spellings (e.g. 'Vizag', 'Bangalore', 'Tirupathi')
    """
    if not query_str:
        return None
    raw = query_str.strip()
    if not raw:
        return None

    # 1. If 'Name (CODE)' format, extract code inside parentheses
    code_match = re.search(r'\(([A-Za-z0-9]{2,10})\)', raw)
    if code_match:
        code_inside = code_match.group(1).upper()
        station = Station.objects.filter(code=code_inside).first()
        if station:
            return station
        raw = re.sub(r'\s*\([A-Za-z0-9]+\)\s*', ' ', raw).strip()

    cleaned = raw.upper()

    # 2. Direct station code (case-insensitive)
    station = Station.objects.filter(code=cleaned).first()
    if station:
        return station

    # 3. Alias map lookup (direct and alpha-only normalized)
    norm_key = re.sub(r'[^A-Z0-9]', '', cleaned)
    if norm_key in STATION_ALIAS_MAP:
        station = Station.objects.filter(code=STATION_ALIAS_MAP[norm_key]).first()
        if station:
            return station

    for word in re.findall(r'[A-Za-z]+', cleaned):
        if word in STATION_ALIAS_MAP:
            station = Station.objects.filter(code=STATION_ALIAS_MAP[word]).first()
            if station:
                return station

    # 4. Exact name match (case-insensitive)
    station = Station.objects.filter(name__iexact=raw).first()
    if station:
        return station

    # 5. Exact city match
    station = Station.objects.filter(city__iexact=raw).first()
    if station:
        return station

    # 6. Substring match on name or city
    station = Station.objects.filter(Q(name__icontains=raw) | Q(city__icontains=raw)).first()
    if station:
        return station

    # 7. Prefix match
    station = Station.objects.filter(name__istartswith=raw).first()
    if station:
        return station

    # 8. Suffix-stripped match ("Jn", "Junction", "City", "Cantt", "Central")
    stem = re.sub(r'\b(JN|JUNCTION|CITY|CANTT|CENTRAL|ROAD|TERMINUS)\b', '', cleaned).strip()
    if stem and stem != cleaned:
        station = Station.objects.filter(Q(name__icontains=stem) | Q(city__icontains=stem)).first()
        if station:
            return station
        if stem in STATION_ALIAS_MAP:
            station = Station.objects.filter(code=STATION_ALIAS_MAP[stem]).first()
            if station:
                return station

    return None

def train_search_view(request):
    """Searches trains between two stations on a journey date with intermediate stop support."""
    from_query = request.GET.get('from_station', '').strip()
    to_query = request.GET.get('to_station', '').strip()
    date_str = request.GET.get('journey_date', '').strip()

    if not from_query or not to_query or not date_str:
        messages.warning(request, "Please enter both origin, destination stations, and journey date.")
        return redirect('core:home')

    try:
        journey_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, "Invalid date format. Please select a valid date.")
        return redirect('core:home')

    today = date.today()
    if journey_date < today:
        messages.error(request, "Journey date cannot be in the past.")
        return redirect('core:home')
    if journey_date > today + timedelta(days=120):
        messages.error(request, "Advance reservation is permitted up to 120 days only.")
        return redirect('core:home')

    from_station = get_station_by_query(from_query)
    to_station = get_station_by_query(to_query)

    if not from_station or not to_station:
        if not from_station:
            suggs = get_station_suggestions(from_query)
            if suggs:
                messages.error(request, f"We couldn't find a station named '{from_query}'. Did you mean: {', '.join(suggs)}?")
            else:
                messages.error(request, f"We couldn't find a station named '{from_query}'.")
        if not to_station:
            suggs = get_station_suggestions(to_query)
            if suggs:
                messages.error(request, f"We couldn't find a station named '{to_query}'. Did you mean: {', '.join(suggs)}?")
            else:
                messages.error(request, f"We couldn't find a station named '{to_query}'.")
        return redirect('core:home')

    if from_station == to_station:
        messages.error(request, "Origin and destination stations cannot be the same.")
        return redirect('core:home')

    # Save to session recent searches
    recent_searches = request.session.get('recent_searches', [])
    search_entry = {
        'from_code': from_station.code,
        'from_name': from_station.name,
        'to_code': to_station.code,
        'to_name': to_station.name,
        'date': date_str,
    }
    if search_entry not in recent_searches:
        recent_searches.insert(0, search_entry)
        request.session['recent_searches'] = recent_searches[:5]

    # Day of week abbreviation e.g. 'MON', 'TUE'
    day_abbr = journey_date.strftime('%a').upper()

    # Find trains that stop at both stations in correct sequence
    matching_trains = []
    active_trains = Train.objects.filter(is_active=True).prefetch_related('stops__station', 'classes')

    for train in active_trains:
        if not train.runs_on_day(day_abbr):
            continue

        stops = list(train.stops.all())
        from_stop = next((s for s in stops if s.station_id == from_station.id), None)
        to_stop = next((s for s in stops if s.station_id == to_station.id), None)

        if from_stop and to_stop and from_stop.stop_order < to_stop.stop_order:
            distance_segment = max(to_stop.distance_from_source_km - from_stop.distance_from_source_km, 50)
            
            # Compute class details and fares
            class_options = []
            for tc in train.classes.all():
                fare = float(tc.base_fare) + (float(tc.per_km_rate) * distance_segment)
                # Query inventory if available (from bookings app models)
                class_options.append({
                    'class_code': tc.class_code,
                    'class_name': tc.class_name,
                    'fare': round(fare, 2),
                    'total_seats': tc.total_seats,
                })

            matching_trains.append({
                'train': train,
                'from_stop': from_stop,
                'to_stop': to_stop,
                'distance_km': distance_segment,
                'departure_time': from_stop.departure_time or train.departure_time,
                'arrival_time': to_stop.arrival_time or train.arrival_time,
                'classes': class_options,
            })

    return render(request, 'trains/search_results.html', {
        'from_station': from_station,
        'to_station': to_station,
        'journey_date': journey_date,
        'date_str': date_str,
        'day_abbr': day_abbr,
        'matching_trains': matching_trains,
        'trains_count': len(matching_trains),
    })

def train_schedule_view(request, train_number):
    """Displays full timetable and intermediate halts of a train."""
    train = get_object_or_404(Train.objects.prefetch_related('stops__station', 'classes'), train_number=train_number)
    stops = train.stops.all().order_by('stop_order')
    return render(request, 'trains/schedule.html', {
        'train': train,
        'stops': stops,
    })

def live_status_view(request):
    """Simulates real-time train running status with visual stop timeline."""
    train_number = request.GET.get('train_number', '').strip()
    train = None
    stops_status = []
    current_status_summary = ""

    if train_number:
        train = Train.objects.filter(train_number=train_number).prefetch_related('stops__station').first()
        if not train:
            messages.error(request, f"Train #{train_number} not found.")
        else:
            now = datetime.now()
            current_time = now.time()
            stops = list(train.stops.all().order_by('stop_order'))
            total_stops = len(stops)

            # Simulated calculation: determine index based on time of day
            passed = True
            active_stop_idx = 0
            for idx, stop in enumerate(stops):
                stop_time = stop.departure_time or stop.arrival_time or time(8, 0)
                is_passed = (stop_time <= current_time)
                if not is_passed and passed:
                    active_stop_idx = max(0, idx - 1)
                    passed = False
                stops_status.append({
                    'stop': stop,
                    'is_passed': is_passed,
                    'is_current': (idx == active_stop_idx),
                    'delay_mins': 5 if idx > 0 else 0, # simulated mild delay
                })

            current_status_summary = f"Simulated Status: Running on time near {stops[active_stop_idx].station.name} ({stops[active_stop_idx].station.code})"

    sample_trains = Train.objects.filter(is_active=True)[:6]

    return render(request, 'trains/live_status.html', {
        'train_number': train_number,
        'train': train,
        'stops_status': stops_status,
        'current_status_summary': current_status_summary,
        'sample_trains': sample_trains,
    })

def station_autocomplete_view(request):
    """AJAX JSON search for station dropdown autocomplete matching code, name, city, and aliases."""
    term = request.GET.get('term', '').strip()
    get_all = request.GET.get('all', '').strip()

    if get_all or len(term) < 1:
        stations = Station.objects.all().order_by('name')
        if not get_all:
            stations = stations[:15]
        results = [
            {
                'code': s.code,
                'name': s.name,
                'city': s.city,
                'label': f"{s.name} ({s.code})",
                'value': s.code,
            }
            for s in stations
        ]
        return JsonResponse(results, safe=False)

    term_upper = term.upper()
    matching_station_codes = set()

    for alias, code in STATION_ALIAS_MAP.items():
        if term_upper in alias or alias in term_upper:
            matching_station_codes.add(code)

    stations = Station.objects.filter(
        Q(code__icontains=term) | Q(name__icontains=term) | Q(city__icontains=term) | Q(code__in=matching_station_codes)
    ).distinct().order_by('name')[:15]

    results = [
        {
            'code': s.code,
            'name': s.name,
            'city': s.city,
            'label': f"{s.name} ({s.code})",
            'value': s.code,
        }
        for s in stations
    ]
    return JsonResponse(results, safe=False)

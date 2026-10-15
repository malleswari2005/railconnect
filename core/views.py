from django.shortcuts import render
from datetime import date, timedelta

def home_view(request):
    """Homepage with search form, recent searches, and popular routes."""
    today = date.today().isoformat()
    max_date = (date.today() + timedelta(days=120)).isoformat()
    popular_routes = [
        {'from_name': 'New Delhi', 'from_code': 'NDLS', 'to_name': 'Mumbai Central', 'to_code': 'MMCT'},
        {'from_name': 'Howrah Jn', 'from_code': 'HWH', 'to_name': 'New Delhi', 'to_code': 'NDLS'},
        {'from_name': 'Bengaluru City', 'from_code': 'SBC', 'to_name': 'Chennai Central', 'to_code': 'MAS'},
        {'from_name': 'Mumbai Central', 'from_code': 'MMCT', 'to_name': 'Ahmedabad Jn', 'to_code': 'ADI'},
    ]
    return render(request, 'core/home.html', {
        'today': today,
        'max_date': max_date,
        'popular_routes': popular_routes,
    })

def about_view(request):
    """About page explaining project architecture, features, and team division for viva."""
    return render(request, 'core/about.html')

def handler403_view(request, exception=None):
    """Custom branded 403 page."""
    return render(request, '403.html', status=403)

def handler404_view(request, exception=None):
    """Custom branded 404 page."""
    return render(request, '404.html', status=404)

def handler500_view(request):
    """Custom branded 500 page."""
    return render(request, '500.html', status=500)

from functools import wraps
from django.shortcuts import render, redirect
from django.conf import settings

def get_user_role(user):
    """
    Returns the role of a user based on Django Groups and staff flags.
    Any user with no group defaults to 'Passenger'.
    """
    if not user or not user.is_authenticated:
        return 'Guest'

    if user.is_superuser or user.is_staff or user.groups.filter(name='Admin').exists():
        return 'Admin'
    if user.groups.filter(name='TTE').exists():
        return 'TTE'
    if user.groups.filter(name='Operations').exists():
        return 'Operations'
    return 'Passenger'

def get_role_home_url(user):
    """
    Returns the designated portal entry point for a user based on role.
    """
    role = get_user_role(user)
    if role == 'Admin':
        return '/admin-portal/'
    elif role == 'TTE':
        return '/tte/'
    elif role == 'Operations':
        return '/operations/'
    return '/'

def role_required(allowed_roles):
    """
    Decorator for views that checks if the logged in user belongs to one of the allowed roles.
    If unauthenticated, redirects to LOGIN_URL with ?next=.
    If unauthorized, returns HTTP 403 Forbidden with custom 403.html template.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"{settings.LOGIN_URL}?next={request.get_full_path()}")

            user_role = get_user_role(request.user)

            # Superusers always have universal oversight
            if request.user.is_superuser or user_role in allowed_roles:
                return view_func(request, *args, **kwargs)

            return render(request, '403.html', {
                'user_role': user_role,
                'allowed_roles': allowed_roles,
            }, status=403)
        return _wrapped_view
    return decorator

def admin_required(view_func):
    return role_required(['Admin'])(view_func)

def tte_required(view_func):
    return role_required(['TTE'])(view_func)

def operations_required(view_func):
    return role_required(['Operations'])(view_func)

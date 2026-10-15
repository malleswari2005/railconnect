from datetime import datetime
from django.conf import settings
from core.decorators import get_user_role

def global_context(request):
    """Provides application-wide variables for templates."""
    user = getattr(request, 'user', None)
    return {
        'PROJECT_NAME': 'RailConnect',
        'DEMO_MODE': getattr(settings, 'DEMO_MODE', True),
        'DEMO_REFUND_POLICY': getattr(settings, 'DEMO_REFUND_POLICY', {}),
        'CURRENT_YEAR': datetime.now().year,
        'user_role': get_user_role(user),
    }

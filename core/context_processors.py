from django.conf import settings
from datetime import datetime

def global_context(request):
    """Provides application-wide variables for templates."""
    return {
        'PROJECT_NAME': 'RailConnect',
        'DEMO_MODE': getattr(settings, 'DEMO_MODE', True),
        'DEMO_REFUND_POLICY': getattr(settings, 'DEMO_REFUND_POLICY', {}),
        'CURRENT_YEAR': datetime.now().year,
    }

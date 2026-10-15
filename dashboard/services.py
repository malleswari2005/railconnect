from .models import AuditLog

def create_audit_log(actor, action, object_repr, details="", ip_address=None):
    """
    Utility function to create an immutable audit log record.
    Safe against null actor or exceptions.
    """
    try:
        user = actor if (actor and actor.is_authenticated) else None
        return AuditLog.objects.create(
            actor=user,
            action=action,
            object_repr=str(object_repr)[:255],
            details=details,
            ip_address=ip_address
        )
    except Exception:
        # Never break primary operational flow if audit logging fails
        return None

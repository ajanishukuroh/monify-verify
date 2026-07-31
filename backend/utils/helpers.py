from datetime import datetime
import uuid


def format_currency(amount, currency='NGN'):
    """Format amount as Nigerian Naira."""
    try:
        return f"₦{float(amount):,.2f}"
    except (TypeError, ValueError):
        return f"₦0.00"


def format_datetime(dt):
    """Format a datetime object for display."""
    if not dt:
        return 'N/A'
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return dt
    return dt.strftime('%b %d, %Y %I:%M %p')


def generate_payment_reference():
    """Generate a unique payment reference."""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    unique_id = str(uuid.uuid4()).replace('-', '')[:8].upper()
    return f"MNFY-{timestamp}-{unique_id}"


def get_status_badge(status):
    """Return CSS class for payment status."""
    status_map = {
        'PAID': 'badge-success',
        'PENDING': 'badge-warning',
        'FAILED': 'badge-danger',
        'CANCELLED': 'badge-secondary',
        'OVERPAID': 'badge-info',
        'PARTIALLY_PAID': 'badge-warning',
    }
    return status_map.get(status, 'badge-secondary')


def get_status_icon(status):
    """Return emoji icon for payment status."""
    icons = {
        'PAID': '✅',
        'PENDING': '⏳',
        'FAILED': '❌',
        'CANCELLED': '🚫',
        'OVERPAID': '💚',
        'PARTIALLY_PAID': '⚠️',
    }
    return icons.get(status, '❓')

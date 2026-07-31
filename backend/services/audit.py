from backend.models.audit import AuditLog
from backend.database import db
from datetime import datetime


def log_action(payment_id, action, performed_by='system', metadata=None):
    """Log an audit action for a payment."""
    entry = AuditLog(
        payment_id=payment_id,
        action=action,
        performed_by=performed_by,
        extra_data=metadata,
        timestamp=datetime.utcnow()
    )
    db.session.add(entry)
    db.session.commit()
    return entry

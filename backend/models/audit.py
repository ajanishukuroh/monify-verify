from datetime import datetime
from backend.database import db


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    performed_by = db.Column(db.String(150), nullable=True)
    extra_data = db.Column(db.Text, nullable=True)  # JSON string for extra data
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AuditLog {self.action} @ {self.timestamp}>'

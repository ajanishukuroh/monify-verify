from datetime import datetime
from backend.database import db


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    payment_reference = db.Column(db.String(100), unique=True, nullable=False)
    transaction_reference = db.Column(db.String(100), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='NGN')
    status = db.Column(db.String(30), default='PENDING')  # PENDING, PAID, FAILED, CANCELLED
    customer_name = db.Column(db.String(150), nullable=True)
    customer_email = db.Column(db.String(150), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    qr_code_path = db.Column(db.String(255), nullable=True)
    checkout_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    audit_logs = db.relationship('AuditLog', backref='payment', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'merchant_id': self.merchant_id,
            'payment_reference': self.payment_reference,
            'transaction_reference': self.transaction_reference,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Payment {self.payment_reference} - {self.status}>'

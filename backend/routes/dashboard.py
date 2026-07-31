from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime, date
from backend.models.payment import Payment
from backend.models.audit import AuditLog
from backend.utils.helpers import format_currency
import datetime as dt_module

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())

    # Stats
    all_payments = Payment.query.filter_by(merchant_id=current_user.id).all()
    today_payments = Payment.query.filter(
        Payment.merchant_id == current_user.id,
        Payment.created_at >= today_start
    ).all()

    today_revenue = sum(p.amount for p in today_payments if p.status == 'PAID')
    today_tx_count = len(today_payments)
    pending_count = len([p for p in all_payments if p.status == 'PENDING'])
    verified_count = len([p for p in all_payments if p.status == 'PAID'])

    # Recent payments (last 5)
    recent_payments = Payment.query.filter_by(
        merchant_id=current_user.id
    ).order_by(Payment.created_at.desc()).limit(5).all()

    # Recent audit logs (last 8)
    payment_ids = [p.id for p in all_payments]
    recent_logs = []
    if payment_ids:
        recent_logs = AuditLog.query.filter(
            AuditLog.payment_id.in_(payment_ids)
        ).order_by(AuditLog.timestamp.desc()).limit(8).all()

    return render_template(
        'dashboard.html',
        today_revenue=format_currency(today_revenue),
        today_tx_count=today_tx_count,
        pending_count=pending_count,
        verified_count=verified_count,
        recent_payments=recent_payments,
        recent_logs=recent_logs,
        format_currency=format_currency,
        now=datetime.utcnow(),
    )

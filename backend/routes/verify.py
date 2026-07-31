from flask import Blueprint, render_template
from backend.models.payment import Payment
from backend.models.user import User
from backend.services.audit import log_action
from backend.utils.helpers import format_currency, format_datetime

verify_bp = Blueprint('verify', __name__)


@verify_bp.route('/verify/<reference>')
def verify_payment(reference):
    """
    Public verification page — accessible via QR code scan.
    No authentication required.
    """
    payment = Payment.query.filter_by(payment_reference=reference).first()

    if not payment:
        return render_template('verify.html', payment=None, merchant=None,
                               error='Payment reference not found.'), 404

    merchant = User.query.get(payment.merchant_id)

    # Log the public verification view
    log_action(payment.id, 'Verification Page Viewed (QR Scan)', performed_by='public')

    return render_template(
        'verify.html',
        payment=payment,
        merchant=merchant,
        error=None,
        format_currency=format_currency,
        format_datetime=format_datetime,
    )

import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from backend.database import db
from backend.models.payment import Payment
from backend.models.audit import AuditLog
from backend.services import monnify, qr as qr_service
from backend.services.audit import log_action
from backend.utils.helpers import generate_payment_reference, format_currency, format_datetime

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')


@payment_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        customer_name = request.form.get('customer_name', '').strip()
        customer_email = request.form.get('customer_email', '').strip()
        amount = request.form.get('amount', '').strip()
        description = request.form.get('description', 'Payment').strip()

        if not all([customer_name, customer_email, amount]):
            flash('All fields are required.', 'error')
            return render_template('payment/create.html')

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash('Please enter a valid amount.', 'error')
            return render_template('payment/create.html')

        ref = generate_payment_reference()

        # Save to DB first
        payment = Payment(
            merchant_id=current_user.id,
            payment_reference=ref,
            amount=amount,
            currency='NGN',
            status='PENDING',
            customer_name=customer_name,
            customer_email=customer_email,
            description=description
        )
        db.session.add(payment)
        db.session.commit()

        log_action(payment.id, 'Payment Initialized', performed_by=current_user.email)

        # Initialize with Monnify
        result = monnify.initialize_transaction(
            amount=amount,
            customer_name=customer_name,
            customer_email=customer_email,
            payment_reference=ref,
            description=description
        )

        if result and result.get('checkoutUrl'):
            payment.checkout_url = result['checkoutUrl']
            db.session.commit()
            log_action(payment.id, 'Monnify Checkout URL Generated', performed_by=current_user.email)
            return redirect(result['checkoutUrl'])
        else:
            flash('Could not connect to Monnify. Payment saved as pending.', 'warning')
            return redirect(url_for('payment.history'))

    return render_template('payment/create.html')


@payment_bp.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')

    query = Payment.query.filter_by(merchant_id=current_user.id)
    if status_filter:
        query = query.filter_by(status=status_filter)

    payments = query.order_by(Payment.created_at.desc()).paginate(
        page=page, per_page=15, error_out=False
    )

    return render_template(
        'payment/history.html',
        payments=payments,
        status_filter=status_filter,
        format_currency=format_currency,
        format_datetime=format_datetime,
    )


@payment_bp.route('/callback')
@login_required
def callback():
    """Handle redirect from Monnify after payment attempt."""
    payment_reference = request.args.get('paymentReference', '')
    if not payment_reference:
        flash('No payment reference found.', 'error')
        return redirect(url_for('dashboard.index'))

    payment = Payment.query.filter_by(
        payment_reference=payment_reference,
        merchant_id=current_user.id
    ).first()

    if not payment:
        flash('Payment not found.', 'error')
        return redirect(url_for('dashboard.index'))

    # Verify with Monnify
    result = monnify.verify_transaction(payment_reference)
    if result:
        new_status = result.get('paymentStatus', 'PENDING')
        payment.status = new_status
        payment.transaction_reference = result.get('transactionReference', '')
        db.session.commit()

        log_action(payment.id, f'Payment Status Updated: {new_status}', performed_by='monnify_callback')

        if new_status == 'PAID':
            # Generate QR code
            try:
                base_url = current_app.config['BASE_URL']
                qr_path = qr_service.generate_qr(payment_reference, base_url)
                payment.qr_code_path = qr_path
                db.session.commit()
                log_action(payment.id, 'QR Code Generated', performed_by='system')
            except Exception as e:
                current_app.logger.error(f"QR generation failed: {e}")

            flash('✅ Payment confirmed! QR code generated.', 'success')
        else:
            flash(f'Payment status: {new_status}', 'warning')
    else:
        flash('Could not verify payment with Monnify.', 'warning')

    return redirect(url_for('payment.history'))


@payment_bp.route('/webhook', methods=['POST'])
def webhook():
    """Monnify webhook endpoint for real-time payment notifications."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No data'}), 400

    payment_reference = data.get('paymentReference', '')
    transaction_reference = data.get('transactionReference', '')
    payment_status = data.get('paymentStatus', '')
    amount = data.get('amountPaid', 0)

    payment = Payment.query.filter_by(payment_reference=payment_reference).first()
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404

    payment.status = payment_status
    payment.transaction_reference = transaction_reference
    db.session.commit()

    log_action(payment.id, f'Webhook: {payment_status}', performed_by='monnify_webhook',
               metadata=json.dumps({'amount_paid': amount}))

    if payment_status == 'PAID':
        try:
            base_url = current_app.config['BASE_URL']
            qr_path = qr_service.generate_qr(payment_reference, base_url)
            payment.qr_code_path = qr_path
            db.session.commit()
            log_action(payment.id, 'QR Code Generated', performed_by='system')
        except Exception as e:
            current_app.logger.error(f"QR generation failed: {e}")

    return jsonify({'status': 'ok'}), 200


@payment_bp.route('/<reference>/verify-now')
@login_required
def verify_now(reference):
    """Manually re-verify a payment from Monnify."""
    payment = Payment.query.filter_by(
        payment_reference=reference,
        merchant_id=current_user.id
    ).first_or_404()

    result = monnify.verify_transaction(reference)
    if result:
        new_status = result.get('paymentStatus', payment.status)
        payment.status = new_status
        payment.transaction_reference = result.get('transactionReference', payment.transaction_reference)
        db.session.commit()
        log_action(payment.id, f'Manual Verify: {new_status}', performed_by=current_user.email)

        if new_status == 'PAID' and not payment.qr_code_path:
            try:
                base_url = current_app.config['BASE_URL']
                qr_path = qr_service.generate_qr(reference, base_url)
                payment.qr_code_path = qr_path
                db.session.commit()
                log_action(payment.id, 'QR Code Generated', performed_by='system')
            except Exception as e:
                current_app.logger.error(f"QR generation: {e}")

        flash(f'Payment status: {new_status}', 'success' if new_status == 'PAID' else 'warning')
    else:
        flash('Could not reach Monnify for verification.', 'error')

    return redirect(url_for('payment.history'))


@payment_bp.route('/<reference>/qr')
@login_required
def download_qr(reference):
    """Download the QR code for a payment."""
    payment = Payment.query.filter_by(
        payment_reference=reference,
        merchant_id=current_user.id
    ).first_or_404()

    if not payment.qr_code_path:
        # Generate on demand
        try:
            base_url = current_app.config['BASE_URL']
            qr_path = qr_service.generate_qr(reference, base_url)
            payment.qr_code_path = qr_path
            db.session.commit()
            log_action(payment.id, 'QR Code Generated (On Demand)', performed_by=current_user.email)
        except Exception as e:
            flash('Failed to generate QR code.', 'error')
            return redirect(url_for('payment.history'))

    import os
    if not os.path.exists(payment.qr_code_path):
        flash('QR code file not found.', 'error')
        return redirect(url_for('payment.history'))

    log_action(payment.id, 'Merchant Downloaded QR Code', performed_by=current_user.email)
    return send_file(payment.qr_code_path, as_attachment=True, download_name=f"verify-{reference}.png")


@payment_bp.route('/<reference>/audit')
@login_required
def audit_log(reference):
    """View audit logs for a specific payment."""
    payment = Payment.query.filter_by(
        payment_reference=reference,
        merchant_id=current_user.id
    ).first_or_404()

    logs = AuditLog.query.filter_by(payment_id=payment.id).order_by(AuditLog.timestamp.asc()).all()
    log_action(payment.id, 'Merchant Viewed Audit Log', performed_by=current_user.email)

    return render_template(
        'payment/audit.html',
        payment=payment,
        logs=logs,
        format_currency=format_currency,
        format_datetime=format_datetime,
    )


@payment_bp.route('/dev/simulate-webhook', methods=['GET', 'POST'])
@login_required
def simulate_webhook():
    """DEV ONLY: Simulate a Monnify webhook for local testing."""
    if request.method == 'POST':
        reference = request.form.get('reference', '').strip()
        status = request.form.get('status', 'PAID')
        amount = float(request.form.get('amount', 100))

        payment = Payment.query.filter_by(
            payment_reference=reference,
            merchant_id=current_user.id
        ).first()

        if not payment:
            flash('Payment reference not found.', 'error')
            return render_template('payment/simulate.html')

        payment.status = status
        payment.transaction_reference = f"SIMULATED_{reference}"
        db.session.commit()

        log_action(payment.id, f'[DEV] Simulated Webhook: {status}', performed_by=current_user.email)

        if status == 'PAID':
            try:
                base_url = current_app.config['BASE_URL']
                qr_path = qr_service.generate_qr(reference, base_url)
                payment.qr_code_path = qr_path
                db.session.commit()
                log_action(payment.id, 'QR Code Generated', performed_by='system')
                flash(f'✅ Payment marked as {status} and QR code generated!', 'success')
            except Exception as e:
                flash(f'Payment updated but QR failed: {e}', 'warning')
        else:
            flash(f'Payment status updated to {status}', 'info')

        return redirect(url_for('payment.history'))

    # Prefill with latest pending payment for convenience
    latest = Payment.query.filter_by(
        merchant_id=current_user.id, status='PENDING'
    ).order_by(Payment.created_at.desc()).first()

    return render_template('payment/simulate.html', latest_payment=latest)

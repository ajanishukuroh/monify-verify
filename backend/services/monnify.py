import requests
import base64
from flask import current_app


def _get_auth_header():
    """Build Basic Auth header from API key and secret."""
    api_key = current_app.config['MONNIFY_API_KEY']
    secret_key = current_app.config['MONNIFY_SECRET_KEY']
    credentials = f"{api_key}:{secret_key}"
    encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    return f"Basic {encoded}"


def get_access_token():
    """
    Authenticate with Monnify and retrieve an access token.
    Returns the token string or None on failure.
    """
    base_url = current_app.config['MONNIFY_BASE_URL']
    url = f"{base_url}/api/v1/auth/login"

    try:
        response = requests.post(
            url,
            headers={
                'Authorization': _get_auth_header(),
                'Content-Type': 'application/json'
            },
            timeout=15
        )
        data = response.json()
        if data.get('requestSuccessful'):
            return data['responseBody']['accessToken']
        else:
            current_app.logger.error(f"Monnify auth failed: {data}")
            return None
    except Exception as e:
        current_app.logger.error(f"Monnify auth exception: {e}")
        return None


def initialize_transaction(amount, customer_name, customer_email, payment_reference, description='Payment'):
    """
    Initialize a Monnify transaction.
    Returns dict with checkoutUrl and paymentReference, or None on failure.
    """
    token = get_access_token()
    if not token:
        return None

    base_url = current_app.config['MONNIFY_BASE_URL']
    contract_code = current_app.config['MONNIFY_CONTRACT_CODE']
    app_base_url = current_app.config['BASE_URL']

    url = f"{base_url}/api/v1/merchant/transactions/init-transaction"

    payload = {
        "amount": amount,
        "customerName": customer_name,
        "customerEmail": customer_email,
        "paymentReference": payment_reference,
        "paymentDescription": description,
        "currencyCode": "NGN",
        "contractCode": contract_code,
        "redirectUrl": f"{app_base_url}/payment/callback",
        "paymentMethods": ["ACCOUNT_TRANSFER", "CARD"]
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            timeout=15
        )
        data = response.json()
        if data.get('requestSuccessful'):
            return data['responseBody']
        else:
            current_app.logger.error(f"Monnify init failed: {data}")
            return None
    except Exception as e:
        current_app.logger.error(f"Monnify init exception: {e}")
        return None


def verify_transaction(payment_reference):
    """
    Verify a transaction status from Monnify by payment reference.
    Returns the responseBody dict or None on failure.
    """
    token = get_access_token()
    if not token:
        return None

    base_url = current_app.config['MONNIFY_BASE_URL']
    import urllib.parse
    encoded_ref = urllib.parse.quote(payment_reference, safe='')
    url = f"{base_url}/api/v2/merchant/transactions/query?paymentReference={encoded_ref}"

    try:
        response = requests.get(
            url,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            timeout=15
        )
        data = response.json()
        if data.get('requestSuccessful'):
            return data['responseBody']
        else:
            current_app.logger.error(f"Monnify verify failed: {data}")
            return None
    except Exception as e:
        current_app.logger.error(f"Monnify verify exception: {e}")
        return None

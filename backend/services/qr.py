import os
import qrcode
from qrcode.image.pure import PyPNGImage
from flask import current_app


def generate_qr(payment_reference: str, base_url: str) -> str:
    """
    Generate a QR code PNG that points to the public verification URL.
    Returns the relative file path of the saved QR image.
    """
    verify_url = f"{base_url.rstrip('/')}/verify/{payment_reference}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(verify_url)
    qr.make(fit=True)

    # Use PIL-based image for color support
    img = qr.make_image(fill_color="#6C47FF", back_color="white")

    qr_dir = current_app.config.get('QR_CODE_DIR', 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)

    filename = f"{payment_reference}.png"
    filepath = os.path.join(qr_dir, filename)
    img.save(filepath)

    return filepath

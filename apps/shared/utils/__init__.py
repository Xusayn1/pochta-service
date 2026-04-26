from decimal import Decimal
import logging
from datetime import datetime
import secrets

logger = logging.getLogger(__name__)


def generate_order_number(city_code="TAS"):
    """Generate order number in format PS-2025-TAS-123456."""
    year = datetime.now().year
    sequence = f"{secrets.randbelow(1_000_000):06d}"
    return f"PS-{year}-{city_code}-{sequence}"


def mask_name(full_name):
    """Mask name like 'John Doe' -> 'J*** D***'"""
    if not full_name:
        return ""
    parts = full_name.split()
    if len(parts) == 1:
        return parts[0][0] + "***"
    elif len(parts) >= 2:
        first = parts[0][0] + "***" if len(parts[0]) > 0 else "***"
        last = parts[-1][0] + "***" if len(parts[-1]) > 0 else "***"
        return f"{first} {last}"
    return "*** ***"


def calculate_price(service_type, weight_kg, distance_km):
    """Calculate price based on service type, weight, and distance"""
    base_rates = {
        'standard': {'base': 15000, 'per_kg': 2000, 'per_km': 500},
        'express': {'base': 25000, 'per_kg': 3000, 'per_km': 800},
        'business': {'base': 35000, 'per_kg': 4000, 'per_km': 1000},
        'fragile': {'base': 30000, 'per_kg': 5000, 'per_km': 1000},
        'freight': {'base': 50000, 'per_kg': 8000, 'per_km': 1500},
        'ecommerce': {'base': 20000, 'per_kg': 2500, 'per_km': 600},
    }

    rate = base_rates.get(service_type, base_rates['standard'])
    price = rate['base'] + (weight_kg * rate['per_kg']) + (distance_km * rate['per_km'])
    return Decimal(price).quantize(Decimal('0.01'))


def send_sms_notification(phone, message):
    """Send SMS notification (stub implementation - logs to console)"""
    logger.info(f"SMS to {phone}: {message}")
    # In production, integrate with SMS service like Eskiz, PlayMobile, etc.
    return True

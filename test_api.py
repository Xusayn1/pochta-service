#!/usr/bin/env python
"""
Test script for simplified address and order APIs.
"""
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api/v1"

def print_response(response, title):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)
    return response

def test_workflow():
    """Test the complete workflow."""
    
    # Generate unique phone number based on timestamp
    import time
    timestamp = str(int(time.time()))[-7:]
    phone = f"+998{timestamp}"
    
    # Ensure it's exactly 13 characters
    if len(phone) < 13:
        phone = phone.ljust(13, '0')
    phone = phone[:13]
    
    # 1. Register a test user
    print("\n\n### STEP 1: REGISTER A USER ###")
    register_data = {
        "username": f"testuser_{timestamp}",
        "phone": phone,
        "full_name": "Test User",
        "email": f"test_{timestamp}@example.com",
        "password": "testpass123",
        "confirm_password": "testpass123"
    }
    resp = requests.post(f"{BASE_URL}/users/register/", json=register_data)
    print_response(resp, "Registration Response")
    
    if resp.status_code != 201:
        print("[ERROR] Registration failed")
        return
    
    # Extract tokens
    auth_data = resp.json()
    access_token = auth_data.get('access')
    print(f"[OK] Registration successful. Access token: {access_token[:20]}...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 2. Test simplified address creation
    print("\n\n### STEP 2: CREATE ADDRESS (SIMPLIFIED) ###")
    address_data = {
        "title": "Home",
        "full_address": "Apartment 10, Navoi Street, Tashkent, Uzbekistan",
        "is_default": True
    }
    resp = requests.post(f"{BASE_URL}/users/addresses/", json=address_data, headers=headers)
    print_response(resp, "Address Creation Response")
    
    if resp.status_code == 201:
        address = resp.json()
        address_id = address.get('id')
        print(f"[OK] Address created successfully. ID: {address_id}")
    else:
        print("[ERROR] Address creation failed")
        return
    
    # 3. List addresses
    print("\n\n### STEP 3: LIST ADDRESSES ###")
    resp = requests.get(f"{BASE_URL}/users/addresses/", headers=headers)
    print_response(resp, "Address List Response")
    
    # 4. Test simplified order creation
    print("\n\n### STEP 4: CREATE ORDER (SIMPLIFIED) ###")
    order_data = {
        "sender_address": address_id,
        "recipient_phone": "+998901234568",
        "recipient_address": "123 Main Street, Samarkand, Uzbekistan",
        "weight_kg": 2.5
    }
    resp = requests.post(f"{BASE_URL}/orders/create/", json=order_data, headers=headers)
    print_response(resp, "Order Creation Response")
    
    if resp.status_code == 201:
        order = resp.json()
        order_number = order.get('order_number')
        print(f"[OK] Order created successfully. Order #: {order_number}")
    else:
        print("[ERROR] Order creation failed")
        return
    
    # 5. List orders
    print("\n\n### STEP 5: LIST ORDERS ###")
    resp = requests.get(f"{BASE_URL}/orders/", headers=headers)
    print_response(resp, "Order List Response")
    
    print("\n\n[OK] ALL TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    try:
        test_workflow()
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

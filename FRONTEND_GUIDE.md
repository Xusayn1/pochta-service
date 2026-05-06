# Frontend Integration Guide

## Address Form (Simplified)

### Before (Complex)
```javascript
// Old form with region/city selection
const addressForm = {
  title: "Home",
  region: 1,           // Select from dropdown
  city: 2,             // Dependent dropdown
  address: "Street...",
  landmark: "Nearby...",
  is_default: true
}
```

### After (Simplified)
```javascript
// New form - just text fields
const addressForm = {
  title: "Home",        // Address name/label
  full_address: "Apartment 10, Navoi Street, Tashkent, 100100, Uzbekistan",  // Complete address
  is_default: true      // Set as default pickup location
}
```

## API Calls

### Create Address
```javascript
async function saveAddress(addressData) {
  const response = await fetch('/api/v1/users/addresses/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`
    },
    body: JSON.stringify({
      title: addressData.title,        // e.g., "Home", "Office"
      full_address: addressData.fullAddress,  // Complete address text
      is_default: addressData.isDefault || false
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    console.error('Error:', error.details || error.error);
    return null;
  }
  
  return await response.json();
}
```

### List Addresses
```javascript
async function loadAddresses() {
  const response = await fetch('/api/v1/users/addresses/', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });
  
  if (!response.ok) {
    console.error('Failed to load addresses');
    return [];
  }
  
  const data = await response.json();
  return data.results;  // Array of addresses
}
```

### Update Address
```javascript
async function updateAddress(addressId, addressData) {
  const response = await fetch(`/api/v1/users/addresses/${addressId}/`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`
    },
    body: JSON.stringify({
      title: addressData.title,
      full_address: addressData.fullAddress,
      is_default: addressData.isDefault
    })
  });
  
  return await response.json();
}
```

## Order Form (Simplified)

### Before
```javascript
const orderForm = {
  sender_address: 1,
  recipient_name: "John Doe",
  recipient_phone: "+998901234567",
  recipient_address: "123 Main Street",
  item_description: "Package contents",
  to_region: 2,
  service_type: "standard",
  weight_kg: 2.5,
  declared_value: 10000,
  notes: "Handle with care"
}
```

### After (Simplified)
```javascript
const orderForm = {
  sender_address: 1,                    // From user's saved addresses
  recipient_phone: "+998901234567",     // Recipient contact
  recipient_address: "123 Main Street", // Full recipient address
  weight_kg: 2.5                        // Package weight in kg
}
```

## Create Order
```javascript
async function createOrder(orderData) {
  const response = await fetch('/api/v1/orders/create/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`
    },
    body: JSON.stringify({
      sender_address: orderData.pickupAddressId,  // Selected saved address ID
      recipient_phone: orderData.recipientPhone,   // Format: +998XXXXXXXXX
      recipient_address: orderData.recipientAddress, // Complete address
      weight_kg: parseFloat(orderData.weight)       // Numeric value
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    console.error('Order creation failed:', error.details || error.error);
    return null;
  }
  
  const order = await response.json();
  console.log('Order created:', order.order_number);
  return order;
}
```

## Form HTML Examples

### Address Form
```html
<form id="addressForm">
  <div class="form-group">
    <label for="title">Address Label (e.g., Home, Office)</label>
    <input type="text" id="title" name="title" required 
           placeholder="Home" maxlength="100">
  </div>

  <div class="form-group">
    <label for="fullAddress">Full Address</label>
    <textarea id="fullAddress" name="fullAddress" required 
              placeholder="e.g., Apartment 10, Navoi Street, Tashkent, 100100"
              rows="3"></textarea>
  </div>

  <div class="form-group">
    <label>
      <input type="checkbox" id="isDefault" name="isDefault">
      Set as default pickup address
    </label>
  </div>

  <button type="submit" class="btn btn-primary">Save Address</button>
</form>

<script>
  document.getElementById('addressForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const result = await saveAddress({
      title: document.getElementById('title').value,
      fullAddress: document.getElementById('fullAddress').value,
      isDefault: document.getElementById('isDefault').checked
    });
    
    if (result) {
      alert('Address saved successfully!');
      // Refresh address list
      loadAddresses();
    }
  });
</script>
```

### Order Form
```html
<form id="orderForm">
  <div class="form-group">
    <label for="senderAddress">Pickup Location</label>
    <select id="senderAddress" name="senderAddress" required>
      <option value="">Select a saved address</option>
      <!-- Populated by JavaScript -->
    </select>
  </div>

  <div class="form-group">
    <label for="recipientPhone">Recipient Phone Number</label>
    <input type="tel" id="recipientPhone" name="recipientPhone" required
           placeholder="+998901234567" pattern="\+998[0-9]{9}">
  </div>

  <div class="form-group">
    <label for="recipientAddress">Delivery Address</label>
    <textarea id="recipientAddress" name="recipientAddress" required
              placeholder="Full address for delivery" rows="3"></textarea>
  </div>

  <div class="form-group">
    <label for="weight">Weight (kg)</label>
    <input type="number" id="weight" name="weight" required 
           min="0.1" step="0.1" placeholder="2.5">
  </div>

  <button type="submit" class="btn btn-primary">Create Order</button>
</form>

<script>
  // Load addresses on page load
  async function populateAddresses() {
    const addresses = await loadAddresses();
    const select = document.getElementById('senderAddress');
    
    addresses.forEach(addr => {
      const option = document.createElement('option');
      option.value = addr.id;
      option.textContent = `${addr.title} - ${addr.full_address}`;
      select.appendChild(option);
    });
  }

  document.getElementById('orderForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const result = await createOrder({
      pickupAddressId: parseInt(document.getElementById('senderAddress').value),
      recipientPhone: document.getElementById('recipientPhone').value,
      recipientAddress: document.getElementById('recipientAddress').value,
      weight: document.getElementById('weight').value
    });
    
    if (result) {
      alert(`Order created: ${result.order_number}`);
      // Redirect to order detail page
      window.location.href = `/order-tracking/${result.order_number}/`;
    }
  });

  // Load addresses on page load
  window.addEventListener('load', populateAddresses);
</script>
```

## Response Examples

### Address Response
```json
{
  "id": 5,
  "title": "Home",
  "full_address": "Apartment 10, Navoi Street, Tashkent, Uzbekistan",
  "is_default": true,
  "created_at": "2026-04-27T14:30:21.020462+05:00",
  "updated_at": "2026-04-27T14:30:21.020483+05:00"
}
```

### Order Response
```json
{
  "order_number": "PS-2026-TAS-274170",
  "sender_address": 5,
  "recipient_phone": "+998901234568",
  "recipient_address": "123 Main Street, Samarkand, Uzbekistan",
  "weight_kg": "2.50",
  "status": "pending",
  "price": "70000.00",
  "estimated_delivery": null,
  "created_at": "2026-04-27T14:30:21.056783+05:00"
}
```

## Error Handling

### Address Creation Error
```javascript
async function saveAddress(addressData) {
  const response = await fetch('/api/v1/users/addresses/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`
    },
    body: JSON.stringify(addressData)
  });
  
  if (!response.ok) {
    if (response.status === 400) {
      const error = await response.json();
      // Display user-friendly error
      console.error('Validation error:', error.details || error.error);
      alert(`Error: ${error.error}\nDetails: ${error.details}`);
    } else if (response.status === 401) {
      alert('Your session has expired. Please log in again.');
      // Redirect to login
    } else {
      alert('An error occurred. Please try again later.');
    }
    return null;
  }
  
  return await response.json();
}
```

## Summary of Changes

| Field | Old Form | New Form |
|-------|----------|----------|
| Region | Required select | ✗ Removed |
| City | Required select | ✗ Removed |
| Address | TextField | ✗ Merged to full_address |
| Landmark | TextField | ✗ Merged to full_address |
| Full Address | N/A | ✓ Single text area |
| Service Type | Select dropdown | ✓ Default "standard" (optional) |
| Notes | Text area | ✓ Optional (removed from form) |
| Region Selection | Required for orders | ✓ Optional backend (removed from form) |

## Benefits

✅ **Simpler UX** - No cascading dropdowns  
✅ **Faster loading** - No need to fetch region/city data  
✅ **Fewer validation errors** - Less validation required  
✅ **Better mobile experience** - Less tapping/scrolling  
✅ **More flexible** - Users can enter any address text

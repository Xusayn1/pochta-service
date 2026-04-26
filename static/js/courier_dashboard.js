let courierOrdersState = {
  available_orders: [],
  assigned_orders: [],
  history_orders: []
};
let selectedFilter = "all";
let activeOrderId = null;

function getAccessToken() {
  return localStorage.getItem("access_token");
}

function getCsrfToken() {
  const match = document.cookie.match(/(^|;)\s*csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[2]) : "";
}

async function apiRequest(url, options = {}) {
  const token = getAccessToken();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  if ((options.method || "GET") !== "GET") {
    headers["X-CSRFToken"] = getCsrfToken();
  }
  const response = await fetch(url, { ...options, headers });
  let payload = {};
  try {
    payload = await response.json();
  } catch (_error) {
    payload = {};
  }
  if (!response.ok) {
    throw new Error(payload.detail || "Request failed");
  }
  return payload;
}

function bindCursor() {
  const cursor = document.getElementById("cursor");
  const ring = document.getElementById("cursorRing");
  if (!cursor || !ring) {
    return;
  }

  let mx = 0;
  let my = 0;
  let rx = 0;
  let ry = 0;
  document.addEventListener("mousemove", function (e) {
    mx = e.clientX;
    my = e.clientY;
  });

  (function animCursor() {
    rx += (mx - rx) * 0.15;
    ry += (my - ry) * 0.15;
    cursor.style.left = `${mx}px`;
    cursor.style.top = `${my}px`;
    ring.style.left = `${rx}px`;
    ring.style.top = `${ry}px`;
    requestAnimationFrame(animCursor);
  })();
}

function bindHoverCursorTargets() {
  const cursor = document.getElementById("cursor");
  const ring = document.getElementById("cursorRing");
  if (!cursor || !ring) {
    return;
  }
  document.querySelectorAll("a, button, .order-card, .stat-card, label").forEach(function (el) {
    el.addEventListener("mouseenter", function () {
      cursor.style.transform = "translate(-50%,-50%) scale(1.8)";
      ring.style.width = "56px";
      ring.style.height = "56px";
      ring.style.opacity = "0.3";
    });
    el.addEventListener("mouseleave", function () {
      cursor.style.transform = "translate(-50%,-50%) scale(1)";
      ring.style.width = "36px";
      ring.style.height = "36px";
      ring.style.opacity = "0.6";
    });
  });
}

function orderTypeClass(serviceType) {
  if (serviceType === "express") return "express";
  if (serviceType === "fragile") return "fragile";
  return "standard";
}

function renderAvailableOrders() {
  const container = document.getElementById("orders-container");
  if (!container) {
    return;
  }

  const filtered = courierOrdersState.available_orders.filter(function (order) {
    if (selectedFilter === "all") return true;
    return order.service_type === selectedFilter;
  });

  if (!filtered.length) {
    container.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <div class="empty-icon">📭</div>
        <div class="empty-title">No available orders</div>
        <div class="empty-sub">Try another filter or check again in a moment.</div>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(function (order) {
    const typeClass = orderTypeClass(order.service_type);
    return `
      <div class="order-card" data-type="${order.service_type}">
        <div class="order-header">
          <div class="order-id">${order.order_number || "#" + order.id}</div>
          <div class="order-type ${typeClass}">${order.service_type}</div>
        </div>
        <div class="order-meta" style="border-top:0; padding-top:0;">
          <div class="meta-item">
            <div class="meta-label">Customer</div>
            <div class="meta-val">${order.customer_name}</div>
          </div>
          <div class="meta-item">
            <div class="meta-label">Phone</div>
            <div class="meta-val">${order.phone}</div>
          </div>
          <div class="meta-item">
            <div class="meta-label">Status</div>
            <div class="meta-val"><strong>${order.status}</strong></div>
          </div>
        </div>
        <div class="route-label">Address</div>
        <div class="route-addr" style="margin-bottom:1rem;">${order.address}</div>
        <div class="order-actions">
          <button class="btn-take" onclick="acceptOrder(${order.id})"><span>Accept</span></button>
        </div>
      </div>
    `;
  }).join("");
}

function renderAssignedOrders() {
  const container = document.getElementById("active-order-container");
  const emptyState = document.getElementById("noActiveDelivery");
  if (!container || !emptyState) {
    return;
  }

  if (!courierOrdersState.assigned_orders.length) {
    container.innerHTML = "";
    emptyState.style.display = "block";
    return;
  }

  emptyState.style.display = "none";
  container.innerHTML = courierOrdersState.assigned_orders.map(function (order) {
    return `
      <div class="active-delivery fade-in delay-1">
        <div class="active-delivery-header">
          <div class="active-label">
            <div class="active-dot"></div>
            Currently Delivering
          </div>
        </div>
        <div class="active-delivery-grid">
          <div class="active-order-info">
            <div class="active-order-id">${order.order_number || "#" + order.id}</div>
            <div class="active-customer">Customer: ${order.customer_name}</div>
            <div class="active-route">
              <div class="active-route-item">
                <div class="active-route-icon">
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="rgba(201,168,76,0.7)" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                </div>
                <div class="active-route-text">
                  <div class="active-route-label">Delivering To</div>
                  <div class="active-route-addr">${order.address}</div>
                </div>
              </div>
              <div class="active-route-item">
                <div class="active-route-icon done">☎</div>
                <div class="active-route-text">
                  <div class="active-route-label">Recipient Phone</div>
                  <div class="active-route-addr">${order.phone}</div>
                </div>
              </div>
            </div>
          </div>
          <div class="delivery-progress">
            <div class="progress-steps">
              <div class="progress-step done">
                <div class="progress-step-dot">✓</div>
                <div class="progress-step-info">
                  <div class="progress-step-title">Order Accepted</div>
                  <div class="progress-step-time">In progress</div>
                </div>
              </div>
              <div class="progress-step current">
                <div class="progress-step-dot">→</div>
                <div class="progress-step-info">
                  <div class="progress-step-title">Out for Delivery</div>
                  <div class="progress-step-time">Current status: ${order.status}</div>
                </div>
              </div>
            </div>
          </div>
          <div class="active-actions">
            <div class="active-actions-title">Actions</div>
            <button class="btn-delivered" onclick="openDeliverModal(${order.id})"><span>✓ Mark as Delivered</span></button>
            <button class="btn-issue" onclick="cancelOrder(${order.id})">Cancel Order</button>
          </div>
        </div>
      </div>
    `;
  }).join("");
}

function updateBadges() {
  const availableBadge = document.getElementById("badge-available");
  if (availableBadge) {
    availableBadge.textContent = courierOrdersState.available_orders.length || "";
  }
  const activeBadge = document.getElementById("badge-active");
  if (activeBadge) {
    activeBadge.textContent = courierOrdersState.assigned_orders.length || "";
  }
}

async function loadOrders() {
  try {
    const payload = await apiRequest("/api/courier/orders/");
    courierOrdersState = payload;
    renderAvailableOrders();
    renderAssignedOrders();
    updateBadges();
    bindHoverCursorTargets();
  } catch (error) {
    showToast(error.message || "Unable to load orders.");
  }
}

async function acceptOrder(orderId) {
  try {
    await apiRequest(`/api/courier/orders/${orderId}/accept/`, { method: "POST", body: JSON.stringify({}) });
    showToast("Order accepted.");
    await loadOrders();
  } catch (error) {
    showToast(error.message || "Failed to accept order.");
  }
}

function openDeliverModal(orderId) {
  activeOrderId = orderId;
  openModal("modalDeliver");
}

async function confirmDelivered() {
  if (!activeOrderId) {
    closeModal("modalDeliver");
    return;
  }
  try {
    await apiRequest(`/api/courier/orders/${activeOrderId}/deliver/`, { method: "POST", body: JSON.stringify({}) });
    closeModal("modalDeliver");
    showToast("Order delivered successfully.");
    activeOrderId = null;
    await loadOrders();
  } catch (error) {
    showToast(error.message || "Failed to mark order delivered.");
  }
}

async function cancelOrder(orderId) {
  try {
    await apiRequest(`/api/courier/orders/${orderId}/cancel/`, { method: "POST", body: JSON.stringify({}) });
    showToast("Order cancelled.");
    await loadOrders();
  } catch (error) {
    showToast(error.message || "Failed to cancel order.");
  }
}

function showTab(name) {
  ["available", "active", "history"].forEach(function (t) {
    const el = document.getElementById("tab-" + t);
    if (el) {
      el.style.display = t === name ? "block" : "none";
    }
  });
  document.querySelectorAll(".sidebar-nav a").forEach(function (a) {
    a.classList.remove("active");
  });
  const links = document.querySelectorAll(".sidebar-nav a");
  const tabMap = { available: 0, active: 1, history: 2 };
  if (links[tabMap[name]]) {
    links[tabMap[name]].classList.add("active");
  }
}

function toggleStatus(cb) {
  const status = document.getElementById("statusVal");
  if (status) {
    status.textContent = cb.checked ? "Online" : "Offline";
  }
}

function filterOrders(btn, type) {
  selectedFilter = type;
  document.querySelectorAll(".filter-btn").forEach(function (b) {
    b.classList.remove("active");
  });
  btn.classList.add("active");
  renderAvailableOrders();
}

function showNotif(msg) {
  if (msg) {
    const notifMsg = document.querySelector(".notif-msg");
    if (notifMsg) {
      notifMsg.textContent = msg;
    }
  }
  const banner = document.getElementById("notifBanner");
  if (banner) {
    banner.classList.add("show");
  }
  setTimeout(function () {
    closeNotif();
  }, 6000);
}

function closeNotif() {
  const banner = document.getElementById("notifBanner");
  if (banner) {
    banner.classList.remove("show");
  }
}

function showToast(msg) {
  const t = document.getElementById("toast");
  const text = document.getElementById("toastMsg");
  if (!t || !text) {
    return;
  }
  text.textContent = msg;
  t.classList.add("show");
  setTimeout(function () {
    t.classList.remove("show");
  }, 3500);
}

function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.classList.add("open");
  }
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.classList.remove("open");
  }
}

document.addEventListener("DOMContentLoaded", function () {
  bindCursor();
  document.querySelectorAll(".modal-overlay").forEach(function (overlay) {
    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) {
        overlay.classList.remove("open");
      }
    });
  });
  loadOrders();
  setTimeout(function () {
    showNotif("Courier dashboard connected. Loading live orders.");
  }, 1200);
});

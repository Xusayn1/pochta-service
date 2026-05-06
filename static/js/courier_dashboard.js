const DASHBOARD_SETTINGS_KEY = "courier_dashboard_settings";
const DEFAULT_SETTINGS = {
  online: true,
  newOrderAlerts: true,
  deliveryReminders: true,
  earningsSummaries: false,
};

let courierOrdersState = {
  available_orders: [],
  assigned_orders: [],
  history_orders: [],
  summary: {},
};
let selectedFilter = "all";
let activeOrderId = null;
let modalOrderId = null;

function getAccessToken() {
  return localStorage.getItem("access_token");
}

function getCurrentRole() {
  return localStorage.getItem("user_role");
}

function getCsrfToken() {
  const match = document.cookie.match(/(^|;)\s*csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[2]) : "";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function titleCase(value) {
  return String(value || "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString("en-US", {
    maximumFractionDigits: 0,
  });
}

function formatCurrency(value) {
  return `UZS ${formatNumber(value)}`;
}

function formatDate(value) {
  if (!value) {
    return "-";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "-";
  }

  return date.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function shortenAddress(address, maxLength = 46) {
  const safeAddress = String(address || "").trim();
  if (!safeAddress) {
    return "Address not provided";
  }
  return safeAddress.length > maxLength
    ? `${safeAddress.slice(0, maxLength - 3)}...`
    : safeAddress;
}

function setStatValue(id, primary, suffix = "") {
  const element = document.getElementById(id);
  if (!element) {
    return;
  }

  const safePrimary = escapeHtml(primary);
  const safeSuffix = escapeHtml(suffix);
  element.innerHTML = safeSuffix
    ? `<span>${safePrimary}</span><span style="font-size:1.2rem">${safeSuffix}</span>`
    : `<span>${safePrimary}</span>`;
}

function readDashboardSettings() {
  try {
    const raw = localStorage.getItem(DASHBOARD_SETTINGS_KEY);
    const parsed = raw ? JSON.parse(raw) : {};
    return { ...DEFAULT_SETTINGS, ...parsed };
  } catch (_error) {
    return { ...DEFAULT_SETTINGS };
  }
}

function persistDashboardSettings(settings) {
  localStorage.setItem(DASHBOARD_SETTINGS_KEY, JSON.stringify(settings));
}

function signOut() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user_role");
  localStorage.removeItem("phone");
  window.location.href = "/login/";
}

Object.assign(window, {
  showTab,
  toggleStatus,
  filterOrders,
  closeNotif,
  closeModal,
  acceptOrderFromModal,
  confirmDelivered,
  loadProfile,
  saveSettings,
  signOut,
  openDeliverModal,
  openOrderDetails,
  acceptOrder,
  cancelOrder,
});

async function apiRequest(url, options = {}) {
  const token = getAccessToken();
  const method = options.method || "GET";
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  if (method !== "GET") {
    headers["X-CSRFToken"] = getCsrfToken();
  }

  const response = await fetch(url, { ...options, headers });
  let payload = {};

  try {
    payload = await response.json();
  } catch (_error) {
    payload = {};
  }

  if (response.status === 401) {
    signOut();
    throw new Error("Session expired. Please login again.");
  }

  if (!response.ok) {
    throw new Error(payload.detail || payload.error || payload.message || "Request failed.");
  }

  return payload;
}

function bindCursor() {
  const cursor = document.getElementById("cursor");
  const ring = document.getElementById("cursorRing");
  if (!cursor || !ring) {
    return;
  }

  let mouseX = 0;
  let mouseY = 0;
  let ringX = 0;
  let ringY = 0;

  document.addEventListener("mousemove", (event) => {
    mouseX = event.clientX;
    mouseY = event.clientY;
  });

  (function animateCursor() {
    ringX += (mouseX - ringX) * 0.15;
    ringY += (mouseY - ringY) * 0.15;

    cursor.style.left = `${mouseX}px`;
    cursor.style.top = `${mouseY}px`;
    ring.style.left = `${ringX}px`;
    ring.style.top = `${ringY}px`;

    requestAnimationFrame(animateCursor);
  })();
}

function bindHoverCursorTargets() {
  const cursor = document.getElementById("cursor");
  const ring = document.getElementById("cursorRing");
  if (!cursor || !ring) {
    return;
  }

  document.querySelectorAll("a, button, .order-card, .stat-card, label").forEach((element) => {
    element.addEventListener("mouseenter", () => {
      cursor.style.transform = "translate(-50%,-50%) scale(1.8)";
      ring.style.width = "56px";
      ring.style.height = "56px";
      ring.style.opacity = "0.3";
    });

    element.addEventListener("mouseleave", () => {
      cursor.style.transform = "translate(-50%,-50%) scale(1)";
      ring.style.width = "36px";
      ring.style.height = "36px";
      ring.style.opacity = "0.6";
    });
  });
}

function getOrderTypeClass(serviceType) {
  if (serviceType === "express") {
    return "express";
  }
  if (serviceType === "fragile") {
    return "fragile";
  }
  return "standard";
}

function getAllOrders() {
  return [
    ...courierOrdersState.available_orders,
    ...courierOrdersState.assigned_orders,
    ...courierOrdersState.history_orders,
  ];
}

function getOrderById(orderId) {
  return getAllOrders().find((order) => order.id === orderId) || null;
}

function buildRouteLabel(order) {
  return `${shortenAddress(order.pickup_address)} -> ${shortenAddress(order.address)}`;
}

function updateAvailableSubtitle() {
  const subtitle = document.getElementById("available-subtitle");
  if (!subtitle) {
    return;
  }

  const count = courierOrdersState.available_orders.length;
  subtitle.textContent = count
    ? `${count} orders ready near your area right now`
    : "No nearby orders are waiting right now";
}

function renderSummary() {
  const summary = courierOrdersState.summary || {};

  setStatValue("summary-today-deliveries", formatNumber(summary.today_deliveries || 0));
  setStatValue("summary-today-earnings", formatNumber(summary.today_earnings || 0));
  setStatValue("summary-completion-rate", formatNumber(summary.completion_rate || 100), "%");

  setStatValue("history-total-delivered", formatNumber(summary.total_deliveries || 0));
  setStatValue(
    "history-month-delivered",
    formatNumber(getDeliveredCountForCurrentMonth(courierOrdersState.history_orders))
  );
  setStatValue("history-total-earnings", formatNumber(summary.total_earnings || 0));
  setStatValue("history-completion-rate", formatNumber(summary.completion_rate || 100), "%");

  setStatValue("earn-month", formatNumber(summary.monthly_earnings || 0));
  setStatValue("earn-total-deliveries", formatNumber(summary.total_deliveries || 0));
  setStatValue("earn-avg", formatNumber(summary.average_earnings || 0));

  updateAvailableSubtitle();
}

function renderAvailableOrders() {
  const container = document.getElementById("orders-container");
  if (!container) {
    return;
  }

  const filteredOrders = courierOrdersState.available_orders.filter((order) => {
    if (selectedFilter === "all") {
      return true;
    }
    return order.service_type === selectedFilter;
  });

  if (!filteredOrders.length) {
    container.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <div class="empty-icon">Pending</div>
        <div class="empty-title">No available orders</div>
        <div class="empty-sub">Try another filter or check again in a moment.</div>
      </div>
    `;
    return;
  }

  container.innerHTML = filteredOrders.map((order) => {
    const typeClass = getOrderTypeClass(order.service_type);
    return `
      <div class="order-card" data-type="${escapeHtml(order.service_type)}">
        <div class="order-header">
          <div class="order-id">${escapeHtml(order.order_number || `#${order.id}`)}</div>
          <div class="order-type ${escapeHtml(typeClass)}">${escapeHtml(titleCase(order.service_type))}</div>
        </div>
        <div class="order-meta" style="border-top:0; padding-top:0;">
          <div class="meta-item">
            <div class="meta-label">Customer</div>
            <div class="meta-val">${escapeHtml(order.customer_name || "Customer")}</div>
          </div>
          <div class="meta-item">
            <div class="meta-label">Phone</div>
            <div class="meta-val">${escapeHtml(order.phone || "-")}</div>
          </div>
          <div class="meta-item">
            <div class="meta-label">Payout</div>
            <div class="meta-val"><strong>${escapeHtml(formatCurrency(order.price || 0))}</strong></div>
          </div>
        </div>
        <div class="route-label">Destination</div>
        <div class="route-addr" style="margin-bottom:0.5rem;">${escapeHtml(shortenAddress(order.address, 84))}</div>
        <div class="route-label">Pickup</div>
        <div class="route-addr" style="margin-bottom:1rem;">${escapeHtml(shortenAddress(order.pickup_address, 84))}</div>
        <div class="order-actions">
          <button class="btn-details" onclick="openOrderDetails(${order.id})">Details</button>
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
  container.innerHTML = courierOrdersState.assigned_orders.map((order) => `
    <div class="active-delivery fade-in delay-1">
      <div class="active-delivery-header">
        <div class="active-label">
          <div class="active-dot"></div>
          Currently Delivering
        </div>
      </div>
      <div class="active-delivery-grid">
        <div class="active-order-info">
          <div class="active-order-id">${escapeHtml(order.order_number || `#${order.id}`)}</div>
          <div class="active-customer">Customer: ${escapeHtml(order.customer_name || "Customer")}</div>
          <div class="active-route">
            <div class="active-route-item">
              <div class="active-route-icon">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="rgba(201,168,76,0.7)" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
              </div>
              <div class="active-route-text">
                <div class="active-route-label">Delivering To</div>
                <div class="active-route-addr">${escapeHtml(order.address || "Address not provided")}</div>
              </div>
            </div>
            <div class="active-route-item">
              <div class="active-route-icon done">Call</div>
              <div class="active-route-text">
                <div class="active-route-label">Recipient Phone</div>
                <div class="active-route-addr">${escapeHtml(order.phone || "-")}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="delivery-progress">
          <div class="progress-steps">
            <div class="progress-step done">
              <div class="progress-step-dot">OK</div>
              <div class="progress-step-info">
                <div class="progress-step-title">Order Accepted</div>
                <div class="progress-step-time">${escapeHtml(formatDate(order.created_at))}</div>
              </div>
            </div>
            <div class="progress-step current">
              <div class="progress-step-dot">Go</div>
              <div class="progress-step-info">
                <div class="progress-step-title">Out for Delivery</div>
                <div class="progress-step-time">Current status: ${escapeHtml(titleCase(order.status))}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="active-actions">
          <div class="active-actions-title">Actions</div>
          <button class="btn-delivered" onclick="openDeliverModal(${order.id})"><span>Mark as Delivered</span></button>
          <button class="btn-issue" onclick="cancelOrder(${order.id})">Cancel Order</button>
          <button class="btn-contact" onclick="openOrderDetails(${order.id})">Review Details</button>
        </div>
      </div>
    </div>
  `).join("");
}

function getDeliveredCountForCurrentMonth(orders) {
  const now = new Date();
  return orders.filter((order) => {
    if (order.status !== "delivered" || !order.delivered_at) {
      return false;
    }
    const deliveredAt = new Date(order.delivered_at);
    return deliveredAt.getFullYear() === now.getFullYear() && deliveredAt.getMonth() === now.getMonth();
  }).length;
}

function renderHistory() {
  const tbody = document.getElementById("history-orders-tbody");
  if (!tbody) {
    return;
  }

  const historyOrders = courierOrdersState.history_orders;
  if (!historyOrders.length) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align:center;opacity:0.4;padding:2rem">No completed or cancelled deliveries yet.</td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = historyOrders.map((order) => {
    const statusClass = order.status === "delivered" ? "delivered" : "cancelled";
    const earned = order.status === "delivered" ? formatCurrency(order.price || 0) : "-";
    return `
      <tr>
        <td><span class="td-id">${escapeHtml(order.order_number || `#${order.id}`)}</span></td>
        <td>${escapeHtml(buildRouteLabel(order))}</td>
        <td>${escapeHtml(titleCase(order.service_type))}</td>
        <td>${escapeHtml(formatDate(order.delivered_at || order.updated_at))}</td>
        <td style="color:${order.status === "delivered" ? "var(--gold)" : "rgba(255,255,255,0.3)"}">${escapeHtml(earned)}</td>
        <td><span class="status-pill ${escapeHtml(statusClass)}">${escapeHtml(titleCase(order.status))}</span></td>
      </tr>
    `;
  }).join("");
}

function renderEarnings() {
  const tbody = document.getElementById("earnings-history-tbody");
  if (!tbody) {
    return;
  }

  const historyOrders = courierOrdersState.history_orders;
  if (!historyOrders.length) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align:center;opacity:0.4;padding:2rem">No payout history yet.</td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = historyOrders.map((order) => {
    const statusClass = order.status === "delivered" ? "delivered" : "cancelled";
    const earned = order.status === "delivered" ? formatCurrency(order.price || 0) : "-";
    return `
      <tr>
        <td><span class="td-id">${escapeHtml(order.order_number || `#${order.id}`)}</span></td>
        <td>${escapeHtml(buildRouteLabel(order))}</td>
        <td>${escapeHtml(titleCase(order.service_type))}</td>
        <td>${escapeHtml(formatDate(order.delivered_at || order.updated_at))}</td>
        <td style="color:${order.status === "delivered" ? "var(--gold)" : "rgba(255,255,255,0.3)"}">${escapeHtml(earned)}</td>
        <td><span class="status-pill ${escapeHtml(statusClass)}">${escapeHtml(titleCase(order.status))}</span></td>
      </tr>
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

function updateStatusDisplay(isOnline) {
  const statusLabel = document.getElementById("statusVal");
  const badge = document.querySelector(".nav-courier-badge");
  const roleDisplay = document.getElementById("profile-role-display");

  if (statusLabel) {
    statusLabel.textContent = isOnline ? "Online" : "Offline";
  }

  if (badge) {
    badge.textContent = isOnline ? "Online · Tashkent" : "Offline · Tashkent";
  }

  if (roleDisplay) {
    roleDisplay.textContent = isOnline ? "Courier · Active" : "Courier · Offline";
  }
}

function applySettingsToForm() {
  const settings = readDashboardSettings();
  const statusToggle = document.getElementById("statusToggle");
  const newOrderAlerts = document.getElementById("setting-new-order-alerts");
  const deliveryReminders = document.getElementById("setting-delivery-reminders");
  const earningsSummaries = document.getElementById("setting-earnings-summaries");

  if (statusToggle) {
    statusToggle.checked = settings.online;
  }
  if (newOrderAlerts) {
    newOrderAlerts.checked = settings.newOrderAlerts;
  }
  if (deliveryReminders) {
    deliveryReminders.checked = settings.deliveryReminders;
  }
  if (earningsSummaries) {
    earningsSummaries.checked = settings.earningsSummaries;
  }

  updateStatusDisplay(settings.online);
}

function saveSettings() {
  const statusToggle = document.getElementById("statusToggle");
  const newOrderAlerts = document.getElementById("setting-new-order-alerts");
  const deliveryReminders = document.getElementById("setting-delivery-reminders");
  const earningsSummaries = document.getElementById("setting-earnings-summaries");

  const settings = {
    online: Boolean(statusToggle?.checked),
    newOrderAlerts: Boolean(newOrderAlerts?.checked),
    deliveryReminders: Boolean(deliveryReminders?.checked),
    earningsSummaries: Boolean(earningsSummaries?.checked),
  };

  persistDashboardSettings(settings);
  updateStatusDisplay(settings.online);
  showToast("Preferences saved.");
}

function showTab(name, updateHash = true) {
  const allTabs = ["available", "active", "history", "earnings", "profile", "settings"];
  const targetTab = allTabs.includes(name) ? name : "available";

  allTabs.forEach((tabName) => {
    const element = document.getElementById(`tab-${tabName}`);
    if (element) {
      element.style.display = tabName === targetTab ? "block" : "none";
    }
  });

  document.querySelectorAll(".sidebar-nav a").forEach((link) => {
    link.classList.toggle("active", link.dataset.tab === targetTab);
  });

  if (updateHash) {
    window.history.replaceState(null, "", `#${targetTab}`);
  }

  if (targetTab === "history") {
    renderHistory();
  }
  if (targetTab === "earnings") {
    renderEarnings();
  }
  if (targetTab === "profile") {
    loadProfile();
  }
}

function showTabFromHash() {
  const requestedTab = window.location.hash.replace("#", "");
  showTab(requestedTab || "available", false);
}

function toggleStatus(checkbox) {
  const settings = readDashboardSettings();
  settings.online = Boolean(checkbox?.checked);
  persistDashboardSettings(settings);
  updateStatusDisplay(settings.online);
}

function filterOrders(button, type) {
  selectedFilter = type;
  document.querySelectorAll(".filter-btn").forEach((filterButton) => {
    filterButton.classList.remove("active");
  });
  if (button) {
    button.classList.add("active");
  }
  renderAvailableOrders();
}

function showNotif(message) {
  const settings = readDashboardSettings();
  if (!settings.newOrderAlerts) {
    return;
  }

  const messageElement = document.querySelector(".notif-msg");
  const banner = document.getElementById("notifBanner");
  if (messageElement && message) {
    messageElement.textContent = message;
  }
  if (banner) {
    banner.classList.add("show");
  }

  setTimeout(() => {
    closeNotif();
  }, 6000);
}

function closeNotif() {
  const banner = document.getElementById("notifBanner");
  if (banner) {
    banner.classList.remove("show");
  }
}

function showToast(message) {
  const toast = document.getElementById("toast");
  const toastText = document.getElementById("toastMsg");
  if (!toast || !toastText) {
    return;
  }

  toastText.textContent = message;
  toast.classList.add("show");
  setTimeout(() => {
    toast.classList.remove("show");
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

function populateOrderDetailsModal(order) {
  document.getElementById("modalOrderId").textContent = order.order_number || `#${order.id}`;
  document.getElementById("md-type").textContent = titleCase(order.service_type);
  document.getElementById("md-from").textContent = order.pickup_address || "Pickup address not provided";
  document.getElementById("md-to").textContent = order.address || "Delivery address not provided";
  document.getElementById("md-weight").textContent = `${Number(order.weight_kg || 0).toFixed(1)} kg`;
  document.getElementById("md-dist").textContent = order.region || "Route assigned";
  document.getElementById("md-customer").textContent = order.customer_name || order.recipient_name || "Customer";
  document.getElementById("md-earn").textContent = formatCurrency(order.price || 0);
}

function openOrderDetails(orderId) {
  const order = getOrderById(orderId);
  if (!order) {
    showToast("Order details are not available right now.");
    return;
  }

  modalOrderId = orderId;
  populateOrderDetailsModal(order);
  openModal("modalOrderDetails");
}

async function acceptOrder(orderId) {
  try {
    await apiRequest(`/api/courier/orders/${orderId}/accept/`, {
      method: "POST",
      body: JSON.stringify({}),
    });
    closeModal("modalOrderDetails");
    showToast("Order accepted.");
    await loadOrders();
    showTab("active");
  } catch (error) {
    showToast(error.message || "Failed to accept order.");
  }
}

function acceptOrderFromModal() {
  if (!modalOrderId) {
    closeModal("modalOrderDetails");
    return;
  }

  acceptOrder(modalOrderId);
}

function populateDeliverModal(order) {
  document.getElementById("deliver-earnings").textContent = formatCurrency(order.price || 0);
  document.getElementById("deliver-order-id").textContent = order.order_number || `#${order.id}`;
  document.getElementById("deliver-recipient").textContent = order.recipient_name || order.customer_name || "Recipient";
  document.getElementById("deliver-address").textContent = order.address || "Delivery address not provided";
}

function openDeliverModal(orderId) {
  const order = getOrderById(orderId);
  if (!order) {
    showToast("Delivery details are not available right now.");
    return;
  }

  activeOrderId = orderId;
  populateDeliverModal(order);
  openModal("modalDeliver");
}

async function confirmDelivered() {
  if (!activeOrderId) {
    closeModal("modalDeliver");
    return;
  }

  try {
    await apiRequest(`/api/courier/orders/${activeOrderId}/deliver/`, {
      method: "POST",
      body: JSON.stringify({}),
    });
    closeModal("modalDeliver");
    activeOrderId = null;
    showToast("Order delivered successfully.");
    await loadOrders();
    showTab("history");
  } catch (error) {
    showToast(error.message || "Failed to mark order delivered.");
  }
}

async function cancelOrder(orderId) {
  if (!window.confirm("Cancel this order?")) {
    return;
  }

  try {
    await apiRequest(`/api/courier/orders/${orderId}/cancel/`, {
      method: "POST",
      body: JSON.stringify({}),
    });
    showToast("Order cancelled.");
    await loadOrders();
  } catch (error) {
    showToast(error.message || "Failed to cancel order.");
  }
}

function renderProfile(profile) {
  const settings = readDashboardSettings();
  const displayName = profile.full_name || profile.username || profile.phone || "Courier";
  const initials = displayName
    .split(" ")
    .filter(Boolean)
    .map((word) => word[0])
    .join("")
    .toUpperCase()
    .slice(0, 2) || "CR";

  const avatarElement = document.getElementById("profile-avatar-text");
  const nameElement = document.getElementById("profile-name-display");
  const phoneElement = document.getElementById("profile-phone");
  const emailElement = document.getElementById("profile-email");
  const usernameElement = document.getElementById("profile-username");
  const roleElement = document.getElementById("profile-role-display");
  const sidebarName = document.querySelector(".courier-name");
  const sidebarAvatar = document.querySelector(".courier-avatar");

  if (avatarElement) {
    avatarElement.textContent = initials;
  }
  if (nameElement) {
    nameElement.textContent = displayName;
  }
  if (phoneElement) {
    phoneElement.textContent = profile.phone || "-";
  }
  if (emailElement) {
    emailElement.textContent = profile.email || "-";
  }
  if (usernameElement) {
    usernameElement.textContent = profile.username || "-";
  }
  if (roleElement) {
    roleElement.textContent = `${titleCase(profile.role)} · ${settings.online ? "Active" : "Offline"}`;
  }
  if (sidebarName) {
    sidebarName.textContent = displayName;
  }
  if (sidebarAvatar) {
    sidebarAvatar.textContent = initials;
  }
}

async function loadProfile() {
  try {
    const profile = await apiRequest("/api/v1/users/profile/");
    renderProfile(profile);
  } catch (error) {
    showToast(`Could not load profile: ${error.message}`);
  }
}

async function loadOrders() {
  try {
    const payload = await apiRequest("/api/courier/orders/");
    courierOrdersState = {
      available_orders: payload.available_orders || [],
      assigned_orders: payload.assigned_orders || [],
      history_orders: payload.history_orders || [],
      summary: payload.summary || {},
    };

    renderSummary();
    renderAvailableOrders();
    renderAssignedOrders();
    renderHistory();
    renderEarnings();
    updateBadges();
    bindHoverCursorTargets();
  } catch (error) {
    showToast(error.message || "Unable to load orders.");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  bindCursor();

  const token = getAccessToken();
  const role = getCurrentRole();

  if (!token) {
    window.location.href = "/login/";
    return;
  }

  if (role === "manager") {
    window.location.href = "/custom-admin/";
    return;
  }

  if (role && role !== "courier") {
    window.location.href = "/customer-dashboard/";
    return;
  }

  document.querySelectorAll(".modal-overlay").forEach((overlay) => {
    overlay.addEventListener("click", (event) => {
      if (event.target === overlay) {
        overlay.classList.remove("open");
      }
    });
  });

  window.addEventListener("hashchange", showTabFromHash);

  applySettingsToForm();
  loadProfile();
  loadOrders();
  showTabFromHash();

  setTimeout(() => {
    showNotif("Courier dashboard connected. Loading live orders.");
  }, 1200);
});

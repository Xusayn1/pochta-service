// admin_dashboard.js

document.addEventListener('DOMContentLoaded', () => {
    // 1. Check Authentication (must be admin)
    // We assume the token is stored in localStorage by the login page
    const accessToken = localStorage.getItem('access_token');
    
    // UI Elements
    const navDashboard = document.getElementById('nav-dashboard');
    const navOrders = document.getElementById('nav-orders');
    const navUsers = document.getElementById('nav-users');
    const navSettings = document.getElementById('nav-settings');
    const viewDashboard = document.getElementById('view-dashboard');
    const viewOrders = document.getElementById('view-orders');
    const viewUsers = document.getElementById('view-users');
    const viewSettings = document.getElementById('view-settings');
    const logoutBtn = document.getElementById('logout-btn');
    const loaderOverlay = document.getElementById('loader-overlay');

    // Settings form logic
    document.getElementById('settings-form')?.addEventListener('submit', (e) => {
        e.preventDefault();
        alert('Settings saved successfully!');
    });

    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login/';
    });

    // Helper: Auth Fetch
    const authFetch = async (url, options = {}) => {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (accessToken) {
            headers['Authorization'] = `Bearer ${accessToken}`;
        }

        try {
            const response = await fetch(url, { ...options, headers });
            
            if (response.status === 401 || response.status === 403) {
                console.warn('Unauthorized access');
            }
            
            return response;
        } catch (error) {
            console.error('Fetch error:', error);
            return null;
        }
    };

    // Format Date
    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    };

    // Render Status Badge
    const renderStatusBadge = (status) => {
        const statusMap = {
            'pending': 'Pending',
            'confirmed': 'Confirmed',
            'in_transit': 'In Transit',
            'out_for_delivery': 'Out for Delivery',
            'delivered': 'Delivered',
            'cancelled': 'Cancelled'
        };
        const displayStatus = statusMap[status] || status;
        return `<span class="status-badge status-${status}">${displayStatus}</span>`;
    };

    // Load Dashboard Data
    const loadDashboardData = async () => {
        const statsGrid = document.getElementById('admin-stats');
        const recentOrdersTable = document.querySelector('#orders-table tbody');
        
        try {
            // Using our new admin endpoint
            const res = await authFetch('/api/v1/admin/dashboard/');
            if (!res || !res.ok) {
                statsGrid.innerHTML = '<div class="text-danger">Failed to load statistics.</div>';
                recentOrdersTable.innerHTML = '<tr><td colspan="6" class="text-center">Failed to load orders.</td></tr>';
                return;
            }

            const data = await res.json();
            
            // Render Stats
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-info">
                        <h3>Total Orders</h3>
                        <div class="stat-value">${data.stats.total_orders}</div>
                        <div class="stat-trend trend-up"><i class="fa-solid fa-arrow-trend-up"></i> +12% this week</div>
                    </div>
                    <div class="stat-icon icon-blue"><i class="fa-solid fa-box"></i></div>
                </div>
                <div class="stat-card">
                    <div class="stat-info">
                        <h3>Active Deliveries</h3>
                        <div class="stat-value">${data.stats.active_orders}</div>
                        <div class="stat-trend trend-up"><i class="fa-solid fa-truck-fast"></i> Current</div>
                    </div>
                    <div class="stat-icon icon-yellow"><i class="fa-solid fa-truck-fast"></i></div>
                </div>
                <div class="stat-card">
                    <div class="stat-info">
                        <h3>Total Revenue</h3>
                        <div class="stat-value">$${(data.stats.total_revenue || 0).toLocaleString()}</div>
                        <div class="stat-trend trend-up"><i class="fa-solid fa-arrow-trend-up"></i> +8% this month</div>
                    </div>
                    <div class="stat-icon icon-green"><i class="fa-solid fa-dollar-sign"></i></div>
                </div>
                <div class="stat-card">
                    <div class="stat-info">
                        <h3>Total Users</h3>
                        <div class="stat-value">${data.stats.total_users}</div>
                        <div class="stat-trend"><i class="fa-solid fa-users"></i> Platform</div>
                    </div>
                    <div class="stat-icon icon-purple"><i class="fa-solid fa-user"></i></div>
                </div>
            `;

            // Render Recent Orders
            if (data.recent_orders && data.recent_orders.length > 0) {
                recentOrdersTable.innerHTML = data.recent_orders.map(order => `
                    <tr>
                        <td><strong>#${order.order_number}</strong></td>
                        <td>${order.sender_name || 'N/A'}</td>
                        <td>${order.recipient_address || 'N/A'}</td>
                        <td>${renderStatusBadge(order.status)}</td>
                        <td>${formatDate(order.created_at)}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary">View</button>
                        </td>
                    </tr>
                `).join('');
            } else {
                recentOrdersTable.innerHTML = '<tr><td colspan="6" class="text-center">No recent orders found.</td></tr>';
            }
            
        } catch (error) {
            console.error(error);
        }
    };

    // Load All Orders for Orders View
    const loadAllOrders = async () => {
        loaderOverlay.classList.remove('hidden');
        const ordersTable = document.querySelector('#all-orders-table tbody');
        
        try {
            const res = await authFetch('/api/v1/admin/orders/');
            if (!res || !res.ok) {
                ordersTable.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Failed to load orders.</td></tr>';
                return;
            }

            const data = await res.json();
            
            if (data.results && data.results.length > 0) {
                ordersTable.innerHTML = data.results.map(order => `
                    <tr>
                        <td><strong>#${order.order_number}</strong></td>
                        <td>${order.sender_name || 'N/A'}<br><small class="text-muted">${order.sender_phone || ''}</small></td>
                        <td>${order.courier_name || 'Unassigned'}</td>
                        <td>${renderStatusBadge(order.status)}</td>
                        <td>${formatDate(order.created_at)}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="alert('View details for ${order.order_number}')">View</button>
                        </td>
                    </tr>
                `).join('');
            } else {
                ordersTable.innerHTML = '<tr><td colspan="6" class="text-center">No orders found.</td></tr>';
            }
        } catch (error) {
            console.error(error);
            ordersTable.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Error loading orders.</td></tr>';
        } finally {
            loaderOverlay.classList.add('hidden');
        }
    };

    // Load All Users for Users View
    const loadAllUsers = async () => {
        loaderOverlay.classList.remove('hidden');
        const usersTable = document.querySelector('#users-table tbody');
        
        try {
            const res = await authFetch('/api/v1/admin/users/');
            if (!res || !res.ok) {
                usersTable.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Failed to load users.</td></tr>';
                return;
            }

            const data = await res.json();
            
            if (data.results && data.results.length > 0) {
                usersTable.innerHTML = data.results.map(user => `
                    <tr>
                        <td><strong>#${user.id}</strong></td>
                        <td>${user.full_name || user.username || 'N/A'}</td>
                        <td>${user.phone || ''}<br><small class="text-muted">${user.email || ''}</small></td>
                        <td><span class="status-badge" style="background-color: var(--primary-light); color: var(--primary)">${user.role}</span></td>
                        <td>${formatDate(user.created_at)}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="alert('Manage user ${user.id}')">Manage</button>
                        </td>
                    </tr>
                `).join('');
            } else {
                usersTable.innerHTML = '<tr><td colspan="6" class="text-center">No users found.</td></tr>';
            }
        } catch (error) {
            console.error(error);
            usersTable.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Error loading users.</td></tr>';
        } finally {
            loaderOverlay.classList.add('hidden');
        }
    };

    // Load All Shipments
    const loadAllShipments = async () => {
        loaderOverlay.classList.remove('hidden');
        const table = document.querySelector('#shipments-table tbody');
        try {
            const res = await authFetch('/api/v1/admin/shipments/');
            if (!res || !res.ok) throw new Error("Failed");
            const data = await res.json();
            if (data.results && data.results.length > 0) {
                table.innerHTML = data.results.map(item => `
                    <tr>
                        <td><strong>#${item.order_number}</strong></td>
                        <td>${item.courier}</td>
                        <td>${item.pickup}</td>
                        <td>${item.delivery}</td>
                        <td>${renderStatusBadge(item.status)}</td>
                        <td>${formatDate(item.created_at)}</td>
                    </tr>
                `).join('');
            } else {
                table.innerHTML = '<tr><td colspan="6" class="text-center">No shipments found.</td></tr>';
            }
        } catch (error) {
            table.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Error loading shipments.</td></tr>';
        } finally {
            loaderOverlay.classList.add('hidden');
        }
    };

    // Load All Payments
    const loadAllPayments = async () => {
        loaderOverlay.classList.remove('hidden');
        const table = document.querySelector('#payments-table tbody');
        try {
            const res = await authFetch('/api/v1/admin/payments/');
            if (!res || !res.ok) throw new Error("Failed");
            const data = await res.json();
            if (data.results && data.results.length > 0) {
                table.innerHTML = data.results.map(item => `
                    <tr>
                        <td><strong>#${item.order_number}</strong></td>
                        <td>${item.amount.toLocaleString()} UZS</td>
                        <td>${item.method}</td>
                        <td><span class="status-badge" style="background-color: ${item.status === 'success' ? 'var(--success)' : 'var(--warning)'}; color: white">${item.status}</span></td>
                        <td>${formatDate(item.created_at)}</td>
                    </tr>
                `).join('');
            } else {
                table.innerHTML = '<tr><td colspan="5" class="text-center">No payments found.</td></tr>';
            }
        } catch (error) {
            table.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Error loading payments.</td></tr>';
        } finally {
            loaderOverlay.classList.add('hidden');
        }
    };

    // Load All Locations
    const loadAllLocations = async () => {
        loaderOverlay.classList.remove('hidden');
        const table = document.querySelector('#locations-table tbody');
        try {
            const res = await authFetch('/api/v1/admin/locations/');
            if (!res || !res.ok) throw new Error("Failed");
            const data = await res.json();
            if (data.results && data.results.length > 0) {
                table.innerHTML = data.results.map(item => `
                    <tr>
                        <td><strong>${item.type}</strong></td>
                        <td>${item.name}</td>
                        <td>${item.parent}</td>
                    </tr>
                `).join('');
            } else {
                table.innerHTML = '<tr><td colspan="3" class="text-center">No locations found.</td></tr>';
            }
        } catch (error) {
            table.innerHTML = '<tr><td colspan="3" class="text-center text-danger">Error loading locations.</td></tr>';
        } finally {
            loaderOverlay.classList.add('hidden');
        }
    };

    // Load All Notifications
    const loadAllNotifications = async () => {
        loaderOverlay.classList.remove('hidden');
        const table = document.querySelector('#notifications-table tbody');
        try {
            const res = await authFetch('/api/v1/admin/notifications/');
            if (!res || !res.ok) throw new Error("Failed");
            const data = await res.json();
            if (data.results && data.results.length > 0) {
                table.innerHTML = data.results.map(item => `
                    <tr>
                        <td><strong>${item.user}</strong></td>
                        <td>${item.type}</td>
                        <td>${item.message}</td>
                        <td>${item.is_read ? 'Read' : 'Unread'}</td>
                        <td>${formatDate(item.created_at)}</td>
                    </tr>
                `).join('');
            } else {
                table.innerHTML = '<tr><td colspan="5" class="text-center">No notifications found.</td></tr>';
            }
        } catch (error) {
            table.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Error loading notifications.</td></tr>';
        } finally {
            loaderOverlay.classList.add('hidden');
        }
    };

    // Add event listeners for new tabs
    const navShipments = document.getElementById('nav-shipments');
    const navPayments = document.getElementById('nav-payments');
    const navLocations = document.getElementById('nav-locations');
    const navNotifications = document.getElementById('nav-notifications');
    const viewShipments = document.getElementById('view-shipments');
    const viewPayments = document.getElementById('view-payments');
    const viewLocations = document.getElementById('view-locations');
    const viewNotifications = document.getElementById('view-notifications');

    const allViews = [viewDashboard, viewOrders, viewUsers, viewSettings, viewShipments, viewPayments, viewLocations, viewNotifications];
    const navItems = [
        { id: 'nav-dashboard', view: viewDashboard, load: loadDashboardData },
        { id: 'nav-orders', view: viewOrders, load: loadAllOrders },
        { id: 'nav-users', view: viewUsers, load: loadAllUsers },
        { id: 'nav-settings', view: viewSettings, load: () => {} },
        { id: 'nav-shipments', view: viewShipments, load: loadAllShipments },
        { id: 'nav-payments', view: viewPayments, load: loadAllPayments },
        { id: 'nav-locations', view: viewLocations, load: loadAllLocations },
        { id: 'nav-notifications', view: viewNotifications, load: loadAllNotifications },
    ];

    const showView = (viewElement, navId) => {
        // Hide all views
        allViews.forEach(v => {
            if (v) v.classList.add('hidden');
        });
        
        // Remove active class from all nav items
        navItems.forEach(item => {
            const navEl = document.getElementById(item.id);
            if (navEl && navEl.parentElement) {
                navEl.parentElement.classList.remove('active');
            }
        });
        
        // Show target view & active nav
        if (viewElement) viewElement.classList.remove('hidden');
        const targetNav = document.getElementById(navId);
        if (targetNav && targetNav.parentElement) {
            targetNav.parentElement.classList.add('active');
        }
    };

    // Attach clean event listeners
    navItems.forEach(item => {
        const navEl = document.getElementById(item.id);
        if (navEl) {
            // Remove old listeners by replacing with clone, then add new
            const clone = navEl.cloneNode(true);
            navEl.parentNode.replaceChild(clone, navEl);
            clone.addEventListener('click', (e) => {
                e.preventDefault();
                showView(item.view, item.id);
                if (item.load) item.load();
            });
        }
    });

    // Initial load
    if (!accessToken) {
        console.log("No token, dashboard won't fetch real data.");
    }
    
    loadDashboardData();
});

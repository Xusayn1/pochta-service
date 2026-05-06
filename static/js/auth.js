function getStoredToken(key) {
  return localStorage.getItem(key);
}

function extractErrorMessage(data, fallback) {
  if (!data) return fallback;
  if (typeof data.detail === "string") return data.detail;
  if (typeof data.non_field_errors?.[0] === "string") return data.non_field_errors[0];

  const prettifyFieldName = (fieldName) => {
    return fieldName
      .replace(/_/g, " ")
      .replace(/\b\w/g, (char) => char.toUpperCase());
  };

  for (const [field, value] of Object.entries(data)) {
    if (Array.isArray(value) && typeof value[0] === "string") {
      return `${prettifyFieldName(field)}: ${value[0]}`;
    }

    if (typeof value === "string" && value.trim()) {
      return `${prettifyFieldName(field)}: ${value}`;
    }
  }
  return fallback;
}

function setAuthStateNavbar() {
  const isAuth = !!getStoredToken("access_token");
  document.querySelectorAll(".guest-only-link").forEach((el) => {
    el.style.display = isAuth ? "none" : "list-item";
  });
  document.querySelectorAll(".auth-only-link").forEach((el) => {
    el.style.display = isAuth ? "list-item" : "none";
  });
}

async function logoutUser() {
  const refresh = getStoredToken("refresh_token");
  const access = getStoredToken("access_token");

  try {
    await fetch("/api/logout/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(access ? { Authorization: `Bearer ${access}` } : {}),
      },
      body: JSON.stringify({ refresh }),
    });
  } catch (error) {
    console.warn("Logout request failed", error);
  } finally {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user_role");
    setAuthStateNavbar();
    window.location.href = "/";
  }
}

async function submitLoginForm(event) {
  event.preventDefault();
  const identifier = document.querySelector("#identifier")?.value.trim();
  const password = document.querySelector("#password")?.value;
  const errorBox = document.querySelector("#formError");
  if (errorBox) errorBox.textContent = "";

  if (!identifier || !password) {
    if (errorBox) errorBox.textContent = "Please provide credentials.";
    return;
  }

  const response = await fetch("/api/login/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ identifier, password }),
  });
  const data = await response.json();
  if (!response.ok) {
    if (errorBox) errorBox.textContent = extractErrorMessage(data, "Login failed.");
    return;
  }

  localStorage.setItem("access_token", data.access || data.tokens?.access || "");
  localStorage.setItem("refresh_token", data.refresh || data.tokens?.refresh || "");
  localStorage.setItem("user_role", data.user?.role || "user");

  window.location.href = data.redirect_to || (data.user?.role === "courier" ? "/courier-dashboard/" : "/");
}

async function submitRegisterForm(event) {
  event.preventDefault();

  const phone = document.querySelector("#phone")?.value.trim();
  const username = document.querySelector("#username")?.value.trim();
  const email = document.querySelector("#email")?.value.trim();
  const password = document.querySelector("#regPassword")?.value;
  const confirmPassword = document.querySelector("#confirmPassword")?.value;
  const role = document.querySelector("#role")?.value;

  const errorBox = document.querySelector("#formError");
  const successBox = document.querySelector("#formSuccess");
  if (errorBox) errorBox.textContent = "";
  if (successBox) successBox.textContent = "";

  if (!phone || !username || !email || !password || !confirmPassword || !role) {
    if (errorBox) errorBox.textContent = "Please fill in all required fields.";
    return;
  }
  if (password !== confirmPassword) {
    if (errorBox) errorBox.textContent = "Passwords do not match.";
    return;
  }

  const response = await fetch("/api/register/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      phone,
      username,
      email,
      password,
      confirm_password: confirmPassword,
      role,
    }),
  });
  const data = await response.json();
  if (!response.ok) {
    if (errorBox) errorBox.textContent = extractErrorMessage(data, "Registration failed.");
    return;
  }

  localStorage.setItem("access_token", data.access || data.tokens?.access || "");
  localStorage.setItem("refresh_token", data.refresh || data.tokens?.refresh || "");
  localStorage.setItem("user_role", data.user?.role || "user");

  if (successBox) successBox.textContent = "Registration successful. Redirecting...";
  setTimeout(() => {
    window.location.href = data.redirect_to || (data.user?.role === "courier" ? "/courier-dashboard/" : "/");
  }, 500);
}

document.addEventListener("DOMContentLoaded", () => {
  setAuthStateNavbar();
  const pathname = window.location.pathname;
  const isAuth = !!getStoredToken("access_token");
  const role = localStorage.getItem("user_role");

  // Redirect authenticated users away from login/register pages
  if (isAuth && (pathname.startsWith("/login") || pathname.startsWith("/register"))) {
    if (role === "courier") {
      window.location.href = "/courier-dashboard/";
    } else if (role === "manager") {
      window.location.href = "/custom-admin/";
    } else {
      window.location.href = "/customer-dashboard/";
    }
    return;
  }

  const logoutLink = document.querySelector("#logoutLink");
  if (logoutLink) {
    logoutLink.addEventListener("click", (event) => {
      event.preventDefault();
      logoutUser();
    });
  }

  const loginForm = document.querySelector("#loginForm");
  if (loginForm) loginForm.addEventListener("submit", submitLoginForm);

  const registerForm = document.querySelector("#registerForm");
  if (registerForm) registerForm.addEventListener("submit", submitRegisterForm);
});

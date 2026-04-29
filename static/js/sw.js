/**
 * ApexForge Service Worker
 * Offline-first caching for core app shell, static assets, and API responses.
 */

const CACHE_VERSION = "v1";
const APP_SHELL_CACHE = `apexforge-shell-${CACHE_VERSION}`;
const DYNAMIC_CACHE   = `apexforge-dynamic-${CACHE_VERSION}`;
const OFFLINE_URL     = "/offline/";

// Static assets to cache immediately on install
const APP_SHELL_ASSETS = [
  "/",
  "/offline/",
  "https://cdn.tailwindcss.com",
  "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap",
  "https://unpkg.com/htmx.org@1.9.10",
  "https://unpkg.com/alpinejs@3.13.3/dist/cdn.min.js",
  "https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js",
];

// ---------------------------------------------------------------------------
// Install — cache app shell
// ---------------------------------------------------------------------------
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(APP_SHELL_CACHE)
      .then((cache) => cache.addAll(APP_SHELL_ASSETS))
      .then(() => self.skipWaiting())
      .catch((err) => console.warn("[SW] Install cache failed:", err))
  );
});

// ---------------------------------------------------------------------------
// Activate — delete old caches
// ---------------------------------------------------------------------------
self.addEventListener("activate", (event) => {
  const KEEP = [APP_SHELL_CACHE, DYNAMIC_CACHE];
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter((key) => !KEEP.includes(key))
            .map((key) => caches.delete(key))
        )
      )
      .then(() => self.clients.claim())
  );
});

// ---------------------------------------------------------------------------
// Fetch — network-first for navigations, cache-first for static assets
// ---------------------------------------------------------------------------
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET, non-http requests (e.g. chrome-extension://)
  if (request.method !== "GET" || !url.protocol.startsWith("http")) return;

  // Skip Django admin, API calls with side-effects, and HTMX POSTs
  if (
    url.pathname.startsWith("/admin/") ||
    url.pathname.startsWith("/api/") ||
    request.headers.get("HX-Request") // let HTMX always go to network
  ) {
    return;
  }

  // Static assets — cache first, then network
  if (
    url.pathname.startsWith("/static/") ||
    url.hostname === "fonts.googleapis.com" ||
    url.hostname === "fonts.gstatic.com" ||
    url.hostname === "cdn.tailwindcss.com" ||
    url.hostname === "unpkg.com" ||
    url.hostname === "cdn.jsdelivr.net"
  ) {
    event.respondWith(
      caches.match(request).then(
        (cached) =>
          cached ||
          fetch(request).then((response) => {
            if (response.ok) {
              const clone = response.clone();
              caches.open(APP_SHELL_CACHE).then((c) => c.put(request, clone));
            }
            return response;
          })
      )
    );
    return;
  }

  // Navigation / HTML — network first, fall back to cache, then offline page
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const clone = response.clone();
          caches.open(DYNAMIC_CACHE).then((c) => c.put(request, clone));
          return response;
        })
        .catch(() =>
          caches
            .match(request)
            .then((cached) => cached || caches.match(OFFLINE_URL))
        )
    );
    return;
  }

  // Everything else — network first, dynamic cache fallback
  event.respondWith(
    fetch(request)
      .then((response) => {
        if (response.ok) {
          const clone = response.clone();
          caches.open(DYNAMIC_CACHE).then((c) => c.put(request, clone));
        }
        return response;
      })
      .catch(() => caches.match(request))
  );
});

// ---------------------------------------------------------------------------
// Push Notifications
// ---------------------------------------------------------------------------
self.addEventListener("push", (event) => {
  const data = event.data ? event.data.json() : {};
  const title = data.title || "ApexForge";
  const options = {
    body: data.body || "You have a new notification.",
    icon: "/static/img/icon-192.png",
    badge: "/static/img/icon-192.png",
    data: { url: data.url || "/" },
    vibrate: [100, 50, 100],
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const targetUrl = event.notification.data?.url || "/";
  event.waitUntil(
    clients
      .matchAll({ type: "window", includeUncontrolled: true })
      .then((windowClients) => {
        for (const client of windowClients) {
          if (client.url === targetUrl && "focus" in client) {
            return client.focus();
          }
        }
        return clients.openWindow(targetUrl);
      })
  );
});

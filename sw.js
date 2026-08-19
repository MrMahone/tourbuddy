/* Elbe-Tour — Service Worker
   App-Shell cache-first, Daten network-first mit Cache-Fallback,
   OSM-Tiles stale-while-revalidate mit Deckel. */

var VERSION = 'v1';
var SHELL = 'elbe-shell-' + VERSION;
var DATA = 'elbe-data-' + VERSION;
var TILES = 'elbe-tiles-' + VERSION;
var RUNTIME = 'elbe-runtime-' + VERSION;
var TILE_CAP = 800;

var SHELL_URLS = [
  './',
  'index.html',
  'manifest.webmanifest',
  'assets/icon.svg',
  'assets/icon-192.png',
  'assets/icon-512.png',
  'assets/icon-maskable-512.png',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
];

var DATA_FILES = /(waypoints|crossings)\.json$|route\.geojson$/;

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(SHELL).then(function (c) {
      // Einzeln adden: ein fehlgeschlagener Remote-Request darf die Installation nicht kippen.
      return Promise.all(SHELL_URLS.map(function (u) {
        return c.add(new Request(u, { cache: 'reload' })).catch(function () {});
      }));
    }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.map(function (k) {
        if (k.indexOf('elbe-') === 0 && k.indexOf(VERSION) === -1) return caches.delete(k);
      }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('message', function (e) {
  if (e.data === 'skipWaiting') self.skipWaiting();
});

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;

  var url;
  try { url = new URL(req.url); } catch (err) { return; }
  if (url.protocol !== 'http:' && url.protocol !== 'https:') return;

  // Start der App: erst Netz, dann Cache — damit ein Update ankommt, aber offline startet.
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req).then(function (res) {
        put(SHELL, req, res.clone());
        return res;
      }).catch(function () {
        return caches.match(req)
          .then(function (m) { return m || caches.match('index.html'); })
          .then(function (m) { return m || caches.match('./'); })
          .then(function (m) {
            return m || new Response('<h1>Offline</h1><p>App noch nicht vollständig gespeichert.</p>', {
              status: 503, headers: { 'Content-Type': 'text/html; charset=utf-8' }
            });
          });
      })
    );
    return;
  }

  // Daten: immer erst frisch versuchen, Cache als Rückfall.
  if (DATA_FILES.test(url.pathname)) {
    e.respondWith(
      fetch(req).then(function (res) {
        // Server hat geantwortet, aber mit Fehlerstatus (falscher Pfad, Datei weg).
        if (!res || !res.ok) return fallback(req, 'X-Elbe-Http', res && res.status);
        // Nur ablegen und ausliefern, was sich auch parsen lässt. Ein defektes JSON
        // (Tippfehler nach einem Push) darf den letzten guten Stand nicht überschreiben.
        return res.clone().text().then(function (txt) {
          try {
            JSON.parse(txt);
          } catch (err) {
            return fallback(req, 'X-Elbe-Stale');
          }
          put(DATA, req, res.clone());
          return res;
        });
      }).catch(function () {
        // Kein Netz.
        return fallback(req, 'X-Elbe-Cache');
      })
    );
    return;
  }

  // Kartenkacheln: sofort aus dem Cache, im Hintergrund erneuern.
  if (/tile\.openstreetmap\.org$/.test(url.hostname)) {
    e.respondWith(
      caches.open(TILES).then(function (c) {
        return c.match(req).then(function (hit) {
          var net = fetch(req).then(function (res) {
            if (res && res.ok && res.type !== 'opaque') {
              c.put(req, res.clone()).then(function () { trim(c, TILE_CAP); }).catch(function () {});
            }
            return res;
          }).catch(function () { return hit; });
          return hit || net;
        });
      })
    );
    return;
  }

  // Alles andere (Leaflet, Fonts, Icons): Cache first, sonst Netz und mitnehmen.
  e.respondWith(
    caches.match(req).then(function (hit) {
      if (hit) return hit;
      return fetch(req).then(function (res) {
        if (res && res.ok && res.type !== 'opaque') put(RUNTIME, req, res.clone());
        return res;
      });
    })
  );
});

// Letzten guten Stand ausliefern und mit einem Hinweis-Header markieren, damit die App
// dem Nutzer sagen kann, warum die Daten nicht die frischen sind.
function fallback(req, marker, status) {
  return caches.match(req, { ignoreSearch: true }).then(function (m) {
    if (!m) {
      // Nichts im Cache: 503, aber den Grund mitgeben — sonst liest die App
      // eine defekte Datei oder einen 404 als „offline".
      return new Response('{"items":[]}', { status: 503, headers: hdr(marker, status, 'application/json') });
    }
    return m.blob().then(function (b) {
      return new Response(b, {
        status: 200, statusText: 'OK',
        headers: hdr(marker, status, m.headers.get('Content-Type') || 'application/json')
      });
    });
  });
}

function hdr(marker, status, type) {
  var h = { 'Content-Type': type };
  h[marker] = '1';
  if (status) h['X-Elbe-Status'] = String(status);
  return h;
}

function put(cacheName, req, res) {
  if (!res || res.type === 'opaque') return;
  caches.open(cacheName).then(function (c) { c.put(req, res).catch(function () {}); });
}

function trim(cache, max) {
  return cache.keys().then(function (keys) {
    if (keys.length <= max) return;
    return Promise.all(keys.slice(0, keys.length - max).map(function (k) { return cache.delete(k); }));
  });
}

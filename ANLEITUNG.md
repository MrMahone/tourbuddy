# Elbe-Tour PWA — Betrieb & Pflege

## Dateien

| Datei | Zweck |
|---|---|
| `index.html` | die komplette App (Markup, CSS, JS inline, kein Build-Step) |
| `waypoints.json` | Register A: Wegpunkte, POIs, Schlafen |
| `crossings.json` | Register B: Querungen mit Ampelstatus |
| `sw.js` | Service Worker (Offline-Cache) |
| `manifest.webmanifest`, `assets/` | PWA-Installation und Icons |
| `design-brief-elbe-app.md`, `support.js`, `README.md`, `tour-kontext.md` | Doku und Design-Referenz — von der App nicht gelesen |

## Auf GitHub Pages bringen

```bash
git init && git add . && git commit -m "Elbe-Tour PWA"
```

Dann Repo auf GitHub anlegen, pushen, und unter *Settings → Pages* als Quelle `main` / `/ (root)` wählen.
Alle Pfade sind relativ, ein Unterpfad wie `benutzer.github.io/fahrradtool/` funktioniert also.

Wichtig: **HTTPS ist Pflicht** — ohne HTTPS kein Service Worker, keine Geolocation, kein Offline-Betrieb.
GitHub Pages liefert das automatisch.

Auf dem Handy im Browser öffnen → „Zum Startbildschirm hinzufügen". Danach startet die App im
Vollbild und funktioniert offline, sobald sie einmal geladen war.

## Status pflegen (der häufigste Fall)

Eine Zeile in `crossings.json` ändern und pushen:

```jsonc
{
  "id": "lenzen-pevestorf",
  "status": "rot",              // gruen | gruen-check | gelb | rot
  "statusDate": "2026-08-22",   // erscheint im Sheet als „Stand: 22.08."
  "note": "Pegel unter 90 cm — Fähre liegt fest"
}
```

Die App lädt die JSONs bei jedem Start frisch (mit Cache-Fallback offline). Nach dem Push also
einmal mit Netz öffnen — dann ist der neue Stand auch offline gespeichert.

**Statusbedeutung:** `gruen-check` ist ein eigener Status, nicht „grün mit Sternchen": die Raute
erscheint grün mit hohlem Kern und heißt „fährt regulär, aber am Durchfahrtstag live prüfen".

## Schlafplätze ergänzen

Telefonnummern sind bewusst **nicht** eingetragen — nichts Unverifiziertes. Sobald du eine Nummer
bestätigt hast, rein damit; der große Telefon-Button erscheint dann automatisch:

```jsonc
"sleep": [
  { "name": "Campingplatz Torgau", "type": "camping", "phone": "+49 3421 712159", "detourKm": 1.4 }
]
```

`sleepStatus` pro Ort (`gruen` / `gelb` / `rot`) ist die Ampel aus dem Punkteraster und erscheint
als Badge im Sheet-Kopf. `gelb` heißt „Versorgungspunkt, Zeltmöglichkeit noch nicht verifiziert".

## Route auf den Sigma ROX 11.1 EVO

Im Sheet unten: **GPX bis hierher**. Die App schneidet die Strecke von deiner GPS-Position (ohne
Position: vom Start der gewählten Richtung) bis zum gewählten Punkt aus und öffnet den
Teilen-Dialog.

> Teilen → **SIGMA RIDE** → Track importieren → per Bluetooth auf den ROX

Klappt offline und ohne Konto. Falls das Gerät keinen Datei-Teilen-Dialog kann, lädt die App die
GPX-Datei stattdessen herunter — dann in SIGMA RIDE über „Track-Datei importieren" öffnen.

Zweiter Weg: **In Komoot planen** öffnet den Komoot-Planer auf dem Punkt (auf dem Handy die
Komoot-App). Wenn eine GPS-Position bekannt ist, werden Start und Ziel als Wegpunkte mitgegeben —
das nutzt eine undokumentierte Komoot-URL, kann also ignoriert werden; der Planer öffnet dann
einfach nur an der richtigen Stelle. Komoot → ROX braucht die Kopplung in der SIGMA RIDE App
(und laut Testberichten Komoot Premium), der GPX-Weg oben braucht das nicht.

## Fahrtrichtung umstellen

Ebenen-Button (unten rechts) → **Richtung**. Schaltet zwischen `QUELLE → HH` und `HH → QUELLE`.
Es dreht sich nur die Anzeige: Chip-Untertitel, die Spalte „NOCH BIS …", die Flussleiste und die
Richtung des GPX-Exports. Die Datenachse bleibt immer „km ab Quelle". Die Wahl wird im Gerät
gespeichert.

## Echten Elberadweg-Verlauf einbinden

Aktuell liegt unter den Markern eine gepunktete Linie durch die Wegpunkt-Kette — gut zur
Orientierung, aber Luftlinie zwischen den Orten. Für einen echten Verlauf:

1. GPX von elberadweg.de (bzw. deiner finalen Planung) holen und nach GeoJSON konvertieren
2. Als `route.geojson` in den Ordner legen
3. In `waypoints.json` unter `meta` eintragen: `"routeFile": "route.geojson"`

Die App zeichnet dann diese Linie und schneidet auch die GPX-Exporte daraus (auf 2.000 Punkte
ausgedünnt, damit der ROX nicht stolpert). Danach lohnt es, die km-Werte im Punkteraster
geometrisch gegen den Verlauf zu rechnen — bis dahin sind sie Schätzungen.

## Bekannte Näherungen (Stand 19.08.2026)

- **Koordinaten und km-Werte sind Schätzungen** (`"estimate": true`). Koordinaten liegen im
  Ortszentrum bzw. am Fähranleger, km sind die kumulierten Δ-Schätzungen aus `tour-kontext.md`.
  Gesamtlänge 1.066 km, konsistent zur Doku-Angabe „1.050–1.100 km".
- **Schlafplatz-Marker** haben keine eigenen Koordinaten: sie sitzen versetzt beim jeweiligen Ort.
  Das Sheet weist darauf hin.
- **Zwei Punkte wurden gegenüber `tour-kontext.md` umsortiert**, weil die km-Achse flussabwärts
  monoton laufen muss: Werben liegt vor Sandau/Havelberg, und Schnackenburg vor Lenzen.
- **Querungsstatus ist vom 18.08.2026** und laut Doku sehr dynamisch — vor jedem Durchfahrtstag
  gegen aktuelle Meldungen prüfen.

## Lokal testen

```bash
python -c "import http.server as h, mimetypes; mimetypes.add_type('text/javascript','.js'); h.test(HandlerClass=h.SimpleHTTPRequestHandler, port=8765)"
```

Das `add_type` ist auf Windows nötig — sonst liefert Python `.js` als `text/plain` aus und der
Browser weigert sich, den Service Worker zu registrieren. Auf GitHub Pages ist das kein Thema.

## Wenn die Wegpunkte nicht laden

Die App **sagt dir, was los ist** — die rote Meldung oben ist die Diagnose:

| Meldung | Bedeutung | Was tun |
|---|---|---|
| *„Datei auf dem Server ist defekt — zeige letzten guten Stand"* | Syntaxfehler in der gepushten JSON. Die App läuft mit dem letzten guten Stand weiter. | JSON reparieren und neu pushen. Kein Stress unterwegs — nichts ist verloren. |
| *„… ist defekt und nichts gespeichert — JSON prüfen"* | Syntaxfehler **und** kein Cache (z. B. neues Gerät). | JSON reparieren, dann mit Netz einmal öffnen. |
| *„… nicht gefunden (HTTP 404) — Pfad prüfen"* | Datei liegt nicht dort, wo die App sie sucht. | Liegen `waypoints.json` und `crossings.json` neben `index.html` im Repo-Root? |
| *„Offline und noch nichts gespeichert"* | Erststart ohne Netz. | Einmal mit Netz öffnen, danach geht alles offline. |
| *„Offline — Datenstand aus dem Cache"* | Normalbetrieb ohne Netz. | Nichts. Läuft. |
| Chip zeigt km, aber keine Marker | Daten geladen, aber leer. | `items`-Array in der JSON prüfen. |

**Der wichtigste Punkt:** Ein Tippfehler in der JSON kann die App nicht mehr blind machen. Der
Service Worker prüft jede frisch geladene Datei, ob sie überhaupt parsebar ist, und behält bei
einem Defekt den letzten guten Stand im Cache.

### Vor jedem Push prüfen (10 Sekunden, verhindert 90 % der Fälle)

```bash
python -m json.tool waypoints.json > /dev/null && python -m json.tool crossings.json > /dev/null && echo OK
```

Bei einem Fehler nennt der Befehl Zeile und Spalte — meist ein fehlendes oder zu viel gesetztes
Komma. Nur pushen, wenn `OK` erscheint.

### Unterwegs ohne Laptop

Die JSON-Datei direkt auf github.com im Browser öffnen: GitHub zeigt Syntaxfehler an und man kann
sie dort auch bearbeiten und committen. Und selbst wenn die App streikt — die Querungen mit Status
und Betriebszeiten sind in `crossings.json` reiner, lesbarer Text.

### Alten Stand hartnäckig im Cache

App vom Startbildschirm ganz schließen und neu öffnen. Wenn das nicht reicht, im Browser
(nicht in der installierten App) die Seite mit Reload öffnen — die App holt die JSONs bei jedem
Start neu, sobald Netz da ist.

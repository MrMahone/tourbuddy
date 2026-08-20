# Elbe-Tour PWA — Betrieb & Pflege

## Dateien

| Datei | Zweck |
|---|---|
| `index.html` | die komplette App (Markup, CSS, JS inline, kein Build-Step) |
| `waypoints.json` | Register A: Wegpunkte, POIs, Schlafen |
| `crossings.json` | Register B: Querungen mit Ampelstatus |
| `swim.json` | Register C: Bademöglichkeiten (Elbstrand, Seen) |
| `route.geojson` | echter Routenverlauf beider Ufer aus OpenStreetMap |
| `sw.js` | Service Worker (Offline-Cache) |
| `tools/` | Datenpipeline gegen OpenStreetMap — wird nicht ausgeliefert |
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

## Woher die Geometrie kommt

Route, Positionen und km-Werte stammen aus OpenStreetMap und werden von den Skripten
unter `tools/` erzeugt. Die App liest nur die fertigen JSON-Dateien.

```bash
python tools/build_route.py          # route.geojson aus den OSM-Relationen
python tools/build_data.py           # Bericht: was würde sich ändern
python tools/build_data.py --write   # Register aktualisieren (Backups als *.bak)
```

Verwendete OSM-Quellen:

| Relation | Inhalt |
|---|---|
| `123822` | Elbe (Gewässerlauf) — dient als Referenzachse für Reihenfolge und Snapping |
| `181093` | Labská stezka — tschechischer Teil, Quelle bis Hřensko |
| `22327` | Elberadweg D10 rechtselbisch |
| `22328` | Elberadweg D10 linkselbisch |

Zwei Dinge, die dabei wichtig sind und leicht schiefgehen:

**OSM-Relationen sind zerstückelt.** Die Wege einer Route teilen nicht überall denselben
Knoten; gemessen wurden Lücken von 7 m bis 20 km. Reihum-Verketten läuft an den großen
Lücken in die falsche Richtung. Deshalb ordnet die Pipeline die Fragmente entlang des
Flusslaufs — der gibt die Reihenfolge eindeutig vor — und füllt echte Lücken mit der
Flussgeometrie statt mit Luftlinien.

**Der Moldau-Abstecher fliegt raus.** Die offizielle Labská stezka führt über Prag an der
Moldau. Deine Planung lässt das bewusst weg. Die Pipeline verwirft daher Fragmente, deren
weitester Punkt mehr als 8 km von der Elbe entfernt liegt (der Prag-Abschnitt kommt auf
15,7 km, alle anderen bleiben unter 2,6 km).

Der Overpass-Cache liegt unter `tools/.cache/`. Ein zweiter Lauf braucht kein Netz.
Achtung: ändert sich die Route, ändern sich auch die Abfragefilter — dann wird alles neu
geladen, und das dauert einige Minuten.

## Baden

`swim.json` enthält nur zwei Sorten: `elbe` (Strand am Fluss) und `see` (See oder Baggersee).
Freibäder sind bewusst nicht drin. Aufgenommen wird, was höchstens 2 km Umweg von der Route
liegt (Konstante `SWIM_MAX_DETOUR_KM` in `tools/build_data.py`).

Mehrfach erfasste Stellen werden zusammengefasst, und unbenannte Strände auf höchstens einen
je 3 km ausgedünnt — sonst kommen allein an der Elbe über 130 Marker zusammen, meist nur
kartierte Sandflächen.

Bei jedem Elbstrand steht ein Warnhinweis im Sheet: **Strömung, Sog an den Buhnen,
Berufsschifffahrt.** Das ist kein Formalkram — die Buhnenfelder der Elbe haben eine
erhebliche Sogwirkung. Seen am Weg sind zum Baden die deutlich bessere Wahl.

## Datenstand und was noch geschätzt ist

Stand 20.08.2026, nach dem OSM-Abgleich:

- **Route und km-Achse sind gemessen**, nicht geschätzt. Gesamtlänge **1129 km** entlang der
  OSM-Radwegachse (Labská stezka + Elberadweg rechtselbisch), Elbquelle bis Elbphilharmonie.
  Der Wert liegt unter der Doku-Angabe für die offizielle Route, weil der Moldau-Abstecher
  über Prag nicht mitgerechnet wird.
- **Alle 56 Ortskoordinaten** stammen aus OSM-place-Knoten. Größte Korrektur gegenüber der
  ersten Schätzung: Sandau/Havelberg um 4,6 km, Bertingen und Arneburg je 2,4 km.
- **25 von 60 Querungen** sitzen auf echten OSM-Fähranlegern bzw. benannten Brücken. Die
  restlichen **35** sind auf den Flusslauf gesnappt (`estimate: true`) — sie liegen damit auf
  dem Wasser, aber die genaue Anlegestelle ist nicht bestätigt.
- **20 von 30 Schlafplätzen** haben echte Koordinaten aus OSM, **17** davon mit Telefonnummer.
  Diese Nummern sind Fremddaten und im Sheet als solche gekennzeichnet — vor dem Verlassen
  der Route einmal anrufen. Die restlichen Marker sitzen weiter beim Ort, nicht am Platz.
- **Zwei Punkte sind gegenüber `tour-kontext.md` umsortiert**, weil die km-Achse flussabwärts
  monoton laufen muss: Werben liegt vor Sandau/Havelberg, Schnackenburg vor Lenzen.
- **Querungsstatus ist vom 18.08.2026** und kommt aus deiner Recherche, nicht aus OSM. Der
  Wasserstand ändert das binnen Tagen — vor jedem Durchfahrtstag prüfen.
- **Der Umweg-Wert der POIs** (`poi.detourKm`) stammt weiter aus deiner Recherche. Neu daneben:
  `routeDistKm`, der gemessene Abstand des Ortes zur Radwegachse.

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

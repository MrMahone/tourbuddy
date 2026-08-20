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

## Datenstand der Querungen

**Status: 20.08.2026**, abgeglichen mit der offiziellen Ausfallliste
`elberadweg.de/news-service/baustellen-umleitungen-faehrausfall`. Jede aktualisierte Querung
trägt die Quelle im Sheet.

11 außer Betrieb, 3 eingeschränkt, 46 in Betrieb (davon 14 am Durchfahrtstag live prüfen).

Gegenüber der ersten Fassung korrigiert: **Ferchland–Grieben ist außer Betrieb** (12.–30.08.),
stand vorher als „eingeschränkt". Alle Ausfälle haben jetzt exakte Zeiträume statt „bis auf
Weiteres" — die meisten enden am 23.08., Belgern am 25.08., Breitenhagen am 28.08.,
Arneburg und Ferchland am 30.08.

**Baustellen, die eine Querung betreffen**, sind als Hinweis am jeweiligen Eintrag vermerkt:
Umleitung Königstein–Kurort Rathen (bis 30.11.2026), Kleindröben–Mauken (bis 30.09.2026) und
der Brückenbau Wittenberge (läuft bis 12.10.2029).

### Pegel — live in der App

Beim Öffnen einer Fähre holt die App den aktuellen Wasserstand direkt von
pegelonline.wsv.de und zeigt:

- **den Messwert** in cm am zuständigen Pegel
- **die Veränderung über 24 Stunden** (steigt oder fällt der Fluss?)
- **die Einordnung**, also „unter mittlerem Niedrigwasser" oder „im normalen Bereich".
  Das ist der wichtigere Teil: absolute Zentimeter sind zwischen Pegeln nicht vergleichbar,
  jeder hat seinen eigenen Nullpunkt. Rogätz steht bei −19 cm, das ist kein Fehler.
- **das Alter der Messung** („gemessen 12:15 Uhr, vor 14 Min.")

Liegt der Wert unter mittlerem Niedrigwasser oder unter dem niedrigsten schiffbaren
Wasserstand, wird die Zeile orange.

Technisch: eine Sammelabfrage holt alle 73 Elbe-Pegel in einem Rutsch (66 KB, ~0,7 s) und
gilt dann eine halbe Stunde. Der 24-Stunden-Verlauf wird nur für den gerade geöffneten Pegel
geladen (~7 KB). Beides wird erst beim ersten Fährklick angefordert, nicht beim App-Start.

**Ohne Netz** steht der letzte gespeicherte Wert samt Messalter da. Der Service Worker cacht
die Pegelabfragen ausdrücklich **nicht** — cache-first würde den Wert einfrieren und man
würde tagelang denselben Stand sehen, ohne es zu merken.

Bei Brücken erscheint kein Pegel: deren Benutzbarkeit hängt nicht am Wasserstand.
Für Tschechien gibt es keinen — pegelonline führt dort nur Přelouč, und das ohne Koordinaten.

### Positionsgenauigkeit

Im Feld `posSource` steht, woher die Koordinate kommt:

| Wert | Anzahl | Bedeutung |
|---|---|---|
| `osm-objekt` | 32 | Fähranleger oder benannte Brücke aus OSM |
| `osm-faehrlinie` | 0 | Mitte einer OSM-Fährlinie (`route=ferry`) |
| `flusslauf-bruecke` | 18 | Brücke, auf den Flusslauf gesetzt — die Querungsstelle stimmt, die genaue Brücke ist nicht bestätigt |
| `flusslauf-geschaetzt` | 10 | Anlegestelle unbestätigt, Marker sitzt auf dem Fluss. Das Sheet weist darauf hin. |

Die Filterung nach Linienlänge ist wichtig: HADAG-Fähren in Hamburg fahren **längs** der Elbe,
nicht darüber. Ihr Linienmittelpunkt ist keine Querungsstelle, deshalb bleiben Linien über 2 km
außen vor.

## Datenstand der übrigen Register

- **Route und km-Achse gemessen**, Gesamtlänge 1129 km entlang der OSM-Radwegachse.
- **Alle 56 Ortskoordinaten** aus OSM-place-Knoten. Größte Korrektur: Sandau/Havelberg 4,6 km.
- **20 von 30 Schlafplätzen** mit echten Koordinaten, 17 davon mit Telefonnummer aus OSM —
  Fremddaten, im Sheet gekennzeichnet, vor dem Abbiegen anrufen.
- **Zwei Punkte umsortiert** gegenüber `tour-kontext.md`, damit die km-Achse monoton bleibt:
  Werben vor Sandau/Havelberg, Schnackenburg vor Lenzen.

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

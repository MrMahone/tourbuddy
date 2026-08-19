# Handoff: Elbe-Tour Karte (Mobile-first PWA)

## Overview
Mobile-first Karten-PWA für eine Fahrradreise entlang der Elbe (Quelle → Hamburg), Start 20.08.2026. Ein Werkzeug für unterwegs: Wo bin ich, was liegt voraus, wo schlafe ich, wo komme ich über den Fluss. Kein Reiseführer. Nutzung einhändig, bei Sonne, oft mit schlechtem Netz.

## About the Design Files
Die Datei `Elbe-Tour Karte.dc.html` in diesem Bundle ist eine **Design-Referenz in HTML** (klickbarer Prototyp) — kein Produktionscode. Aufgabe: dieses Design als echte PWA neu implementieren gemäß dem fixen Technik-Rahmen unten (Vanilla JS + Leaflet, kein Build-Step). Der Prototyp lädt Beispieldaten inline; die echte App liest `waypoints.json` / `crossings.json`.

## Fidelity
**High-fidelity.** Farben, Typografie, Abstände, Markerformen und Sheet-Verhalten sind final gemeint und sollen pixelgenau übernommen werden. Die Beispieldaten (Orte, Telefonnummern, Status) sind Dummys.

## Technik-Rahmen (fix, vom Auftraggeber)
- Leaflet + OSM-Raster-Tiles (z. B. OpenFreeMap), **kein Build-Step**: eine `index.html` + JSON + Assets
- PWA: Manifest + Service Worker (App-Shell + JSON cachen; besuchte Tiles cachen)
- Hosting: GitHub Pages
- Daten: `waypoints.json` und `crossings.json` (Schema siehe unten), bei jedem Start frisch laden, Cache-Fallback offline
- Optional: Elberadweg-GPX als dezente Routenlinie unter den Markern

## Screens / Views

Es gibt genau **eine** View: die Vollbild-Karte. Alles andere (Bottom Sheet, Ebenen-Panel) legt sich temporär darüber. Kein Header, keine Navigation, keine Unterseiten.

### 1. Karte (Vollbild)
- Leaflet füllt den Viewport (`100dvh`), `zoomControl: false`, Attribution klein (9px, halbtransparenter Grund `rgba(243,242,242,.7)`)
- Startansicht: `fitBounds` über alle Wegpunkte, Padding 30px
- Routenlinie (optional/GPX): Farbe `#3c5a68`, weight 3, opacity 0.45, `dashArray: '1 7'`, `lineCap: 'round'` — gepunktete, dezente Linie unter den Markern
- Tap auf Karte (nicht Marker) schließt das Sheet

**Brand-Chip** (oben links, 12px Abstand):
- Weißer Block `#f3f2f2`, Border `2px solid #201e1d`, KEIN Radius, Shadow klein, Padding 10/14/9
- Zeile 1: rotes Quadrat 9×9 `#ec3013` + „ELBE-TOUR" (12px, 800, letter-spacing .12em)
- Zeile 2: „QUELLE → HAMBURG · 1021 KM" (9px, 600, letter-spacing .1em, Farbe `#6d6a66`, tabular-nums)

**Floating Buttons** (rechts unten, bottom 28px, gap 8px, vertikal):
- Locate-Button (Fadenkreuz-Icon) und Ebenen-Button (Lucide `layers`)
- Je 52×52px, `#f3f2f2`, Border `2px solid #201e1d`, kein Radius, Hover `#e9e7e2`, Focus `outline: 2px solid #ec3013; offset 2px`
- Locate zentriert auf die GPS-Position (Zoom ≥ 12); in der echten App: Geolocation API

**GPS-Positionsmarker:**
- Roter Punkt: 20×20 Wrapper, innen Kreis `#ec3013` mit `2px solid #f3f2f2` Rand
- Pulsierender Halo: `2px solid #ec3013`-Ring, Animation `scale(.55)→scale(1.6)` + opacity `.9→0`, 2.2s ease-out infinite; bei `prefers-reduced-motion` aus

### 2. Ebenen-Panel (über Ebenen-Button)
- 232px breit, `#f3f2f2`, Border `2px solid #201e1d`, Shadow md, erscheint über dem Button
- Kopfzeile: rotes Quadrat 8×8 + „EBENEN" (10px, 700, .12em, `#6d6a66`), darunter 2px-Linie
- 4 Zeilen à min. 48px: Standard / Querungen hervorheben / Schlafplätze hervorheben / Dark Mode
  - Layout: [Lucide-Icon 16px, Farbe `#6d6a66`] [Label 14px 600, flex 1] [12×12-Quadrat mit 2px-Ink-Border, aktiv gefüllt `#ec3013`]
  - Icons: map / Raute (rotiertes Quadrat) / home / moon
  - Trennung: 1px `#cfccc7`, vor Dark Mode 2px `#201e1d`
- Auswahl eines Markers schließt das Panel

### 3. Bottom Sheet
Erscheint bei Marker-Tap; Karte zentriert den Punkt leicht nach oben (Pixel-Offset: +14 % der Viewporthöhe nach unten auf den Kartenmittelpunkt, Zoom min. 10).

- Container: absolute, volle Breite, Höhe 72 %, `#f3f2f2`, `border-top: 2px solid #201e1d`, Shadow `0 -8px 28px rgba(0,0,0,.2)`, kein Radius
- **Zwei Snap-Punkte:** Peek = `translateY(calc(100% - 272px))` (272px sichtbar), Voll = `translateY(0)`
- Transition `transform .18s ease-out` („kurz und trocken"); während Drag: keine Transition, 1:1 dem Finger folgen
- **Gesten** (Pointer Events auf dem Kopfbereich):
  - Tap (Bewegung < 6px): toggelt Peek ↔ Voll
  - Ziehen nach oben > 50px → Voll; nach unten > 60px → Peek bzw. aus Peek schließen
  - Im Voll-Zustand Drag nach oben auf −20px begrenzen
  - X-Button (44×44) und Karten-Tap schließen ebenfalls; Buttons/Links im Kopf starten keinen Drag
- Handle: 36×4px Balken `#cfccc7`, zentriert
- Scrollen des Inhalts nur im Voll-Zustand (`overflow-y: auto`), im Peek `hidden`

**Sheet-Kopf (immer sichtbar, Padding 0 20px 10px):**
1. Kicker: rotes Quadrat 8×8 + Typzeile (10px, 700, .12em, `#6d6a66`), z. B. „QUERUNG · GIERFÄHRE", „WEGPUNKT · ETAPPENORT", „SCHLAFPLATZ · CAMPING"
2. Name: 28px, 800, line-height 1.02, letter-spacing −.015em
3. Nur Querungen — Statuszeile: Badge + „Stand: TT.MM." (12px, `#6d6a66`, tabular)
4. Nur `critical: true`: „▲ EINZIGE QUERUNG IN DIESEM ABSCHNITT" (11px, 700, .06em, `#a2210d`)
5. Kennzahlen-Band: 3 Spalten über 2px-Ink-Linie, Spalten durch 1px `#cfccc7` getrennt. Je Zelle: Label (9px, 700, .1em, `#6d6a66`) + Wert (19px, 800, tabular). Spalten: KM AB QUELLE / UMWEG / NOCH BIS HH

**Flussleiste (Signature-Element, nur im Voll-Zustand, zwischen Kopf und Inhalt):**
- Über 2px-Ink-Linie abgetrennt, Padding 10/20/12
- Labelzeile „QUELLE" … „HAMBURG" (9px, 700, .1em, `#6d6a66`)
- Track: 2px `#cfccc7`; gefüllter Anteil bis zur aktuellen Position 2px `#201e1d`
- Etappen-Ticks: 1×8px `#6d6a66` bei km 415/528/722/855 (in echt: aus Etappenorten generieren)
- Positionsmarke: 12×12 Quadrat `#ec3013` mit `2px solid #f3f2f2`, zentriert auf Prozentposition (`left: pct; margin-left: −6px`)
- Darunter: „km {km} von 1021" (12px, 700 / „von …" 500 `#6d6a66`, tabular)

**Inhalt (Padding 0 20px 24px, oben 1px `#cfccc7`):**
- *Wegpunkt:* Stichpunkte als Zeilen (14px, line-height 1.45, 6×6-Ink-Quadrat als Bullet, 1px-Trennlinien, Padding 11px 0). Danach ggf. Abschnitt „SCHLAFEN" (Label 10px über 2px-Linie), pro Unterkunft: Name (15px 700) + Typ-Tag rechts (11px, `#6d6a66`) + „Umweg +x,x km" + **Telefon-Button**
- *Schlafplatz:* Zeile „Bei {Ort}", optionale Notiz, großer Telefon-Button
- *Querung:* Definitionszeilen Label links `#6d6a66` / Wert rechts 600 (Betrieb, Ersatz), Notiz als Fließzeile; bei Status `gruen-check`/`gelb` Link-Zeile „Pegelstand prüfen" (→ pegelonline.wsv.de)
- *Immer:* Link-Zeile „In Karten-App öffnen" (geo:/maps-URL), gedämpfte Variante (Border `#cfccc7`, Text `#6d6a66`, Hover Ink)

**Telefon-Button (kritischstes Tap-Target):**
- `<a href="tel:…">`, min-height 48–52px, Border `2px solid #201e1d`, kein Radius, Padding 0 14px
- Lucide `phone` in `#ec3013` + Nummer (15–16px, 700, tabular), flush left; Hover `#e9e7e2`

## Marker-System

Drei Klassen, unterscheidbar über Form UND Farbe. Alle als Leaflet `divIcon` (className leer, HTML wie unten). Alle mit `box-shadow: 0 1px 4px rgba(0,0,0,.3)`. „Papierfarbe" (Ränder) = `#f3f2f2` hell / `#211f1e` dark.

| Klasse | Form | Standard | Hervorgehoben |
|---|---|---|---|
| Wegpunkt/Ort | Kreis, Füllung `#3c5a68` (Flussblau-Grau), 2px Papier-Rand | 16px | gedimmt (10px, opacity .35), wenn anderer Modus aktiv |
| Schlafplatz | Quadrat, Papier-Füllung, `2px solid #3c5a68` Rand, Lucide-`home`-Glyphe (stroke `#3c5a68`, ~60 % der Größe) | 22px | 30px im Modus „Schlafplätze" |
| Querung | Raute (45° rotiertes Quadrat), 2px Papier-Rand | 15px, Füllung `#3c5a68` (Ampelfarbe versteckt) | 30px mit Ampelfarbe im Modus „Querungen" |

- **Ampelfarben (rein funktional, nie dekorativ):** grün `#2f7d33`, gelb `#b26a00`, rot `#8f1d1d`
- **grün-prüfen:** grüne Raute mit hohlem Kern (Papier-Kreis, inset 28 %) — eigener Status, sichtbar unterschieden von grün
- **critical: true:** immer 20px statt 15px, Ampelfarbe immer sichtbar, permanenter Ring `outline: 2px solid #201e1d` (dark: `#eceae6`), offset 2px
- **Ausgewählt:** `outline: 3px solid #ec3013`, offset 2px; Ampelfarbe sichtbar
- Hervorhebungsmodi dimmen die jeweils anderen Klassen auf opacity .35 (ausgewählter Marker nie gedimmt)

## Interactions & Behavior
- Marker-Tap → Sheet im Peek, Karte pannt Punkt in obere Hälfte, Panel schließt
- Sheet-Gesten wie oben; Zurück zur Karte ist immer Geste (Runterwischen/Karten-Tap/X), nie Menüpfad
- Ebenen-Modi sind exklusiv (Radio-Verhalten): standard | querungen | schlaf
- Dark Mode: Toggle im Panel. Tiles per CSS-Filter `invert(1) hue-rotate(190deg) saturate(.3) brightness(.92) contrast(.92)`, Kartengrund `#1a1918`; UI-Flächen wechseln auf Dark-Tokens (unten); Marker-Papierfarbe wechselt mit
- `prefers-reduced-motion: reduce` → alle Transitions/Animationen aus
- Statusdatum („Stand: TT.MM.") ist bei Querungen IMMER sichtbar, schon im Peek

## State Management
- `sel` (ausgewählter Punkt + Klasse wp|sl|cx), `sheet` (peek|full), `mode` (standard|querungen|schlaf), `dark` (bool), `panel` (bool), Drag-Zustand (dy, dragging)
- Marker werden bei Änderung von sel/mode/dark neu gerendert
- Daten: `waypoints.json` + `crossings.json` bei App-Start fetchen, in Cache legen; offline aus Cache. Schlafplatz-Marker aus `waypoint.sleep[]` ableiten (im Prototyp mit kleinem Koordinaten-Offset — in echt eigene Koordinaten pflegen)

### Datenschema (fix)
```json
// waypoints.json
{ "id": "wittenberge", "name": "Wittenberge", "type": "ort|camping|pension|poi",
  "coords": [53.005, 11.75], "kmFromStart": 812, "detourKm": 0,
  "notes": ["…"], "sleep": [{ "name": "…", "type": "camping", "phone": "+49 …", "detourKm": 1.2 }] }

// crossings.json
{ "id": "domitz-bruecke", "name": "Straßenbrücke Dömitz", "kind": "bruecke|faehre|gierfaehre|tunnel",
  "coords": [53.14, 11.25], "status": "gruen|gruen-check|gelb|rot", "statusDate": "2026-08-18",
  "hours": "jederzeit", "critical": true, "backup": null, "note": "…" }
```

## Design Tokens
Basis: Modernist-Designsystem — flach, 0px Radius überall, 2px-Linien, alles flush left, Archivo.

**Hell:**
- Fläche `--sf: #f3f2f2`, Fläche 2/Hover `--sf2: #e9e7e2`
- Ink/Text/Linien stark `#201e1d`, gedämpft `#6d6a66`, Linien weich `#cfccc7`
- Akzent (einziger, nur Interaktion): `#ec3013`; Akzent dunkel (Text auf hell): `#a2210d`

**Dark:**
- Fläche `#211f1e`, Fläche 2 `#2b2927`, Ink `#eceae6`, gedämpft `#9b9792`, Linien weich `#454340`, Kartengrund `#1a1918`

**Karte/Marker:** Flussblau-Grau `#3c5a68`; Ampel grün `#2f7d33` / gelb `#b26a00` / rot `#8f1d1d`

**Typo:** Archivo (400/600/700/800), überall. Kicker/Labels: 9–12px, 700, letter-spacing .06–.12em, VERSALIEN. Zahlen immer `font-variant-numeric: tabular-nums`. Name im Sheet 28px/800.

**Sonstiges:** Radius 0 überall. Borders 2px (stark) / 1px (weich). Focus immer `outline: 2px solid #ec3013; outline-offset: 2px`. Tap-Targets ≥ 44px, tel-Links ≥ 48px.

## Assets
- Icons: Lucide (https://lucide.dev), inline SVG, stroke-width 2–2.2: layers, home, moon, map, phone, x, arrow-up-right, Fadenkreuz (locate)
- Kein Bildmaterial. Tiles: OSM (Attribution pflicht)

## Files
- `Elbe-Tour Karte.dc.html` — der Prototyp (Referenz für alles Obige; Beispieldaten inline im Script-Teil)
- `_ds/…/styles.css` im Projekt — Token-Quelle des Modernist-Systems (Referenz)

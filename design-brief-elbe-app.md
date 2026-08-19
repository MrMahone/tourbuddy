# Design-Brief: Elbe-Tour Karte (Arbeitstitel)

Mobile-first PWA für eine Fahrradreise entlang der Elbe (Quelle → Hamburg), Start 20.08.2026.
Genutzt wird die App unterwegs auf dem Handy: einhändig, bei Sonne, oft mit schlechtem Netz.
Kein Reiseführer, kein Spoiler-Magazin — ein Werkzeug: Wo bin ich, was liegt voraus, wo schlafe ich, wo komme ich über den Fluss.

---

## 1. Kern der Anwendung

Die Karte **ist** die App. Vollbild, kein klassischer Header, keine Navigation, keine Unterseiten.
Alles andere (Detailansicht, Filter) legt sich temporär über die Karte und verschwindet wieder.

```
┌─────────────────────────┐
│                         │
│         KARTE           │  ← Vollbild, Leaflet + OSM
│      ● Wegpunkte        │
│      ▲ Querungen        │
│      ⌂ Schlafplätze     │
│                         │
│              [Layer] ◉  │  ← schwebender Toggle-Button
├─────────────────────────┤
│ ▔▔▔ Bottom Sheet ▔▔▔    │  ← erscheint nur bei Auswahl
└─────────────────────────┘
```

## 2. Marker & Symbolik

Drei Marker-Klassen, auf einen Blick unterscheidbar (Form UND Farbe, nicht nur Farbe):

| Typ | Form | Bedeutung |
|---|---|---|
| Wegpunkt / Ort | Kreis | Etappenort, POI |
| Schlafplatz | Haus/Zelt-Icon | Campingplatz, Pension etc. |
| Querung | Raute oder Dreieck | Brücke, Fähre, Tunnel |

Querungen tragen zusätzlich ihren **Ampelstatus** als Farbe:

- 🟢 **grün** — in Betrieb, verlässlich (Brücken, bestätigte Fähren)
- 🟢◌ **grün-prüfen** — regulär in Betrieb, aber wasserstandsabhängig → am Durchfahrtstag live checken (eigener Status, nicht in Grün verstecken!)
- 🟡 **gelb** — eingeschränkt / vorher Wasserstand prüfen
- 🔴 **rot** — außer Betrieb, nicht einplanen

Standardansicht: Querungsmarker **dezent/klein** (Karte soll nicht überladen wirken).
Über den Layer-Button: "Querungen hervorheben" → alle Querungen groß mit sichtbarer Ampelfarbe, Wegpunkte treten zurück. Gleicher Mechanismus umgekehrt für Schlafplätze denkbar.

Querungen mit `critical: true` (einzige Querung in einem langen fährenfreien Abschnitt, z. B. Dömitzer Brücke) bekommen eine dezente permanente Kennzeichnung — die dürfen nie übersehen werden.

## 3. Interaktion: Bottom Sheet

Tap auf Marker → Bottom Sheet fährt von unten ein, Karte bleibt sichtbar und zentriert den Punkt leicht nach oben.

**Kompaktzustand (Peek, ~30 % Höhe):**
- Name + Typ-Icon
- Bei Querungen: Ampelstatus als Badge + "Stand: TT.MM." (Datenstand IMMER sichtbar)
- 2–3 Stichpunkte: km ab Start, Umweg, Kurzinfo
- Kein Fließtext, keine Spoiler

**Expandiert (Hochwischen oder Tap, ~70 %):**
- Alle Stichpunkte
- Schlafmöglichkeiten mit **Telefonnummer als `tel:`-Link** (großes Tap-Target, ≥48 px — wird mit Handschuhen/unterwegs gedrückt)
- Bei Querungen: Betriebszeiten, Backup-Querung ("Ersatz: Stadtbrücke Riesa"), ggf. Link Pegelstand
- Optional: Link zu OSM/Google-Maps-Navigation zum Punkt

Schließen: Runterwischen, Tap auf Karte, oder X. Zurück zur Karte ist immer eine Geste, nie ein Menüpfad.

## 4. Datenmodell (JSON, zwei Dateien)

```json
// waypoints.json
{
  "id": "wittenberge",
  "name": "Wittenberge",
  "type": "ort",                    // ort | camping | pension | poi
  "coords": [53.005, 11.75],
  "kmFromStart": 812,
  "detourKm": 0,
  "notes": ["Bahnhof (Notausstieg)", "Supermarkt am Radweg"],
  "sleep": [
    { "name": "Campingplatz X", "type": "camping", "phone": "+49 ...", "detourKm": 1.2 }
  ]
}
```

```json
// crossings.json
{
  "id": "domitz-bruecke",
  "name": "Straßenbrücke Dömitz",
  "kind": "bruecke",                // bruecke | faehre | gierfaehre | tunnel
  "coords": [53.14, 11.25],
  "status": "gruen",                // gruen | gruen-check | gelb | rot
  "statusDate": "2026-08-18",
  "hours": "jederzeit",
  "critical": true,
  "backup": null,
  "note": "Einzige verlässliche Querung zw. Wittenberge und Lauenburg"
}
```

Status-Pflege = eine Zeile im JSON ändern und pushen. Die App liest die Dateien bei jedem Start (mit Cache-Fallback offline).

## 5. Gestaltungsrichtung

Kein generisches Karten-Dashboard. Referenzrahmen: **analoge Flusskarte / Tourenbuch** — die App begleitet eine echte Reise auf einem echten Fluss.

- **Palette aus der Elbelandschaft ableiten:** Flussblau-Grau als Basis der Marker-Welt, Sand/Kiesel für Flächen im Sheet, ein warmer Akzent (z. B. Ziegelrot norddeutscher Backstein) ausschließlich für Interaktion. Ampelfarben bleiben reine Funktionsfarben und werden nirgendwo dekorativ verwendet.
- **Typografie:** eine charaktervolle, gut lesbare Serifenlose für UI/Daten; Ortsnamen im Sheet dürfen eine eigene, kartografisch anmutende Display-Stimme haben (Anklang an Flusskarten-Beschriftung). Zahlen (km, Uhrzeiten) tabellarisch gesetzt.
- **Signature-Element (ein Vorschlag, gern ersetzen):** eine schmale "Flussleiste" am oberen Rand des expandierten Sheets — die Elbe als Linie mit dem aktuellen Punkt markiert, km-Stand daneben. Verortung auf einen Blick, ohne die Karte zu brauchen.
- **Outdoor-Tauglichkeit vor Schönheit:** hohe Kontraste (Sonne!), große Tap-Targets, `prefers-reduced-motion` respektieren, Sheet-Animation kurz und trocken.

## 6. Technik-Rahmen (fix)

- Leaflet + OSM-Raster-Tiles (Anbieter: OpenFreeMap o. ä.), kein Build-Step, eine HTML-Datei + JSON + Assets
- PWA: Manifest + Service Worker (App-Shell + JSON cachen; besuchte Tiles cachen)
- Hosting: GitHub Pages
- Optional: Elberadweg-GPX als dezente Routenlinie unter den Markern

## 7. Bewusst offen (hier darfst du gestalten)

- Exakte Marker-Formen und Icon-Sprache
- Sheet-Verhalten im Detail (Snap-Punkte, Handle-Design)
- Ausgestaltung von Layer-Toggle und Hervorhebungsmodus
- Signature-Element (Flussleiste ist Vorschlag, kein Muss)
- Dark Mode (nice-to-have für Abendplanung im Zelt)

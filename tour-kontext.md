# Kontext: Elbe-Tour Hamburg ↔ Elbquelle — Planungsstand für das Fahrradtool (PWA)

Dieses Dokument fasst den Planungsstand aus der Recherche (Stand 18.08.2026) zusammen und dient als
inhaltlicher Kontext für den Code-Auftrag. Es ergänzt den `design-brief-elbe-app.md` (UI/UX + Technik)
um die **echten Tour- und Streckendaten**.

---

## 1. Das Vorhaben in einem Absatz

Mehrtägige Fahrradreise entlang der Elbe zwischen Hamburg und der Elbquelle im Riesengebirge (CZ),
geplanter Start: **Donnerstag, 20.08.2026**. Dazu wird ein eigenes Tool gebaut: eine **mobile-first PWA**
(Leaflet + OSM, kein Build-Step, eine HTML-Datei + JSON), gehostet über **GitHub Pages**. Das Tool ist
kein Reiseführer, sondern ein Unterwegs-Werkzeug: Wo bin ich, was liegt voraus, wo schlafe ich, wo komme
ich über den Fluss.

### Wichtig: Fahrtrichtung ist noch nicht final

Im Planungsgespräch startet die Fahrt **nähe Hamburg → flussaufwärts zur Quelle**
(Hamburg → Wittenberge → Magdeburg → Dessau → Dresden → Děčín → Riesengebirge).
Design-Brief und Mockup tragen dagegen die Beschriftung „Quelle → Hamburg“. Die endgültige Richtung
soll kurz vor Abfahrt anhand der Windlage (ICON-DE-Daten, geoflow) festgelegt werden.
**Konsequenz für den Code:** Das Datenmodell sollte richtungsneutral sein — kanonische Achse ist
„km ab Quelle“ (bzw. eine feste km-Achse), die Anzeige („noch bis …“) muss für beide Richtungen
funktionieren oder zumindest leicht umstellbar sein. Auch das Punkteraster (Abschnitt 4) ist bewusst
richtungsunabhängig angelegt.

---

## 2. Eckdaten der Strecke

**Endpunkt Elbquelle:** Bis direkt an die Quelle darf nicht geradelt werden (Nationalpark Riesengebirge,
Radfahren nur auf freigegebenen Routen). Praktischer Ablauf:
Rad → **Labská bouda (Elbbaude)** → Rad abstellen → **~1 km zu Fuß** → Elbquelle.

**Distanz:** Hamburg ↔ Elbquelle entlang des Elberadwegs grob **1.050–1.100 km**.
(Gesamter ausgeschilderter Elberadweg Quelle–Cuxhaven: ca. 1.270–1.280 km; Hamburg–Cuxhaven davon ~130 km.)

**Profil:** Der Elberadweg ist überwiegend flach bzw. leicht, großteils Radwege oder verkehrsarme Straßen.
Das Finale im Riesengebirge ist die Ausnahme: Eine dokumentierte Quell-Etappe kommt auf **über 1.900 Höhenmeter**.

**Dauer (Bikepacking-Tempo, keine 50–60-km-Touristenetappen):**

| Tagesleistung | Fahrtage |
|---|---|
| 80 km/Tag | ca. 13–14 |
| 100 km/Tag | ca. 10–11 |
| 120 km/Tag | ca. 9 |
| 140 km/Tag | ca. 8 |

**Planungsansatz:** **11–12 Tage** — etwa 9–10 normale Fahrtage à ~100–120 km, für die letzten Tage in
Tschechien Luft lassen; der Schlussanstieg zur Labská bouda soll nicht nach einem ohnehin schon
120-km-Tag erzwungen werden. Der genaue Startpunkt („irgendwo nähe Hamburg“) und damit die konkrete
10-/11-Tage-Etappenaufteilung sind noch offen.

---

## 3. Datenhaltung: zwei getrennte Register

Die Planung wird bewusst in zwei getrennten Tabellen geführt (entspricht den zwei JSON-Dateien im Design-Brief):

- **A. Wegpunkte / POIs / Schlafen** — Orts-/POI-Kette entlang der Route (→ `waypoints.json`).
  *Liegt als „Punkteraster, Arbeitsversion 1“ vor, siehe Abschnitt 4.*
- **B. Elbquerungen** — Brücken + Fähren + aktueller Status (→ `crossings.json`).
  *Liegt als „Arbeitsversion 1“ vor, siehe Abschnitt 5.*

Erfassungsprinzipien für Register B:

- In Städten mit mehreren unmittelbar benachbarten Straßenbrücken reicht eine **Brückengruppe** plus
  besonders sinnvolle Radquerungen — nicht jede Brücke als eigener Wegpunkt.
- **Fähren werden einzeln und vollständig erfasst**, weil ihr Ausfall die Route stark beeinflusst.
- Grundsatz: **Fähren sind Optionen zum Uferwechsel, nie zwingende Glieder der Route**, sofern eine
  sinnvolle Brückenroute existiert. Brücken sind das Rückgrat.
- Querungen, die einzige verlässliche Querung in einem langen Abschnitt sind (z. B. Brücke Dömitz),
  gelten als **kritisch** und dürfen nie übersehen werden.

---

## 4. Punkteraster — Wegpunkte / POIs / Schlafen (Register A, Arbeitsversion 1)

Die Planung ist bewusst **kein Etappenplan**, sondern ein **routenunabhängiges Punkteraster**, das sich
später in beide Richtungen lesen lässt (passt zur noch offenen Fahrtrichtung, Abschnitt 1). Grundprinzip:
Punktabstand ~20–30 km; im Gebirge und im Elbsandsteingebirge stehen Punkte bewusst dichter bzw.
unregelmäßiger — es wird nichts aus dem Raster geworfen, nur um mathematisch schönere Abstände zu bekommen.
Die offiziellen Elberadweg-/Labská-stezka-Verzeichnisse bestätigen genau diese Ortskette, einschließlich
vieler kleinerer Orte.

Bewusste Entscheidungen:

- **Keine Bilder**; POIs spoilerfrei nur als **Name + Typ + Entfernung + Relevanz**.
- **Prag ist ausgelassen** — bleibt mögliche Anreiseoption, aber ab Mělník geht es an der Elbe weiter
  statt über den offiziellen touristischen Moldau-Abstecher (erzeugt Zusatzkilometer).
- **Entfernungen sind vorerst ≈-Kartenschätzungen:** „Elbe:“ = Entfernung zur Elbe, „Umweg:“ = Zusatzstrecke
  gegenüber elbnaher Durchfahrt. Sobald der endgültige GPX-Verlauf steht, werden die Werte **geometrisch
  gegen die Route gerechnet** (aus „≈300 m“ wird dann z. B. exakt „344 m Umweg“).
  → *Relevanz für den Code: Das Tool sollte diese Werte aus Daten beziehen, nicht hart verdrahten.*

### Legende

**POI-Relevanz 1–7:** 7 = dafür praktisch immer kurz stoppen · 5–6 = sehr guter kurzer Stopp ·
3–4 = anschauen, wenn es gerade passt · 1–2 = nur bei Interesse.

**Schlafen-Ampel:** 🟢 = belegte legale Zelt-/Campingmöglichkeit · 🟡 = guter Versorgungspunkt/Ort, aber
noch keine unmittelbare Zeltmöglichkeit verifiziert · 🔴 = freies Zelten hier nicht einplanen
(insbesondere Schutz-/Nationalpark). Die offiziellen Verzeichnisse führen viele Plätze unmittelbar am
Elberadweg auf, z. B. Pirna, Wittenberg, Aken, Tangermünde, Wittenberge und mehrere zwischen Hitzacker
und Geesthacht.

### 4.1 Riesengebirge → Hradec Králové

Punktabstand hier anfangs unregelmäßiger (kein künstlicher Punkt mitten im Gebirge). Offizielle
tschechische Route: Hradec–Špindlerův Mlýn ~95 km, ausdrücklich über Jaroměř, Dvůr Králové, Hostinné,
Vrchlabí. Les Království und Josefov werden im offiziellen Routenführer als Highlights hervorgehoben.

| Punkt | Δ etwa | POI (spoilerfrei) | Schlafen |
|---|---|---|---|
| Elbquelle / Labská bouda | Start | Elbquelle · Elbe: 0 m · Umweg: Bestandteil des Starts · 7/7 | 🔴 Nationalpark; hier nicht einplanen |
| Špindlerův Mlýn | ~15–20 km | Bílý most / Weiße Brücke · Elbe: ≈0 m · Umweg: ≈0–100 m · 4/7 | 🟡 touristischer Ort; Camping separat prüfen |
| Vrchlabí | ~15 km | Schloss Vrchlabí · Elbe: ≈350 m · Umweg: ≈700 m · 4/7 | 🟡 Versorgung/Bahn; nächste Möglichkeiten Richtung Hostinné |
| Hostinné | ~20–25 km | historischer Marktplatz · Elbe: ≈250 m · Umweg: ≈500 m · 4/7 | 🟡 |
| Dvůr Králové n. L. / Les Království | ~20–25 km | Les-Království-Talsperre · Elbe: 0 m · Umweg: praktisch Route · 6/7 | 🟡 |
| Jaroměř / Josefov | ~25 km | Festung Josefov · Elbe: ≈1 km · Umweg: ≈2–3 km · 6/7 | 🟡 |
| Hradec Králové | ~20 km | Hučák-Wasserkraftwerk · Elbe: 0 m · Umweg: ≈0–200 m · 5/7 | 🟡 große Stadt |

### 4.2 Hradec Králové → Mělník

Abschnitt, auf dem das 20–30-km-Prinzip am besten funktioniert. Offizielle Ortsliste u. a.: Pardubice,
Přelouč, Kolín, Poděbrady, Nymburk, Čelákovice, Brandýs, Neratovice, Mělník. Kolín–Poděbrady–Nymburk
gilt als attraktiver Abschnitt; Nymburks Stadtbefestigung ist hervorgehoben.

| Punkt | Δ etwa | POI | Schlafen |
|---|---|---|---|
| Pardubice | ~23 km | Automatické mlýny · Wasser: ≈0–100 m · Umweg: ≈500–800 m von der Elbroute · 5/7 | 🟡 große Stadt |
| Přelouč | ~20–25 km | Schleuse/Wasserkraftwerk Přelouč · Elbe: 0 m · Umweg: ≈0 m · 3/7 | 🟡 |
| Týnec nad Labem | ~20 km | historischer Ortskern · Elbe: ≈100 m · Umweg: ≈300 m · 3/7 | 🟡 |
| Kolín | ~15–20 km | St.-Bartholomäus-Bereich · Elbe: ≈500 m · Umweg: ≈1 km · 5/7 | 🟡 große Versorgung |
| Poděbrady | ~20 km | Schloss Poděbrady · Elbe: ≈50 m · Umweg: ≈100–200 m · 5/7 | 🟡 |
| Nymburk | ~10 km | mittelalterliche Stadtmauer · Elbe: ≈0–100 m · Umweg: ≈100–300 m · 5/7 | 🟡 |
| Čelákovice | ~25–30 km | Elbbrücke/Fußgängerbrücke · Elbe: 0 m · Umweg: ≈0 m · 3/7 | 🟡 |
| Brandýs nad Labem | ~15 km | Schloss Brandýs · Elbe: ≈150 m · Umweg: ≈400 m · 5/7 | 🟡 |
| Neratovice | ~20 km | Elbufer/Brückenbereich · Elbe: 0 m · Umweg: ≈0 m · 2/7 | 🟡 eher Funktionspunkt |
| Mělník | ~15–20 km | Zusammenfluss-Aussicht/Schlossbereich · Elbe: ≈400–500 m · Umweg: ≈1 km + etwas Höhe · 7/7 | 🟡 großer Pausenpunkt |

### 4.3 Mělník → Dresden

Děčín–Bad Schandau–Königstein–Pirna–Dresden werden vom regionalen Tourismusverband mit ~68 km angegeben —
diese Punkte stehen deshalb absichtlich dichter als 25 km. Camping in Königstein, Pirna und Dresden ist
dokumentiert.

| Punkt | Δ etwa | POI | Schlafen |
|---|---|---|---|
| Roudnice nad Labem | ~25 km | Schloss Roudnice · Elbe: ≈250 m · Umweg: ≈500–800 m · 5/7 | 🟡 |
| Litoměřice | ~20–25 km | historischer Stadtkern · Elbe: ≈600 m · Umweg: ≈1,2 km · 5/7 | 🟡 |
| Ústí nad Labem / Střekov | ~20–25 km | Burg Střekov · Elbe: ≈100 m horizontal · Umweg: ≈1–2 km + Anstieg · 6/7 | 🟡 |
| Děčín | ~20–25 km | Schloss Děčín · Elbe: ≈100 m · Umweg: ≈300 m · 6/7 | 🟡 |
| Hřensko / Schmilka | ~15 km | Grenz-/Elbtalpunkt · Elbe: 0 m · Umweg: ≈0 m · 4/7 | 🟢 Camping Hřensko, direkt an der Elbe |
| Bad Schandau | ~10 km | historischer Personenaufzug · Elbe: ≈400 m · Umweg: ≈800 m · 5/7 | 🟢 Ostrauer Mühle, aber ≈3 km von der Elbe |
| Königstein | ~10 km | Festung Königstein · Elbe: ≈1 km horizontal · Umweg: mehrere km + deutlicher Anstieg · 7/7 | 🟢 Camping/Treidlercamping unmittelbar im Elbtal |
| Pirna | ~15–20 km | Marktplatz/Canalettohaus · Elbe: ≈500 m · Umweg: ≈1 km · 5/7 | 🟢 Wasserplatz Pirna, unmittelbar an der Elbe |
| Dresden | ~20–25 km | Brühlsche Terrasse · Elbe: ≈0–100 m · Umweg: ≈100–300 m · 7/7 | 🟢 mehrere Optionen; Wostra elbnah |

### 4.4 Dresden → Magdeburg

Campingmöglichkeiten hier besonders gut dokumentiert: u. a. Riesa, Wittenberg direkt am Radweg, Coswig,
Aken sowie mehrere um Schönebeck und Magdeburg.

| Punkt | Δ etwa | POI | Schlafen |
|---|---|---|---|
| Radebeul | ~10–15 km | Schloss Wackerbarth · Elbe: ≈1 km · Umweg: ≈2–3 km · 4/7 | 🟡; Dresden/Meißen als grüne Nachbarn |
| Meißen | ~15 km | Albrechtsburg & Dom · Elbe: ≈300–400 m · Umweg: ≈1 km + Anstieg · 7/7 | 🟢 Camping direkt an der Elbe |
| Riesa | ~25–30 km | Elbpromenade/Hafenbereich · Elbe: 0 m · Umweg: ≈0 m · 3/7 | 🟢 Wassersportverein/Zeltplatz an der Elbe |
| Strehla | ~10–15 km | historischer Markt/Schlossbereich · Elbe: ≈200 m · Umweg: ≈400–600 m · 4/7 | 🟢 Camping Nixenbad |
| Torgau | ~25 km | Schloss Hartenfels · Elbe: ≈100 m · Umweg: ≈300 m · 7/7 | 🟢 Campingplatz Torgau |
| Elster (Elbe) | ~25–30 km | Elbufer/Kanuverein · Elbe: 0 m · Umweg: ≈0 m · 2/7 | 🟢 Kanuverein Harmonie |
| Lutherstadt Wittenberg | ~15 km | Schlosskirche · Elbe: ≈1 km · Umweg: ≈2 km · 7/7 | 🟢 Marina-Camp, direkt an Elbe und Radweg |
| Coswig (Anhalt) | ~20 km | Schloss Coswig · Elbe: ≈100 m · Umweg: ≈300 m · 4/7 | 🟢 Kanuverein/weitere Campingoptionen |
| Dessau-Roßlau | ~20–25 km | Kornhaus · Elbe: ≈0–100 m · Umweg: gering · 6/7 | 🟢 Campingmöglichkeiten im Stadtgebiet |
| Aken (Elbe) | ~20 km | Altstadt/St.-Nikolai · Elbe: ≈300 m · Umweg: ≈600 m · 3/7 | 🟢 Boot & Campingservice Aken, Elb-km 276 |
| Barby | ~20–25 km | Elbe-Saale-Mündungsbereich · Elbe: ≈0 m · Umweg: gering · 4/7 | 🟢 Seepark Barby, allerdings nicht unmittelbar Elbufer |
| Schönebeck | ~15 km | Salzblume · Elbe: ≈0 m · Umweg: praktisch 0 m · 4/7 | 🟡; mehrere Campingplätze im Umfeld |
| Magdeburg | ~20 km | Magdeburger Dom · Elbe: ≈200 m · Umweg: ≈400–600 m · 7/7 | 🟢 Camping/Stellplätze; Petriförder direkt an der Elbe |

### 4.5 Magdeburg → Wittenberge

Wieder ländlicher — Zwischenpunkte deshalb besonders wichtig. Offizielle Ortsliste führt hier auch
Hohenwarthe, Jerichow, Rogätz, Arneburg, Sandau, Werben usw. Die Campingkette
Bertingen → Tangermünde → Havelberg → Werben → Wittenberge ist brauchbar und in Verzeichnissen geführt.

| Punkt | Δ etwa | POI | Schlafen |
|---|---|---|---|
| Hohenwarthe | ~20 km | Wasserstraßenkreuz / Kanalbrücke · Elbe: ≈500–1.000 m · Umweg: ≈1–2 km · 7/7 | 🟡 |
| Bertingen / Bittkau | ~20–25 km | Elblandschaft · Elbe: ≈0–500 m · Umweg: gering · 2/7 | 🟢 Family-Camp/Kellerwiehl bzw. Bertingen |
| Tangermünde | ~20–25 km | Elbtor/Stadtbefestigung · Elbe: ≈0–100 m · Umweg: ≈200 m · 7/7 | 🟢 Wassersportverein/Naturcamping |
| Arneburg | ~20 km | Elbhang/Altstadtbereich · Elbe: ≈100 m · Umweg: ≈300 m · 4/7 | 🟡 |
| Sandau / Havelberg | ~25–30 km | Havelberger Dom · vom Elbstrom mehrere km · Umweg je nach Routenseite relevant · 6/7 | 🟢 Campinginsel Havelberg |
| Werben (Elbe) | ~20–25 km | historischer Ortskern · Elbe: ≈1 km · Umweg: ≈2 km · 5/7 | 🟢 Campingplatz „Am Elberadweg“ |
| Wittenberge | ~25–30 km | Alte Ölmühle · Elbe: ≈100 m · Umweg: ≈200–400 m · 5/7 | 🟢 Friedensteich / elbwärts 455 |

### 4.6 Wittenberge → Hamburg

| Punkt | Δ etwa | POI | Schlafen |
|---|---|---|---|
| Lenzen (Elbe) | ~25 km | Burg Lenzen · Elbe: ≈1,5–2 km · Umweg: ≈3–4 km · 5/7 | 🟡/🟢 Camping-/Stellmöglichkeiten; alternativ Wittenberge oder Vietze |
| Schnackenburg / Gartow | ~20–25 km | Grenzlandmuseum Schnackenburg · Elbe: ≈100 m · Umweg: ≈200 m · 5/7 | 🟢 Laascher See bzw. Vietze in der Umgebung |
| Dömitz | ~25 km | Festung Dömitz · Elbe: ≈100–200 m · Umweg: ≈400 m · 6/7 | 🟢 Wasserwanderzentrum |
| Hitzacker | ~25 km | Altstadtinsel · Elbe: ≈0–200 m · Umweg: gering · 5/7 | 🟢 Campingmöglichkeiten |
| Neu Darchau | ~20–25 km | Elbfähre/Ufer · Elbe: 0 m · Umweg: 0 m · 2/7 | 🟢 Campingplatz Elbufer bei Klein Kühren |
| Bleckede | ~20–25 km | Schloss Bleckede/Biosphaerium · Elbe: ≈500 m · Umweg: ≈1 km · 4/7 | 🟢 mehrere Campingplätze im Raum Bleckede |
| Lauenburg/Elbe | ~25–30 km | historische Unterstadt · Elbe: ≈0 m · Umweg: praktisch 0 m · 6/7 | 🟢 Bullendorf/Artlenburg als nahe Alternativen |
| Geesthacht / Tesperhude | ~20 km | Geesthachter Staustufe · Elbe: 0 m · Umweg: abhängig von Uferseite gering · 4/7 | 🟢 Camping Hohes Elbufer, direkt an der Elbe |
| Zollenspieker | ~20–25 km | Zollenspieker/Fährstelle · Elbe: 0 m · Umweg: 0 m · 4/7 | 🟢 Stover Strand auf der Gegenseite als Option |
| Hamburg Zentrum | ~25–30 km | Elbphilharmonie · Elbe: 0 m · Umweg: praktisch keiner bei passender Hineinroutung · 7/7 | Ziel |

### Hinweis fürs Datenmodell (`waypoints.json`)

Das Punkteraster bringt gegenüber dem Beispiel-Schema im Design-Brief zusätzliche Felder mit, die das
Datenmodell abbilden sollte: **POI-Relevanz (1–7)**, **Entfernung zur Elbe** und **Umweg** getrennt
(beide zunächst als ≈-Schätzung, später geometrisch aus dem GPX berechnet), sowie ein
**Schlaf-Ampelstatus (🟢/🟡/🔴)** pro Punkt — zusätzlich zur Liste konkreter Schlafplätze mit Telefon.
Ein Flag „Schätzwert vs. berechnet“ für die Distanzen wäre sinnvoll.

---

## 5. Querungsregister (Register B, Arbeitsversion 1 — Status vom 18.08.2026)

Route-relevante Querungen zwischen Elbquelle und Hamburg.
Legende: 🟢 in Betrieb · 🟢\* in Betrieb, aber am Durchfahrtstag live prüfen (wasserstandsabhängig) ·
🟡 eingeschränkt / vorher prüfen · 🔴 außer Betrieb, nicht einplanen.

| Bereich | Querung | Art | Betrieb / Zeiten im August | Status 18.08.26 | Bedeutung |
|---|---|---|---|---|---|
| Ústí-Region | Církvice – Dolní Zálezly | Fähre | täglich 09:00–18:00 | 🟢 | optionale Uferwahl |
| Lovosice | Lovosice – Píšťany | Fähre | täglich 08:00–20:00 | 🟢 | optional |
| Žernoseky | Malé – Velké Žernoseky | Fähre | täglich 09:00–19:00 | 🟢 | optional |
| Děčín | mehrere Stadtbrücken | Brücken | jederzeit | 🟢 | sichere Querung |
| Hřensko/Schöna | Schöna – Hřensko | Fähre | täglich 07:25–21:30 | 🟢 | sehr brauchbar |
| Schmilka | Schmilka – Hirschmühle | Fähre | Pendel-/VVO-Betrieb | 🟢\* | Uferwechsel möglich |
| Bad Schandau | Bahnhof ↔ Ort / Krippen | Fähren | VVO-Betrieb | 🟢\* | mehrere Optionen |
| Königstein | Königstein | Fähre | Mo–Fr 04:50–23:15, WE 05:50–23:15 | 🟢 | hervorragende Querung |
| Rathen | Rathen | Gierfähre | Mo–Fr 04:30–01:00, WE 05:30–01:00 | 🟢 | sehr flexibel |
| Stadt Wehlen | Fähre | Fähre | VVO | 🟠 bis 19.08. Niedrigwasser | ab 20.08. erneut prüfen |
| Pirna | Pirna – Copitz | Fähre | VVO | 🟢\* | Stadtbrücke direkt als Backup |
| Pirna | Stadtbrücke | Brücke | 24/7 | 🟢 | sehr gutes Backup |
| Dresden-Pillnitz | Pillnitz – Kleinzschachwitz | Fähre | täglich 06:00–22:00 | 🟢 | Autofähre + Räder |
| Dresden | Niederpoyritz – Laubegast | Fähre | Mo–Fr 07–20, WE 11–22 | 🟢 | optional |
| Dresden | Blaues Wunder | Brücke | jederzeit | 🟢 (Radverkehr) | wichtige Querung |
| Dresden | Johannstadt – Neustadt | Fähre | Mo–Fr 07–20, WE 11–20, nach Bedarf | 🟢 | optional |
| Dresden | Albert-/Marien-/Waldschlößchenbrücke | Brücken | jederzeit | 🟢 | mehrere sichere Querungen |
| Dresden | Carolabrücke | Brücke | – | 🔴 existiert derzeit nicht | nicht einplanen |
| Coswig/Sachsen | Kötitz – Gauernitz | Fähre | Mo–Fr 06–20, WE 09:30–12 & 13–20 | 🟢 | guter Uferwechsel |
| Meißen | Stadt-/Altstadtbrücken | Brücken | jederzeit | 🟢 | sichere Querung |
| Seußlitz | Seußlitz – Niederlommatzsch | Fähre | nach Bedarf | 🟢\* | optional |
| Riesa | Riesa – Promnitz | Fähre | normalerweise saisonal | 🔴 03.08.–26.11. außer Betrieb (Umbau) | Stadtbrücke nehmen |
| Riesa | Stadtbrücke Riesa | Brücke | jederzeit | 🟢 | offizieller Ersatz |
| Strehla | Strehla – Lorenzkirch | Fähre | Mo–Fr 06–20, WE 09:30–12 & 13–20 | 🟢 | brauchbar |
| Belgern | Belgern | Fähre | Mo–Fr 06–10 & 13–17 | 🔴 Niedrigwasser, bis auf Weiteres | nicht darauf bauen |
| Torgau | Straßenbrücke | Brücke | jederzeit | 🟢 | sichere Querung |
| Dommitzsch | Prettin – Dommitzsch | Gierfähre | Mo–Fr 05–19, WE 09–18 | 🟢\* | einer von 3 Wechseln |
| Pretzsch | Pretzsch – Mauken | Gierfähre | Mo–Fr 05:30–19:30, WE 09–19 | 🟢\* | optional |
| Elster | Elster – Wartenburg | Gierfähre | Mo–Fr 05:30–19, WE 10–18 | 🟢\* | wichtig für Uferwahl |
| Wittenberg | Elbbrücke | Brücke | jederzeit | 🟢 | sehr sichere Querung |
| Coswig/Anhalt | Coswig – Wörlitz | Gierfähre | nur Fr–So bei Betrieb | 🔴 aktuell Niedrigwasser | Vockerode/Wittenberg nutzen |
| Vockerode | Autobahn-/Elbquerung mit Radführung | Brücke | jederzeit | 🟢 | offizielles Fähren-Backup |
| Dessau/Brambach | Brambach | Fähre | saisonal | 🟢\* | optional |
| Aken | Gierfähre Aken | Fähre | Mo–Fr 05:30–20, Sa 07–20, So 08–20 | 🟢\* | sehr brauchbar |
| Breitenhagen | Breitenhagen | Gierfähre | normal Mo–Fr 05–19:30, WE 09–18 | 🔴 12.–28.08. außer Betrieb | nicht einplanen |
| Schönebeck | Elbbrücke | Brücke | jederzeit | 🟢 | verlässliche Querung |
| Magdeburg | mehrere Elbbrücken | Brücken | jederzeit | 🟢 | sehr viele Möglichkeiten |
| Magdeburg-Buckau | Motorfähre | Fähre | saisonal | 🟢\* | eher optional |
| Rogätz | Rogätz – Schartau | Motorfähre | Mo–Fr 05:45–12 & 12:30–20; WE 08–12 & 12:30–20 | 🟡 Wasserstand prüfen | wichtig |
| Ferchland | Ferchland – Grieben | Fähre | saisonal | 🟢\* | wichtiger Uferwechsel |
| Tangermünde | Elbbrücke B188 | Brücke | jederzeit | 🟢 | sichere Querung |
| Arneburg | Fähre | Fähre | normalerweise saisonal | 🔴 Niedrigwasser, eingestellt | nicht verwenden |
| Sandau | Elbbrücke | Brücke | jederzeit | 🟢 | sichere Alternative |
| Räbel/Werben | Räbel – Havelberg-Seite | Fähre | Mo–Fr 05:30–21, WE 08–21 | 🟢\* | sehr lange Betriebszeit |
| Wittenberge | Eisenbahnbrücke/Bohlenweg | Rad-/Fußquerung | jederzeit | 🟢 | 2025 saniert |
| Wittenberge | B189-Elbbrücke | Straßenbrücke | jederzeit | 🟢\* | alternative Querung |
| Lenzen | Lenzen – Pevestorf | Fähre | Mo–Fr 06–20, WE 08–20 | 🟡 wasserstandsabhängig | vorher checken |
| Schnackenburg | Schnackenburg – Lütkenwisch | Fähre | regulär 07–17 | 🔴 aktuell außer Betrieb | nicht darauf bauen |
| Dömitz | Straßenbrücke | Brücke | jederzeit | 🟢 | **sehr wichtig (kritisch)** |
| Hitzacker | Hitzacker – Bitter | Fahrrad-/Personenfähre | normal 09–18 | 🔴 bis mind. 23.08. Niedrigwasser | fällt für Tourstart aus |
| Neu Darchau | Neu Darchau – Darchau | Fähre | Mo–Sa 05:30–~21, So 09–~21 | 🔴 bis mind. 23.08. Niedrigwasser | aktuell nicht planen |
| Bleckede | Bleckede – Neu-Bleckede | Fähre | normalerweise Pendelbetrieb | 🔴 bis mind. 23.08. außer Betrieb | aktuell nicht planen |
| Lauenburg | Elbbrücke B209 | Brücke | jederzeit | 🟢 | zentrale sichere Querung |
| Geesthacht | Elbbrücke / Staustufe | Brückenquerung | jederzeit bzw. radwegabhängig | 🟢\* | sehr brauchbar |
| Zollenspieker | Zollenspieker – Hoopte | Fähre | Pendelfähre | 🟢\* | häufige Querung |
| Hamburg | Elbbrücken | Brücken | jederzeit | 🟢 | mehrere Querungen |
| Hamburg | Alter Elbtunnel | Tunnel | 24/7 | 🟢 | hervorragende Fahrradquerung |
| Hamburg | Finkenwerder – Teufelsbrück | HADAG | Linienbetrieb | 🟢 | Radmitnahme |
| Hamburg | Finkenwerder – Landungsbrücken | HADAG | Linienbetrieb | 🟢 | Radmitnahme |
| Hamburg | Blankenese – Finkenwerder | Fähre | Linienbetrieb | 🟢 | Cranz/Neuenfelde derzeit nicht bedient |

Anmerkungen zum Register:

- Die offizielle Elberadweg-Datenbank führt insgesamt **mehr als 30 Fähren**; das Register umfasst die
  für den Korridor Quelle–Hamburg planungsrelevanten Querungen (kein Anspruch auf Vollständigkeit).
- **Semantik der Betriebszeiten:** Viele kleine Elbfähren haben keinen Taktfahrplan. „06:00–20:00“
  bedeutet typischerweise **Pendel-/Bedarfsbetrieb** innerhalb dieses Fensters (Fähre fährt, wenn
  Fahrgäste anstehen); bei einzelnen ist das ausdrücklich so angegeben (z. B. Johannstadt–Neustadt,
  Seußlitz–Niederlommatzsch). Nur große ÖPNV-Fähren (HADAG Hamburg, VVO) haben konkrete Abfahrten.
- Alle 🟢\*-Einträge sind am tatsächlichen Durchfahrtstag noch einmal live zu prüfen (niedriger Elbpegel).

---

## 6. Aktuelle Lage rund um den Start (20.08.2026)

Es gibt derzeit einen auffälligen **Niedrigwasser-Cluster**:

- **Wegen Niedrigwasser eingestellt:** Belgern, Coswig/Anhalt, Arneburg; im Norden Hitzacker–Bitter,
  Neu Darchau–Darchau und Bleckede–Neu-Bleckede (alle drei bis mind. 23.08.).
- **Unabhängig davon außer Betrieb:** Riesa–Promnitz (Umbau bis 26.11., Ersatz laut Baustelleninfo:
  Stadtbrücke Riesa) und Breitenhagen (12.–28.08.).
- **Stadt Wehlen** war bis 19.08. wegen Niedrigwasser aus → ab 20.08. neu prüfen.
- **Dresden, Sondervermerk:** Die **Carolabrücke existiert derzeit nicht als Querung** (eingestürzter Teil
  vollständig abgerissen, Neubauverfahren läuft 2026). Alternativen: Blaues Wunder, Waldschlößchen-,
  Albert- und Marienbrücke sowie mehrere Fähren.
- **Wittenberge:** Radquerung an der Eisenbahnbrücke wieder frei, Bohlenweg 2025 vollständig saniert.

Das beeinflusst die Reise weniger als es klingt, solange die Hauptlinie über Brücken geplant wird.
Die Statuslage ist aber **sehr dynamisch** (Wasserstand kann sich binnen Tagen ändern) — geplant ist,
das Register am Abend vor der Abfahrt bzw. vor jedem Durchfahrtstag erneut gegen aktuelle Meldungen
zu prüfen (perspektivisch automatisiert). Daher im Tool: **Datenstand („Stand: TT.MM.“) immer sichtbar.**

---

## 7. Bezug zu den vorhandenen Dateien im Ordner `fahrradtool`

- **`design-brief-elbe-app.md`** — maßgeblich für UI/UX und Technik: Karte = App (Vollbild, Leaflet + OSM),
  drei Marker-Klassen (Wegpunkt/Schlafplatz/Querung), Ampelstatus inkl. eigenem Status „grün-prüfen“,
  Bottom Sheet mit Peek/Expand, Datenmodell `waypoints.json` + `crossings.json`, PWA mit Service Worker,
  GitHub Pages, kein Build-Step.
- **`README.md`** — HTML-**Design-Mockup** (DC-Komponente, nutzt `support.js`). **Achtung: Die dort
  eingebetteten Daten sind Platzhalter/Demo-Daten** und widersprechen teils der echten Recherche
  (z. B. dort „Fähre Aken 🔴 Motorschaden“ — real 🟢\*; Gesamtlänge dort 1021 km; erfundene Telefonnummern
  und Schlafplätze). Für die produktive App gelten die Daten aus diesem Dokument, nicht die Mockup-Daten.
  Das Mockup ist als Design-/Interaktionsreferenz zu verstehen.
- **`support.js`** — Runtime für das Mockup.
- **`liste.txt`** — derzeit leer.

---

## 8. Offene Punkte

1. **Fahrtrichtung** final festlegen (Windlage / ICON-DE, kurz vor Abfahrt).
2. **Genauer Startpunkt** nähe Hamburg → daraus konkrete Etappenaufteilung (10–11 Tage à ~100–120 km).
3. **Distanzen im Punkteraster** („Elbe:“ / „Umweg:“) geometrisch gegen den endgültigen GPX-Verlauf
   rechnen — bisher ≈-Kartenschätzungen.
4. **🟡-Punkte im Punkteraster** (v. a. Tschechien) auf konkrete Zelt-/Campingmöglichkeiten verifizieren;
   Telefonnummern und Umweg-km der Schlafplätze ergänzen.
5. Querungsregister vor Abfahrt und unterwegs **gegen aktuelle Meldungen aktualisieren** (Pflege = eine
   Zeile im JSON ändern und pushen).

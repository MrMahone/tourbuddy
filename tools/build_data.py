"""Schritt 2-5: Register gegen OSM praezisieren und swim.json erzeugen.

  * km-Achse aus der echten Radweg-Geometrie (Projektion auf die Primaerachse)
  * Ortskoordinaten aus OSM place-Knoten
  * Querungen auf echte Faehranleger bzw. auf den Flusslauf snappen
  * Schlafplaetze auf echte Campingplatz-Koordinaten inkl. Telefonnummer
  * Bademoeglichkeiten (Elbstrand + See) im Umkreis der Route

Aufruf:
  python tools/build_data.py             Bericht, schreibt nichts
  python tools/build_data.py --write     Register aktualisieren (mit .bak-Backup)

build_route.py muss vorher gelaufen sein (liefert tools/.cache/banks.json).
"""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osm_common as oc  # noqa: E402

# Windows-Konsole ist cp1252 und stolpert ueber tschechische Namen.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SWIM_MAX_DETOUR_KM = 2.0     # weiter weg lohnt auf einem 100-km-Tag nicht
ELBE_NEAR_KM = 0.35         # so nah am Strom = Elbstrand, sonst See
NAME_MIN = 0.34             # Mindest-Namensaehnlichkeit fuer eine Zuordnung
PLACE_NAME_MIN = 0.50       # Orte strenger: falsche Treffer verschieben die km-Achse
PLACE_MAX_SHIFT_KM = 5.0    # weiter weg ist kein Zuordnungsfehler mehr, sondern Zufall

ELBE_WARN = ('Elbe: starke Stroemung, Sog an den Buhnen und Berufsschifffahrt. '
             'Nicht in der Fahrrinne, nicht allein, nicht bei Wellen von Schiffen.')


# Overpass liefert bei zu langen around-Listen stillschweigend null Treffer
# (gemessen: 40 und 90 Stuetzpunkte liefern Daten, 180 liefert leer). Daher
# in Bloecke zerlegen und die Ergebnisse per Union zusammenfassen.
AROUND_CHUNK = 60


def around_chunks(line, step_km=5.0, radius_m=2500):
    """Liste von around-Filtern entlang einer ausgeduennten Linie."""
    cum = oc.cumulative(line)
    pts, nxt = [], 0.0
    for p, k in zip(line, cum):
        if k >= nxt:
            pts.append(p)
            nxt = k + step_km
    if pts[-1] != line[-1]:
        pts.append(line[-1])
    out = []
    for i in range(0, len(pts), AROUND_CHUNK):
        # ein Punkt Ueberlappung, damit an den Blockgrenzen keine Luecke entsteht
        block = pts[i:i + AROUND_CHUNK + 1]
        coords = ','.join('%.5f,%.5f' % (p[0], p[1]) for p in block)
        out.append('(around:%d,%s)' % (radius_m, coords))
    return out, len(pts)


def query_around(selectors, line, step_km, radius_m, tag):
    """selectors: Liste wie ['node["place"="town"]', 'way["natural"="beach"]']."""
    chunks, n = around_chunks(line, step_km, radius_m)
    body = ''.join('%s%s;' % (sel, cl) for cl in chunks for sel in selectors)
    q = '[out:json][timeout:300];(%s);out tags center;' % body
    print('    %-12s %d Stuetzpunkte in %d Bloecken' % (tag, n, len(chunks)))
    return oc.overpass(q, tag)['elements']


def query_around_geom(selectors, line, step_km, radius_m, tag):
    """Wie query_around, aber mit Geometrie statt nur Mittelpunkt."""
    chunks, n = around_chunks(line, step_km, radius_m)
    body = ''.join('%s%s;' % (sel, cl) for cl in chunks for sel in selectors)
    q = '[out:json][timeout:300];(%s);out tags geom;' % body
    print('    %-12s %d Stuetzpunkte in %d Bloecken (mit Geometrie)' % (tag, n, len(chunks)))
    return oc.overpass(q, tag)['elements']


def fetch_places(route):
    return query_around(['node["place"~"^(city|town|village)$"]'],
                        route, 6.0, 4000, 'places')


def fetch_ferries(route):
    return query_around(['node["amenity"="ferry_terminal"]',
                         'way["amenity"="ferry_terminal"]'],
                        route, 5.0, 3000, 'ferries')


def fetch_bridges(route):
    return query_around(['way["bridge"]["name"]', 'way["man_made"="bridge"]["name"]'],
                        route, 5.0, 3000, 'bridges')


def fetch_camps(route):
    return query_around(['node["tourism"="camp_site"]', 'way["tourism"="camp_site"]'],
                        route, 5.0, 5000, 'camps')


def fetch_swim(route):
    return query_around(['node["natural"="beach"]', 'way["natural"="beach"]',
                         'node["leisure"="swimming_area"]', 'way["leisure"="swimming_area"]'],
                        route, 4.0, 2500, 'swim')



CLUSTER_KM = 0.4          # naeher zusammen = dieselbe Stelle, mehrfach erfasst
UNNAMED_EVERY_KM = 3.0    # unbenannte Straende ausduennen, sonst 130 Marker Rauschen


def condense(items):
    """Mehrfacherfassungen zusammenfassen und unbenannte Straende ausduennen.

    Behalten wird immer: alles mit eigenem Namen und alles, was ausdruecklich als
    Badebereich getaggt ist. Unbenannte Straende sind oft nur kartierte Sandflaechen
    und wuerden die Karte zumuellen - davon bleibt hoechstens einer je 3 km.
    """
    def rank(it):
        return (0 if not it['unnamed'] else 1,
                0 if it.get('tagged_area') else 1,
                it['detourKm'])

    keep, out = [], []
    for it in items:
        dup = None
        for k in keep:
            if abs(k['km'] - it['km']) <= 5 and oc.hav(tuple(k['coords']), tuple(it['coords'])) <= CLUSTER_KM:
                dup = k
                break
        if dup is None:
            keep.append(it)
        elif rank(it) < rank(dup):
            keep[keep.index(dup)] = it

    last_unnamed_km = -1e9
    for it in sorted(keep, key=lambda x: x['km']):
        if it['unnamed'] and not it.get('tagged_area'):
            if it['km'] - last_unnamed_km < UNNAMED_EVERY_KM:
                continue
            last_unnamed_km = it['km']
        out.append(it)
    for it in out:
        it.pop('tagged_area', None)
    return out


def pos(el):
    c = el.get('center') or el
    if 'lat' not in c:
        return None
    return (c['lat'], c['lon'])


def best_match(name, coords, cands, max_km, min_name=NAME_MIN):
    """Kandidat mit bester Kombination aus Namensaehnlichkeit und Naehe."""
    best, best_score = None, 0.0
    for el in cands:
        p = pos(el)
        if p is None:
            continue
        d = oc.hav(coords, p)
        if d > max_km:
            continue
        ns = oc.name_score(name, el.get('tags', {}).get('name'))
        if ns < min_name:
            continue
        score = ns - 0.02 * d          # Namensgleichheit zaehlt, Naehe bricht Gleichstand
        if score > best_score:
            best, best_score = el, score
    return best


def main():
    write = '--write' in sys.argv
    with open(os.path.join(oc.CACHE, 'banks.json'), encoding='utf-8') as fh:
        banks = json.load(fh)
    route = [tuple(p) for p in banks['primary']]
    rcum = oc.cumulative(route)
    total = rcum[-1]
    river, _ = oc.river_axis()

    print('Primaerachse: %.1f km, %d Punkte' % (total, len(route)))
    print('Modus: %s\n' % ('SCHREIBEN' if write else 'nur Bericht (--write zum Uebernehmen)'))

    wp = oc.load('waypoints.json')
    cx = oc.load('crossings.json')

    print('OSM-Daten holen')
    places = fetch_places(route)
    ferries = fetch_ferries(route)
    bridges = fetch_bridges(route)
    camps = fetch_camps(route)
    swim_raw = fetch_swim(route)
    print()

    # ---------------------------------------------------------------- Wegpunkte
    print('=' * 78)
    print('WEGPUNKTE: Ortskoordinaten und km')
    print('=' * 78)
    print('%-30s %8s %8s %7s  %s' % ('Ort', 'km alt', 'km neu', 'versch.', 'Quelle'))
    moved = 0
    for w in wp['items']:
        old_coords = tuple(w['coords'])
        old_km = w['km']
        src = 'eigene Angabe'
        # Nur uebernehmen, wenn der Name klar passt und die Verschiebung klein ist.
        # Zusammengesetzte Namen ("Sandau / Havelberg") werden Teil fuer Teil geprueft,
        # POIs (Elbquelle, Hamburg Zentrum) gar nicht - das sind keine place-Knoten.
        if w.get('type') != 'poi':
            for part in [q.strip() for q in w['name'].split('/')]:
                m = best_match(part, old_coords, places, PLACE_MAX_SHIFT_KM, PLACE_NAME_MIN)
                if not m:
                    continue
                new_coords = pos(m)
                shift = oc.hav(old_coords, new_coords)
                w['coords'] = [round(new_coords[0], 6), round(new_coords[1], 6)]
                src = 'OSM place'
                if shift > 0.3:
                    moved += 1
                break
        km, dist, _ = oc.project(tuple(w['coords']), route, rcum)
        w['km'] = int(round(km))
        w['routeDistKm'] = round(dist, 2)
        w['estimate'] = (src == 'Schaetzung')
        print('%-30s %8d %8d %7.1f  %s%s'
              % (w['name'][:30], old_km, w['km'], oc.hav(old_coords, tuple(w['coords'])),
                 src, '  [%.1f km von der Route]' % dist if dist > 3 else ''))
    print('\n  %d von %d Orten aus OSM verschoben (>300 m)' % (moved, len(wp['items'])))

    # ---------------------------------------------------------------- Querungen
    print('\n' + '=' * 78)
    print('QUERUNGEN: Position und km')
    print('=' * 78)
    stats = {'osm': 0, 'fluss': 0}
    for c in cx['items']:
        old = tuple(c['coords'])
        cands = ferries if c['kind'] in ('faehre', 'gierfaehre') else bridges
        m = best_match(c['name'], old, cands, 6.0)
        if m:
            c['coords'] = [round(pos(m)[0], 6), round(pos(m)[1], 6)]
            c['estimate'] = False
            src = 'OSM ' + (m.get('tags', {}).get('name') or '')[:26]
            stats['osm'] += 1
        else:
            lat, lon, d = oc.snap_to(old, river)
            c['coords'] = [round(lat, 6), round(lon, 6)]
            c['estimate'] = True
            src = 'auf den Fluss (%.2f km)' % d
            stats['fluss'] += 1
        km, dist, _ = oc.project(tuple(c['coords']), route, rcum)
        c['km'] = int(round(km))
        print('%-42s %5d -> %5d km  %5.2f km versch.  %s'
              % (c['name'][:42], c.get('km_old', 0) or 0, c['km'],
                 oc.hav(old, tuple(c['coords'])), src))
    print('\n  %d Querungen auf OSM-Objekte, %d auf den Flusslauf gesnappt'
          % (stats['osm'], stats['fluss']))

    # ------------------------------------------------------------- Schlafplaetze
    print('\n' + '=' * 78)
    print('SCHLAFPLAETZE: echte Koordinaten und Telefon')
    print('=' * 78)
    hit = tel = 0
    for w in wp['items']:
        for s in (w.get('sleep') or []):
            m = best_match(s['name'], tuple(w['coords']), camps, 15.0, 0.30)
            if not m:
                print('  %-38s  kein OSM-Treffer (bleibt beim Ort)' % s['name'][:38])
                continue
            t = m.get('tags', {})
            s['coords'] = [round(pos(m)[0], 6), round(pos(m)[1], 6)]
            s['source'] = 'osm'
            hit += 1
            phone = t.get('phone') or t.get('contact:phone')
            if phone and not s.get('phone'):
                s['phone'] = phone.split(';')[0].strip()
                tel += 1
            km, dist, _ = oc.project(tuple(s['coords']), route, rcum)
            s['detourKm'] = round(dist, 1)
            print('  %-38s  %s  %s' % (s['name'][:38],
                                       '%.4f,%.4f' % tuple(s['coords']),
                                       s.get('phone') or '(keine Nummer)'))
    print('\n  %d von %d Schlafplaetzen in OSM gefunden, %d Telefonnummern ergaenzt'
          % (hit, sum(len(w.get('sleep') or []) for w in wp['items']), tel))

    # ------------------------------------------------------- Bademoeglichkeiten
    print('\n' + '=' * 78)
    print('BADEMOEGLICHKEITEN')
    print('=' * 78)
    swim, seen = [], set()
    for el in swim_raw:
        p = pos(el)
        if p is None:
            continue
        t = el.get('tags', {})
        km, dist, _ = oc.project(p, route, rcum)
        if dist > SWIM_MAX_DETOUR_KM:
            continue
        _, _, dr = oc.snap_to(p, river)
        kind = 'elbe' if dr <= ELBE_NEAR_KM else 'see'
        name = t.get('name') or ('Elbstrand' if kind == 'elbe' else 'Badestelle')
        key = (name, round(p[0], 3), round(p[1], 3))
        if key in seen:
            continue
        seen.add(key)
        item = {
            'id': '%s-%d' % (kind, el['id']),
            'name': name,
            'kind': kind,
            'coords': [round(p[0], 6), round(p[1], 6)],
            'km': int(round(km)),
            'detourKm': round(dist, 1),
            'unnamed': 'name' not in t,
            'tagged_area': t.get('leisure') == 'swimming_area',
            'supervised': t.get('supervised'),
            'fee': t.get('fee'),
            'surface': t.get('surface'),
            'note': ELBE_WARN if kind == 'elbe' else None,
            'source': 'osm',
            'osm': '%s/%d' % (el['type'], el['id']),
        }
        swim.append(item)
    swim.sort(key=lambda x: x['km'])
    swim = condense(swim)
    named = sum(1 for s in swim if not s['unnamed'])
    print('  %d Stellen im Umkreis von %.1f km zur Route' % (len(swim), SWIM_MAX_DETOUR_KM))
    print('  davon Elbstrand %d, See %d, mit eigenem Namen %d'
          % (sum(1 for s in swim if s['kind'] == 'elbe'),
             sum(1 for s in swim if s['kind'] == 'see'), named))
    print('\n  Beispiele:')
    for s in swim[:10]:
        print('   km %4d  %-32s %-5s Umweg %.1f km' % (s['km'], s['name'][:32], s['kind'], s['detourKm']))

    # ------------------------------------------------------------------ Schreiben
    wp['meta']['total'] = int(round(total))
    wp['meta']['routeFile'] = 'route.geojson'
    wp['meta']['estimate'] = False
    wp['meta']['axis'] = 'km ab Elbquelle, gemessen entlang der OSM-Radwegachse'
    wp['meta']['estimateNote'] = ('Koordinaten aus OpenStreetMap (place-Knoten bzw. Campingplatz), '
                                  'km-Werte durch Projektion auf die Radwegachse berechnet. '
                                  'Eintraege mit estimate:true haben kein OSM-Gegenstueck gefunden.')
    wp['meta']['source'] = 'OpenStreetMap contributors, ODbL'
    cx['meta']['estimate'] = False
    cx['meta']['source'] = 'OpenStreetMap contributors, ODbL (Positionen); Status aus eigener Recherche'
    cx['meta']['estimateNote'] = ('Positionen aus OSM-Faehranlegern bzw. auf den Flusslauf gesnappt. '
                                  'Status und Betriebszeiten stammen aus der eigenen Recherche, nicht aus OSM.')

    print('\n' + '=' * 78)
    print('PLAUSIBILITAET')
    print('=' * 78)
    kms = [w['km'] for w in wp['items']]
    print('  Wegpunkt-km monoton:  %s' % all(kms[i] <= kms[i + 1] for i in range(len(kms) - 1)))
    ckms = [c['km'] for c in cx['items']]
    print('  Querungs-km monoton:  %s' % all(ckms[i] <= ckms[i + 1] for i in range(len(ckms) - 1)))
    print('  Gesamt:               %d km' % wp['meta']['total'])
    far = [w['name'] for w in wp['items'] if w.get('routeDistKm', 0) > 5]
    print('  weiter als 5 km von der Route: %s' % (', '.join(far) if far else 'keiner'))

    if not write:
        print('\nNichts geschrieben. Mit --write uebernehmen.')
        return

    for f in ('waypoints.json', 'crossings.json'):
        src = os.path.join(oc.ROOT, f)
        if os.path.exists(src):
            shutil.copyfile(src, src + '.bak')
    oc.save('waypoints.json', wp)
    oc.save('crossings.json', cx)
    oc.save('swim.json', {
        'meta': {
            'source': 'OpenStreetMap contributors, ODbL',
            'maxDetourKm': SWIM_MAX_DETOUR_KM,
            'note': 'natural=beach und leisure=swimming_area im Umkreis der Radwegachse.',
            'warn': ELBE_WARN,
        },
        'items': swim,
    })
    print('\nGeschrieben: waypoints.json, crossings.json, swim.json (Backups als *.bak)')


if __name__ == '__main__':
    main()

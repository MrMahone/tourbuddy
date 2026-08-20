"""Querungen praezisieren: Position aus OSM-Faehrlinien, Status aus der
offiziellen Ausfallliste, dazu der zustaendige Elbe-Pegel als Deeplink.

Positionen:
  route=ferry Ways/Relations queren den Fluss - ihre Mitte ist die Querungsstelle.
  Das schliesst die Luecken, die amenity=ferry_terminal offen gelassen hat.

Status:
  https://www.elberadweg.de/news-service/baustellen-umleitungen-faehrausfall/
  (abgerufen 20.08.2026, Datumsangaben unten woertlich uebernommen)

Pegel:
  pegelonline.wsv.de REST-API v2 - Messstellen des Gewaessers ELBE mit
  offiziellem Elbe-km. Zugeordnet wird der naechstgelegene Pegel.

Aufruf:
  python tools/refine_crossings.py             Bericht
  python tools/refine_crossings.py --write     uebernehmen
"""
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osm_common as oc  # noqa: E402
import build_data as bd  # noqa: E402

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

STAND = '2026-08-20'
MAX_CROSSING_LINE_KM = 2.0   # breiter wird die Elbe hier nicht
MAX_GAUGE_KM = 25.0          # weiter weg sagt der Pegel nichts mehr aus
QUELLE_STATUS = 'elberadweg.de/news-service, abgerufen 20.08.2026'

# id -> (status, hours_or_None, note). Datumsangaben woertlich aus der Ausfallliste.
STATUS_UPDATE = {
    'bleckede-neu-bleckede': ('rot', None,
        'Ausfall wegen Niedrigwasser, 10.08.–23.08.2026 (Fähre „Amt Neuhaus“)'),
    'neu-darchau-darchau': ('rot', None,
        'Ausfall wegen Niedrigwasser, 27.07.–23.08.2026 (Fähre „Tanja“)'),
    'hitzacker-bitter': ('rot', None,
        'Ausfall wegen Niedrigwasser, 20.07.–23.08.2026'),
    'arneburg-faehre': ('rot', None,
        'Außer Betrieb 13.08.–30.08.2026'),
    'ferchland-grieben': ('rot', 'saisonal',
        'Außer Betrieb 12.08.–30.08.2026 — war bisher als eingeschränkt geführt, '
        'ist tatsächlich aus. Ersatz: Elbbrücke Tangermünde.'),
    'breitenhagen': ('rot', None,
        'Außer Betrieb 12.08.–28.08.2026'),
    'coswig-woerlitz': ('rot', None,
        'Ausfall bei Niedrigwasser bzw. eingeschränkte Fährzeiten, 01.06.–31.12.2026'),
    'belgern': ('rot', None,
        'Ausfall wegen Niedrigwasser, 13.07.–25.08.2026'),
    'riesa-promnitz': ('rot', None,
        'Außer Betrieb 03.08.–26.11.2026 (Umbau). Ersatz: Stadtbrücke Riesa.'),
}

# Baustellen und Umleitungen, die eine Querung direkt betreffen.
DETOUR_NOTE = {
    'rathen': 'Umleitung Königstein–Kurort Rathen bis 30.11.2026.',
    'koenigstein-faehre': 'Umleitung Königstein–Kurort Rathen bis 30.11.2026.',
    'pretzsch-mauken': 'Umleitung Kleindröben–Mauken bis 30.09.2026.',
    'wittenberge-eisenbahnbruecke': 'Umleitung Wittenberge wegen Brückenbau, bis 12.10.2029.',
    'wittenberge-b189': 'Umleitung Wittenberge wegen Brückenbau, bis 12.10.2029.',
}


def gauges():
    """Elbe-Messstellen von pegelonline. curl, weil urllib hier am Zertifikat scheitert."""
    url = ('https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations.json'
           '?waters=ELBE&includeTimeseries=true&includeCurrentMeasurement=true')
    r = subprocess.run(['curl', '-s', '--max-time', '120',
                        '-H', 'User-Agent: elbe-tour/1.0', url], capture_output=True)
    data = json.loads(r.stdout.decode('utf-8'))
    out = []
    for s in data:
        if s.get('latitude') is None:
            continue
        cur = None
        for ts in s.get('timeseries') or []:
            if ts.get('shortname') == 'W' and (ts.get('currentMeasurement') or {}).get('value') is not None:
                cur = ts['currentMeasurement']
        out.append({
            'name': s.get('longname', '').strip(),
            'number': s.get('number'),
            'km': s.get('km'),
            'coords': (s['latitude'], s['longitude']),
            'value': cur.get('value') if cur else None,
            'time': (cur.get('timestamp') or '')[:16] if cur else None,
        })
    return out


def main():
    write = '--write' in sys.argv
    cx = oc.load('crossings.json')
    with open(os.path.join(oc.CACHE, 'banks.json'), encoding='utf-8') as fh:
        route = [tuple(p) for p in json.load(fh)['primary']]

    print('Pegel von pegelonline holen')
    g = gauges()
    print('  %d Messstellen mit Koordinaten, %d mit aktuellem Wert\n'
          % (len(g), sum(1 for x in g if x['value'] is not None)))

    print('Faehrlinien aus OSM holen')
    raw = bd.query_around_geom(['way["route"="ferry"]'], route, 5.0, 3000, 'ferrylines-geom')
    lines, longs = [], 0
    for e in raw:
        if not e.get('tags', {}).get('name') or not e.get('geometry'):
            continue
        pts = [(g['lat'], g['lon']) for g in e['geometry']]
        ln = oc.length(pts)
        # Eine Querung ist so breit wie der Fluss. Laengere Linien sind
        # Laengsverkehr (HADAG in Hamburg) - ihre Mitte ist keine Querungsstelle.
        if ln > MAX_CROSSING_LINE_KM:
            longs += 1
            continue
        mid = pts[len(pts) // 2]
        e['center'] = {'lat': mid[0], 'lon': mid[1]}
        e['_len'] = ln
        lines.append(e)
    print('  %d Querungslinien, %d Laengslinien verworfen' % (len(lines), longs))

    print('=' * 96)
    print('POSITIONEN')
    print('=' * 96)
    moved = 0
    for c in cx['items']:
        if not c.get('estimate') or c['kind'] not in ('faehre', 'gierfaehre'):
            continue
        m = bd.best_match(c['name'], tuple(c['coords']), lines, 5.0, 0.30)
        if not m:
            continue
        p = bd.pos(m)
        d = oc.hav(tuple(c['coords']), p)
        c['coords'] = [round(p[0], 6), round(p[1], 6)]
        c['estimate'] = False
        moved += 1
        print('  %-40s -> %-30s %5.2f km  (Linie %.2f km breit)'
              % (c['name'][:40], m['tags']['name'][:30], d, m.get('_len', 0)))
    # Herkunft nachtragen, damit im Sheet steht, wie sicher die Position ist.
    for c in cx['items']:
        if c.get('posSource'):
            continue
        if not c.get('estimate'):
            c['posSource'] = 'osm-objekt'
        elif c['kind'] in ('bruecke', 'tunnel', 'radquerung'):
            # Eine Bruecke queert den Fluss - der Punkt auf dem Strom ist die
            # Querungsstelle. Unsicher ist nur, welche Bruecke genau gemeint ist.
            c['posSource'] = 'flusslauf-bruecke'
        else:
            c['posSource'] = 'flusslauf-geschaetzt'

    from collections import Counter
    print()
    print('  %d Faehren zusaetzlich auf echte Querungslinien gesetzt' % moved)
    for k, v in sorted(Counter(c['posSource'] for c in cx['items']).items()):
        print('    %-22s %d' % (k, v))
    unsure = [c['name'] for c in cx['items'] if c['posSource'] == 'flusslauf-geschaetzt']
    if unsure:
        print('  ohne bestaetigte Anlegestelle:')
        for n in unsure:
            print('    - %s' % n)

    print('\n' + '=' * 96)
    print('PEGEL-ZUORDNUNG')
    print('=' * 96)
    ohne = []
    for c in cx['items']:
        near = min(g, key=lambda x: oc.hav(tuple(c['coords']), x['coords']))
        d = oc.hav(tuple(c['coords']), near['coords'])
        if d > MAX_GAUGE_KM:
            # Tschechien: pegelonline fuehrt fuer die Elbe nur Prelouc, und das
            # ohne Koordinaten. Lieber kein Pegel als ein falscher.
            c['gauge'] = None
            ohne.append(c['name'])
            continue
        c['gauge'] = {
            'name': near['name'],
            'elbeKm': near['km'],
            'distKm': round(d, 1),
            'url': 'https://www.pegelonline.wsv.de/gast/pegelinformationen?pegelnr=%s' % near['number'],
        }
    have = [c for c in cx['items'] if c.get('gauge')]
    print('  %d Querungen mit Pegel, %d ohne (zu weit weg)' % (len(have), len(ohne)))
    for c in have[:5]:
        print('    %-40s -> %-16s Elbe-km %-7s (%.1f km entfernt)'
              % (c['name'][:40], c['gauge']['name'], c['gauge']['elbeKm'], c['gauge']['distKm']))
    if ohne:
        print('    ohne Pegel: %s' % ', '.join(n[:24] for n in ohne[:6]))

    print('\n' + '=' * 96)
    print('STATUS')
    print('=' * 96)
    by_id = {c['id']: c for c in cx['items']}
    changed = []
    for cid, (st, hours, note) in STATUS_UPDATE.items():
        c = by_id.get(cid)
        if not c:
            print('  ! unbekannte id %s' % cid)
            continue
        old = c['status']
        c['status'] = st
        c['statusDate'] = STAND
        c['note'] = note
        c['statusSource'] = QUELLE_STATUS
        if hours:
            c['hours'] = hours
        if old != st:
            changed.append((c['name'], old, st))
        print('  %-42s %-12s -> %-12s %s' % (c['name'][:42], old, st,
                                             '' if old == st else '  GEAENDERT'))
    for cid, note in DETOUR_NOTE.items():
        c = by_id.get(cid)
        if c:
            c['detourNote'] = note
    print('\n  %d Statuswechsel: %s' % (len(changed),
          ', '.join('%s %s->%s' % t for t in changed) or 'keiner'))

    cx['meta']['statusDate'] = STAND
    cx['meta']['statusSource'] = QUELLE_STATUS
    cx['meta']['gaugeNote'] = ('Jeder Querung ist der naechstgelegene Elbe-Pegel zugeordnet. '
                               'Der Link zeigt den aktuellen Wasserstand bei pegelonline.wsv.de.')

    if not write:
        print('\nNichts geschrieben. Mit --write uebernehmen.')
        return
    src = os.path.join(oc.ROOT, 'crossings.json')
    shutil.copyfile(src, src + '.bak')
    oc.save('crossings.json', cx)
    print('\nGeschrieben: crossings.json (Backup als .bak)')


if __name__ == '__main__':
    main()

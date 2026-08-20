"""Schritt 1: Elberadweg-Geometrie aus OSM holen und route.geojson bauen.

Quellen (per Testabfrage verifiziert):
  rel 123822 Elbe (waterway)                -> Referenzachse Quelle -> Muendung
  rel 181093 Labska stezka (CZ)             -> Quelle .. Hrensko
  rel  22327 [D10] Elberadweg rechtselbisch -> Grenze .. Cuxhaven
  rel  22328 [D10] Elberadweg linkselbisch  -> Grenze .. Cuxhaven

Warum die Referenzachse: OSM-Routenrelationen zerfallen in Fragmente (gemessene
Luecken 7 m bis 20 km). Greedy-Verkettung laeuft an den grossen Luecken in die
falsche Richtung. Der Flusslauf gibt die Reihenfolge eindeutig vor.

Aufruf:  python tools/build_route.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osm_common as oc  # noqa: E402

QUELLE = (50.7757, 15.5355)      # Pramen Labe, Startpunkt der Referenzachse
HAMBURG = (53.5413, 9.9842)      # Elbphilharmonie - hier endet die Tour
RDP_EPS_KM = 0.015               # ~15 m: formtreu, aber deutlich weniger Punkte
MAX_POINTS = 4000


def river_axis():
    """Elbe-Mittellinie als Referenz, von der Quelle abwaerts."""
    d = oc.overpass('[out:json][timeout:300];\nrel(123822);\nway(r);\nout geom;\n',
                    'elbe-river')
    main = [w for w in d['elements']
            if w['type'] == 'way' and w.get('tags', {}).get('waterway') == 'river']
    line = oc.chain(oc.stitch(main), max_gap_km=15, min_piece_km=0.5)
    if oc.hav(line[0], QUELLE) > oc.hav(line[-1], QUELLE):
        line = line[::-1]
    line = oc.rdp(line, 0.05)
    return line, oc.cumulative(line)


def route_line(rel_id, mode, tag, river, cum):
    if mode == 'super':
        q = ('[out:json][timeout:300];\nrel(%d)->.m;\nrel(r.m)->.s;\n'
             'way(r.s);\nout geom;\n' % rel_id)
    else:
        q = '[out:json][timeout:300];\nrel(%d);\nway(r);\nout geom;\n' % rel_id
    ways = [e for e in oc.overpass(q, tag)['elements'] if e['type'] == 'way']
    frags = oc.stitch(ways)
    line = oc.assemble(frags, river, cum)
    print('  %-14s %5d Ways, %2d Fragmente -> %7.1f km, %6d Punkte'
          % (tag, len(ways), len(frags), oc.length(line), len(line)))
    return line


def cut_at(line, target):
    """Linie am Punkt beenden, der target am naechsten liegt."""
    best_i, best_d = 0, float('inf')
    for i, p in enumerate(line):
        d = oc.hav(p, target)
        if d < best_d:
            best_i, best_d = i, d
    return line[:best_i + 1], best_d


def simplify(line):
    out, eps = oc.simplify_to(line, MAX_POINTS, RDP_EPS_KM)
    print('          Vereinfachung mit %.0f m Toleranz' % (eps * 1000))
    return out


def main():
    print('Referenzachse Elbe holen')
    river, rcum = river_axis()
    print('  Fluss: %.1f km, %d Punkte, Start (%.4f,%.4f)\n'
          % (rcum[-1], len(river), river[0][0], river[0][1]))

    print('Radrouten holen und entlang des Flusses ordnen')
    cz = route_line(181093, 'flat', 'labska-stezka', river, rcum)
    right = route_line(22327, 'super', 'd10-rechts', river, rcum)
    left = route_line(22328, 'super', 'd10-links', river, rcum)

    # Primaerachse: Labska stezka (Quelle .. Grenze) + rechtes Ufer (Grenze .. Hamburg)
    grenz_gap = oc.hav(cz[-1], right[0])
    right_cut, d_hh = cut_at(right, HAMBURG)
    primary = cz + right_cut
    left_cut, d_hh_l = cut_at(left, HAMBURG)

    print('\n  Grenzuebergang Hrensko/Schoena: %.2f km Luecke (Uferwechsel per Faehre)'
          % grenz_gap)
    print('  Beschnitt in Hamburg: Primaerachse %.0f m, linkes Ufer %.0f m vom Ziel entfernt'
          % (d_hh * 1000, d_hh_l * 1000))

    banks = {}
    for name, line in (('primary', primary), ('links', left_cut)):
        before = oc.length(line)
        line = oc.fill_gaps(line, river, rcum)
        print('  %-8s Luecken entlang des Flusses gefuellt: %.1f -> %.1f km'
              % (name, before, oc.length(line)))
        s = simplify(line)
        banks[name] = s
        print('  %-8s %7.1f km -> %5d Punkte (%.0f%% gespart)'
              % (name, oc.length(s), len(s), 100.0 * (1 - len(s) / float(len(line)))))

    print('\n  Gesamt Primaerachse Quelle -> Hamburg: %.1f km' % oc.length(banks['primary']))
    print('  (tour-kontext.md: Elberadweg Quelle-Cuxhaven 1270-1280 km, davon HH-Cuxhaven ~130')
    print('   -> erwartet ~1140-1150 km)')

    with open(os.path.join(oc.CACHE, 'banks.json'), 'w', encoding='utf-8') as fh:
        json.dump(banks, fh)

    features = []
    for name, label in (('primary', 'Elberadweg Primaerachse (Labska stezka + rechtselbisch)'),
                        ('links', 'Elberadweg linkselbisch')):
        features.append({
            'type': 'Feature',
            'properties': {'bank': name, 'name': label,
                           'km': round(oc.length(banks[name]), 1),
                           'source': 'OpenStreetMap contributors, ODbL'},
            'geometry': {'type': 'LineString',
                         'coordinates': [[round(p[1], 6), round(p[0], 6)]
                                         for p in banks[name]]},
        })
    path = oc.save('route.geojson', {'type': 'FeatureCollection', 'features': features})
    print('  geschrieben: route.geojson (%.0f KB)' % (os.path.getsize(path) / 1024.0))


if __name__ == '__main__':
    main()

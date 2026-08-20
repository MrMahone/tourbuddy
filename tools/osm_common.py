"""Gemeinsame Helfer fuer die OSM-Datenpipeline der Elbe-Tour.

Reines Python 3, keine Fremdpakete. Overpass-Antworten werden unter tools/.cache/
abgelegt, damit wiederholte Laeufe keine Quota ziehen.
"""
import hashlib
import json
import math
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(HERE, '.cache')

# Reihenfolge = Vorliebe. Die Haupt-Instanz drosselt haeufig (429),
# der mail.ru-Mirror antwortete im Test stabil.
ENDPOINTS = [
    'https://maps.mail.ru/osm/tools/overpass/api/interpreter',
    'https://overpass-api.de/api/interpreter',
]

R_EARTH = 6371.0088


def overpass(query, tag, force=False):
    """Overpass-Abfrage mit Plattencache. tag = sprechender Dateiname."""
    key = hashlib.sha1(query.encode('utf-8')).hexdigest()[:12]
    path = os.path.join(CACHE, '%s-%s.json' % (tag, key))
    if os.path.exists(path) and not force:
        with open(path, encoding='utf-8') as fh:
            return json.load(fh)

    last = None
    for attempt in range(6):
        host = ENDPOINTS[attempt % len(ENDPOINTS)]
        req = urllib.request.Request(
            host, data=query.encode('utf-8'),
            headers={'Content-Type': 'text/plain; charset=utf-8',
                     'User-Agent': 'elbe-tour-databuild/1.0 (persoenliche Tourplanung)'})
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                raw = resp.read().decode('utf-8')
            data = json.loads(raw)
            if 'elements' not in data:
                raise ValueError('keine elements im Ergebnis')
            os.makedirs(CACHE, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as fh:
                json.dump(data, fh)
            print('    [overpass] %-16s %6d Elemente  via %s'
                  % (tag, len(data['elements']), host.split('/')[2]))
            return data
        except Exception as exc:
            last = exc
            wait = 5 * (attempt + 1)
            print('    [overpass] %s fehlgeschlagen (%s) - neuer Versuch in %ds'
                  % (host.split('/')[2], str(exc)[:60], wait))
            time.sleep(wait)
    raise RuntimeError('Overpass nicht erreichbar: %s' % last)


def hav(a, b):
    """Grosskreisdistanz in km. Punkte als (lat, lon)."""
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * R_EARTH * math.asin(math.sqrt(h))


def length(line):
    return sum(hav(line[i - 1], line[i]) for i in range(1, len(line)))


def stitch(ways):
    """Wege ueber gemeinsame Endpunkte zu moeglichst langen Linien verketten.

    Gibt eine nach Laenge absteigend sortierte Liste von Punktlisten zurueck.
    """
    segs = []
    for w in ways:
        g = [(p['lat'], p['lon']) for p in w.get('geometry') or []]
        if len(g) >= 2:
            segs.append(g)

    def key(p):
        return (round(p[0], 7), round(p[1], 7))

    ends = {}
    for i, s in enumerate(segs):
        ends.setdefault(key(s[0]), []).append(i)
        ends.setdefault(key(s[-1]), []).append(i)

    used = [False] * len(segs)
    # Zuerst an freien Enden starten, damit Pfade nicht in der Mitte beginnen.
    starts = [i for i, s in enumerate(segs)
              if len(ends[key(s[0])]) == 1 or len(ends[key(s[-1])]) == 1]
    order = starts + [i for i in range(len(segs)) if i not in set(starts)]

    lines = []
    for start in order:
        if used[start]:
            continue
        used[start] = True
        line = list(segs[start])
        grew = True
        while grew:
            grew = False
            for at_end in (True, False):
                node = key(line[-1] if at_end else line[0])
                for j in ends.get(node, []):
                    if used[j]:
                        continue
                    nxt = list(segs[j])
                    if at_end:
                        if key(nxt[0]) != node:
                            nxt.reverse()
                        line.extend(nxt[1:])
                    else:
                        if key(nxt[-1]) != node:
                            nxt.reverse()
                        line = nxt[:-1] + line
                    used[j] = True
                    grew = True
                    break
                if grew:
                    break
        lines.append(line)
    lines.sort(key=length, reverse=True)
    return lines


def _xy(p, lat0):
    """Lokale Ebene in km - fuer Punkt-Linie-Abstaende voellig ausreichend."""
    k = math.cos(math.radians(lat0))
    return (math.radians(p[1]) * R_EARTH * k, math.radians(p[0]) * R_EARTH)


def perp_km(p, a, b):
    lat0 = a[0]
    px, py = _xy(p, lat0)
    ax, ay = _xy(a, lat0)
    bx, by = _xy(b, lat0)
    dx, dy = bx - ax, by - ay
    den = dx * dx + dy * dy
    if den == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / den))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def rdp(pts, eps_km):
    """Douglas-Peucker, iterativ (Rekursion reicht bei 20k Punkten nicht)."""
    if len(pts) < 3:
        return list(pts)
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1:
            continue
        worst, wi = -1.0, -1
        for i in range(a + 1, b):
            d = perp_km(pts[i], pts[a], pts[b])
            if d > worst:
                worst, wi = d, i
        if worst > eps_km:
            keep[wi] = True
            stack.append((a, wi))
            stack.append((wi, b))
    return [p for p, k in zip(pts, keep) if k]


def cumulative(line):
    cum = [0.0]
    for i in range(1, len(line)):
        cum.append(cum[-1] + hav(line[i - 1], line[i]))
    return cum


def project(point, line, cum):
    """Punkt auf Polylinie projizieren.

    Rueckgabe: (km entlang der Linie, Abstand in km, Segmentindex).
    """
    best = (0.0, float('inf'), 0)
    for i in range(1, len(line)):
        a, b = line[i - 1], line[i]
        lat0 = a[0]
        px, py = _xy(point, lat0)
        ax, ay = _xy(a, lat0)
        bx, by = _xy(b, lat0)
        dx, dy = bx - ax, by - ay
        den = dx * dx + dy * dy
        t = 0.0 if den == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / den))
        d = math.hypot(px - (ax + t * dx), py - (ay + t * dy))
        if d < best[1]:
            seg = cum[i] - cum[i - 1]
            best = (cum[i - 1] + t * seg, d, i - 1)
    return best


def load(name):
    with open(os.path.join(ROOT, name), encoding='utf-8') as fh:
        return json.load(fh)


def save(name, data):
    path = os.path.join(ROOT, name)
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write('\n')
    return path


_UML = (('ä', 'a'), ('ö', 'o'), ('ü', 'u'), ('ß', 'ss'),
        ('á', 'a'), ('í', 'i'), ('é', 'e'), ('ě', 'e'),
        ('ř', 'r'), ('š', 's'), ('č', 'c'), ('ž', 'z'),
        ('ů', 'u'), ('ý', 'y'), ('è', 'e'), ('ó', 'o'))

# Gattungswoerter, die beim Namensvergleich nichts unterscheiden.
_STOP = {
    'faehre', 'fahre', 'ferry', 'gierfaehre', 'motorfaehre', 'elbfaehre',
    'faehrstelle', 'faehranleger', 'personenfaehre', 'radfaehre', 'faehrstation',
    'bruecke', 'brucke', 'elbbruecke', 'strassenbruecke', 'stadtbruecke',
    'campingplatz', 'camping', 'campingpark', 'zeltplatz', 'wohnmobilstellplatz',
    'der', 'die', 'das', 'und', 'zum', 'zur', 'the', 'bei', 'auf',
}


def tokens(s):
    """Namen in vergleichbare Wort-Menge zerlegen."""
    s = (s or '').lower()
    for a, b in _UML:
        s = s.replace(a, b)
    out = set()
    for tok in ''.join(ch if ch.isalnum() else ' ' for ch in s).split():
        if len(tok) > 2 and tok not in _STOP:
            out.add(tok)
    return out


def name_score(a, b):
    """Jaccard-Aehnlichkeit zweier Namen, 0..1."""
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / float(len(ta | tb))


def chain(lines, max_gap_km=1.5, min_piece_km=0.3):
    """Teilstuecke ueber kleine Luecken zu einer langen Linie verketten.

    OSM-Routenrelationen zerfallen oft in Fragmente, weil aufeinanderfolgende
    Abschnitte nicht exakt denselben Knoten teilen (im Test: Luecken von 7-50 m).
    Greedy: vom laengsten Stueck aus immer das naechstgelegene Fragment anhaengen.
    """
    pieces = [list(l) for l in lines if length(l) >= min_piece_km]
    if not pieces:
        return []
    pieces.sort(key=length, reverse=True)
    chainl = pieces.pop(0)
    while pieces:
        best = None
        for idx, p in enumerate(pieces):
            for my_end in (True, False):
                anchor = chainl[-1] if my_end else chainl[0]
                for rev in (False, True):
                    cand = p[::-1] if rev else p
                    d = hav(anchor, cand[0] if my_end else cand[-1])
                    if best is None or d < best[0]:
                        best = (d, idx, my_end, rev)
        if best is None or best[0] > max_gap_km:
            break
        d, idx, my_end, rev = best
        p = pieces.pop(idx)
        cand = p[::-1] if rev else p
        if my_end:
            chainl.extend(cand)
        else:
            chainl = cand + chainl
    return chainl


MAX_OFF_RIVER_KM = 8.0      # weiter weg = anderer Fluss (Moldau/Prag), nicht unsere Tour


def assemble(frags, ref, ref_cum, min_piece_km=1.0, max_off_river_km=MAX_OFF_RIVER_KM):
    """Fragmente entlang einer Referenzachse ordnen und aneinanderhaengen.

    Robuster als greedy chain(): bei echten Luecken in der OSM-Relation (die
    Labska stezka hat eine ~20 km Luecke) laeuft greedy in die falsche Richtung.
    Die Referenzachse (Flusslauf) gibt die Reihenfolge eindeutig vor.

    ref laeuft von Quelle zur Muendung, daher steigt ref_km flussabwaerts.
    Ergebnis laeuft von der Quelle Richtung Muendung.
    """
    items = []
    dropped = 0
    for f in frags:
        if length(f) < min_piece_km:
            continue
        # Fragmente weit vom Referenzfluss gehoeren zu einem anderen Gewaesser.
        # Die Labska stezka fuehrt offiziell ueber Prag an der Moldau - dieser
        # Abstecher ist in der Tourplanung ausdruecklich ausgelassen.
        probe = [f[i] for i in range(0, len(f), max(1, len(f) // 9))]
        off = sorted(project(p, ref, ref_cum)[1] for p in probe)
        # Der weiteste Punkt entscheidet, nicht der Median: der Moldau-Abstecher
        # laeuft anfangs noch elbnah und entfernt sich dann (gemessen: bis 15.7 km,
        # alle anderen Fragmente bleiben unter 2.6 km).
        if off[-1] > max_off_river_km:
            dropped += 1
            continue
        k0 = project(f[0], ref, ref_cum)[0]
        k1 = project(f[-1], ref, ref_cum)[0]
        line = f if k0 <= k1 else f[::-1]
        items.append((min(k0, k1), max(k0, k1), line))
    if dropped:
        print('      %d Fragmente verworfen (weiter als %.0f km vom Referenzfluss)'
              % (dropped, max_off_river_km))
    items.sort(key=lambda x: x[0])

    out = []
    last_end = -1e9
    for k0, k1, line in items:
        # Fragmente, die vollstaendig in einem bereits verbauten Bereich liegen,
        # sind Parallelvarianten (Alternativrouten) - die wuerden Zickzack erzeugen.
        if k1 <= last_end + 0.2:
            continue
        out.extend(line)
        last_end = max(last_end, k1)
    return out


QUELLE = (50.7757, 15.5355)     # Pramen Labe


def river_axis():
    """Elbe-Mittellinie als Referenzachse, von der Quelle abwaerts.

    Nutzt den Overpass-Cache, laeuft also nach dem ersten Lauf ohne Netz.
    """
    q = ('[out:json][timeout:300];'
         'rel(123822);'
         'way(r);'
         'out geom;')
    d = overpass(q, 'elbe-river')
    main = [w for w in d['elements']
            if w['type'] == 'way' and w.get('tags', {}).get('waterway') == 'river']
    line = chain(stitch(main), max_gap_km=15, min_piece_km=0.5)
    if hav(line[0], QUELLE) > hav(line[-1], QUELLE):
        line = line[::-1]
    line = rdp(line, 0.05)
    return line, cumulative(line)


def snap_to(point, line):
    """Naechsten Punkt auf einer Polylinie zurueckgeben (lat, lon, Abstand km)."""
    best = None
    for i in range(1, len(line)):
        a, b = line[i - 1], line[i]
        lat0 = a[0]
        px, py = _xy(point, lat0)
        ax, ay = _xy(a, lat0)
        bx, by = _xy(b, lat0)
        dx, dy = bx - ax, by - ay
        den = dx * dx + dy * dy
        t = 0.0 if den == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / den))
        d = math.hypot(px - (ax + t * dx), py - (ay + t * dy))
        if best is None or d < best[2]:
            lat = a[0] + t * (b[0] - a[0])
            lon = a[1] + t * (b[1] - a[1])
            best = (lat, lon, d)
    return best


def simplify_to(line, max_points, eps_start=0.010):
    """Vereinfachen bis die Punktzahl passt - ueber die RDP-Toleranz, nicht durch
    Ausduennen. Gleichmaessiges Wegwerfen jedes n-ten Punktes zerstoert die
    Formtreue und erzeugt lange Sehnen in Kurven.
    """
    eps = eps_start
    out = rdp(line, eps)
    while len(out) > max_points and eps < 1.0:
        eps *= 1.6
        out = rdp(line, eps)
    return out, eps


def fill_gaps(line, ref, ref_cum, min_gap_km=0.6):
    """Echte Luecken entlang der Referenzachse (Fluss) ueberbruecken.

    Ohne das entsteht z. B. bei der ~18 km Luecke der Labska stezka eine
    Luftlinie quer durch die Landschaft. Der Fluss ist dort die ehrlichere
    Naeherung, denn die Route folgt ihm.
    """
    if len(line) < 2:
        return line
    out = [line[0]]
    inserted = 0.0
    for i in range(1, len(line)):
        d = hav(line[i - 1], line[i])
        if d >= min_gap_km:
            k0 = project(line[i - 1], ref, ref_cum)[0]
            k1 = project(line[i], ref, ref_cum)[0]
            lo, hi = min(k0, k1), max(k0, k1)
            mid = [p for p, k in zip(ref, ref_cum) if lo < k < hi]
            if k1 < k0:
                mid.reverse()
            if mid:
                out.extend(mid)
                inserted += d
        out.append(line[i])
    return out

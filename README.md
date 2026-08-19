<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <link rel="stylesheet" href="_ds/modernist-68a4e577-3c9a-444c-bc81-b0a1815ea155/styles.css">
  <script src="_ds/modernist-68a4e577-3c9a-444c-bc81-b0a1815ea155/_ds_bundle.js"></script>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    html,body{margin:0;padding:0;height:100%;overscroll-behavior:none}
    a{color:var(--color-accent-700,#a2210d)} a:hover{color:var(--color-accent,#ec3013)}
    .elbe{--sf:#f3f2f2;--sf2:#e9e7e2;--ink:#201e1d;--mut:#6d6a66;--ln:#201e1d;--lnsoft:#cfccc7}
    .elbe[data-dark="1"]{--sf:#211f1e;--sf2:#2b2927;--ink:#eceae6;--mut:#9b9792;--ln:#eceae6;--lnsoft:#454340}
    .elbe[data-dark="1"] .leaflet-tile{filter:invert(1) hue-rotate(190deg) saturate(.3) brightness(.92) contrast(.92)}
    .elbe[data-dark="1"] .leaflet-container{background:#1a1918}
    .leaflet-container{font-family:var(--font-body,'Archivo',sans-serif)}
    .leaflet-control-attribution{font-size:9px;background:rgba(243,242,242,.7)}
    .elbe[data-dark="1"] .leaflet-control-attribution{background:rgba(33,31,30,.7);color:#9b9792}
    .pos-halo{position:absolute;inset:-5px;border:2px solid #ec3013;border-radius:50%;animation:posPulse 2.2s ease-out infinite}
    @keyframes posPulse{0%{transform:scale(.55);opacity:.9}100%{transform:scale(1.6);opacity:0}}
    @media (prefers-reduced-motion:reduce){*{transition-duration:.01ms!important;animation:none!important}}
  </style>
</helmet>
<div class="elbe" data-dark="{{ darkAttr }}" style="position:relative;width:100%;height:100dvh;overflow:hidden;background:#dfe3e0;font-family:var(--font-body,'Archivo',sans-serif);color:var(--ink)">
  <div ref="{{ mapRef }}" style="position:absolute;inset:0;z-index:0"></div>

  <div style="position:absolute;top:12px;left:12px;z-index:500;background:var(--sf);color:var(--ink);border:2px solid var(--ln);padding:10px 14px 9px;box-shadow:var(--shadow-sm,0 1px 4px rgba(0,0,0,.15))">
    <div style="display:flex;align-items:center;gap:8px;font-size:12px;font-weight:800;letter-spacing:.12em;line-height:1"><span style="width:9px;height:9px;background:var(--color-accent,#ec3013)"></span>ELBE-TOUR</div>
    <div style="margin-top:5px;font-size:9px;font-weight:600;letter-spacing:.1em;line-height:1;color:var(--mut);font-variant-numeric:tabular-nums">QUELLE → HAMBURG · 1021 KM</div>
  </div>

  <div style="position:absolute;right:12px;bottom:28px;z-index:500;display:flex;flex-direction:column;align-items:flex-end;gap:8px">
    <button onClick="{{ locate }}" aria-label="Meine Position" style="width:52px;height:52px;background:var(--sf);border:2px solid var(--ln);display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:var(--shadow-sm,0 1px 4px rgba(0,0,0,.15))" style-hover="background:var(--sf2)" style-focus="outline:2px solid #ec3013;outline-offset:2px">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--ink)"><circle cx="12" cy="12" r="7"></circle><circle cx="12" cy="12" r="1.5" fill="currentColor"></circle><path d="M12 2v3M12 19v3M2 12h3M19 12h3"></path></svg>
    </button>
    <sc-if value="{{ panelOpen }}" hint-placeholder-val="{{ false }}">
      <div style="width:232px;background:var(--sf);border:2px solid var(--ln);box-shadow:var(--shadow-md,0 4px 12px rgba(0,0,0,.18))">
        <div style="display:flex;align-items:center;gap:8px;padding:10px 12px 9px;font-size:10px;font-weight:700;letter-spacing:.12em;color:var(--mut);border-bottom:2px solid var(--ln)"><span style="width:8px;height:8px;background:var(--color-accent,#ec3013)"></span>EBENEN</div>
        <button onClick="{{ setModeStd }}" style="display:flex;align-items:center;gap:10px;width:100%;min-height:48px;padding:0 12px;background:none;border:none;border-bottom:1px solid var(--lnsoft);font:600 14px var(--font-body);color:var(--ink);text-align:left;cursor:pointer" style-hover="background:var(--sf2)" style-focus="outline:2px solid #ec3013;outline-offset:-2px">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex:none;color:var(--mut)"><path d="M9 3 3.6 5.4a1 1 0 0 0-.6.92V20l6-2.5 6 2.5 5.4-2.4a1 1 0 0 0 .6-.92V4l-6 2.5L9 4Z"></path><path d="M9 3v14M15 6.5v14"></path></svg>
          <span style="flex:1">Standard</span><span style="flex:none;width:12px;height:12px;border:2px solid var(--ln);background:{{ stdFill }}"></span>
        </button>
        <button onClick="{{ setModeCx }}" style="display:flex;align-items:center;gap:10px;width:100%;min-height:48px;padding:0 12px;background:none;border:none;border-bottom:1px solid var(--lnsoft);font:600 14px var(--font-body);color:var(--ink);text-align:left;cursor:pointer" style-hover="background:var(--sf2)" style-focus="outline:2px solid #ec3013;outline-offset:-2px">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex:none;color:var(--mut)"><rect x="6.5" y="6.5" width="11" height="11" transform="rotate(45 12 12)"></rect></svg>
          <span style="flex:1">Querungen hervorheben</span><span style="flex:none;width:12px;height:12px;border:2px solid var(--ln);background:{{ cxFill }}"></span>
        </button>
        <button onClick="{{ setModeSl }}" style="display:flex;align-items:center;gap:10px;width:100%;min-height:48px;padding:0 12px;background:none;border:none;border-bottom:2px solid var(--ln);font:600 14px var(--font-body);color:var(--ink);text-align:left;cursor:pointer" style-hover="background:var(--sf2)" style-focus="outline:2px solid #ec3013;outline-offset:-2px">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" style="flex:none;color:var(--mut)"><path d="M3 10.5 12 3l9 7.5"></path><path d="M5 9v11h14V9"></path></svg>
          <span style="flex:1">Schlafplätze hervorheben</span><span style="flex:none;width:12px;height:12px;border:2px solid var(--ln);background:{{ slFill }}"></span>
        </button>
        <button onClick="{{ toggDark }}" style="display:flex;align-items:center;gap:10px;width:100%;min-height:48px;padding:0 12px;background:none;border:none;font:600 14px var(--font-body);color:var(--ink);text-align:left;cursor:pointer" style-hover="background:var(--sf2)" style-focus="outline:2px solid #ec3013;outline-offset:-2px">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex:none;color:var(--mut)"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"></path></svg>
          <span style="flex:1">Dark Mode</span><span style="flex:none;width:12px;height:12px;border:2px solid var(--ln);background:{{ darkFill }}"></span>
        </button>
      </div>
    </sc-if>
    <button onClick="{{ toggPanel }}" aria-label="Ebenen" style="width:52px;height:52px;background:var(--sf);border:2px solid var(--ln);display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:var(--shadow-sm,0 1px 4px rgba(0,0,0,.15))" style-hover="background:var(--sf2)" style-focus="outline:2px solid #ec3013;outline-offset:2px">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" style="color:var(--ink)"><path d="M12 2 2 7l10 5 10-5-10-5Z"></path><path d="m2 12 10 5 10-5"></path><path d="m2 17 10 5 10-5"></path></svg>
    </button>
  </div>

  <sc-if value="{{ hasSel }}" hint-placeholder-val="{{ false }}">
    <div style="position:absolute;left:0;right:0;bottom:0;height:72%;z-index:600;background:var(--sf);color:var(--ink);border-top:2px solid var(--ln);box-shadow:0 -8px 28px rgba(0,0,0,.2);display:flex;flex-direction:column;transform:{{ sheetTf }};transition:{{ sheetTrans }}">
      <div onPointerDown="{{ handleDown }}" style="flex:none;position:relative;cursor:grab;touch-action:none;padding:0 20px 10px">
        <div style="display:flex;justify-content:center;padding:8px 0 10px"><span style="width:36px;height:4px;background:var(--lnsoft)"></span></div>
        <button onClick="{{ close }}" aria-label="Schließen" style="position:absolute;top:10px;right:8px;width:44px;height:44px;background:none;border:none;display:flex;align-items:center;justify-content:center;cursor:pointer;color:var(--ink)" style-focus="outline:2px solid #ec3013;outline-offset:-2px">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6 6 18M6 6l12 12"></path></svg>
        </button>
        <div style="display:flex;align-items:center;gap:8px;font-size:10px;font-weight:700;letter-spacing:.12em;color:var(--mut)"><span style="width:8px;height:8px;background:var(--color-accent,#ec3013)"></span>{{ sel.kicker }}</div>
        <h2 style="margin:6px 44px 0 0;font-size:28px;font-weight:800;line-height:1.02;letter-spacing:-.015em">{{ sel.name }}</h2>
        <sc-if value="{{ sel.status }}" hint-placeholder-val="{{ false }}">
          <div style="display:flex;align-items:center;gap:10px;margin-top:10px;flex-wrap:wrap">
            <span style="display:inline-block;padding:5px 8px 4px;font-size:11px;font-weight:800;letter-spacing:.06em;background:{{ sel.badgeBg }};color:{{ sel.badgeFg }};border:2px solid {{ sel.badgeBd }}">{{ sel.statusLabel }}</span>
            <span style="font-size:12px;color:var(--mut);font-variant-numeric:tabular-nums">Stand: {{ sel.statusDateFmt }}</span>
          </div>
        </sc-if>
        <sc-if value="{{ sel.critical }}" hint-placeholder-val="{{ false }}">
          <div style="margin-top:8px;font-size:11px;font-weight:700;letter-spacing:.06em;color:var(--color-accent-700,#a2210d)">▲ EINZIGE QUERUNG IN DIESEM ABSCHNITT</div>
        </sc-if>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;margin-top:12px;border-top:2px solid var(--ln)">
          <div style="padding:8px 8px 2px 0;border-right:1px solid var(--lnsoft)">
            <div style="font-size:9px;font-weight:700;letter-spacing:.1em;color:var(--mut)">KM AB QUELLE</div>
            <div style="margin-top:2px;font-size:19px;font-weight:800;font-variant-numeric:tabular-nums;line-height:1">{{ sel.km }}</div>
          </div>
          <div style="padding:8px 8px 2px 12px;border-right:1px solid var(--lnsoft)">
            <div style="font-size:9px;font-weight:700;letter-spacing:.1em;color:var(--mut)">UMWEG</div>
            <div style="margin-top:2px;font-size:19px;font-weight:800;font-variant-numeric:tabular-nums;line-height:1">{{ sel.detourStr }}</div>
          </div>
          <div style="padding:8px 0 2px 12px">
            <div style="font-size:9px;font-weight:700;letter-spacing:.1em;color:var(--mut)">NOCH BIS HH</div>
            <div style="margin-top:2px;font-size:19px;font-weight:800;font-variant-numeric:tabular-nums;line-height:1">{{ sel.remainStr }}</div>
          </div>
        </div>
      </div>
      <sc-if value="{{ showLeiste }}" hint-placeholder-val="{{ false }}">
        <div style="flex:none;padding:10px 20px 12px;border-top:2px solid var(--ln)">
          <div style="display:flex;justify-content:space-between;font-size:9px;font-weight:700;letter-spacing:.1em;color:var(--mut)"><span>QUELLE</span><span>HAMBURG</span></div>
          <div style="position:relative;height:18px;margin-top:5px">
            <div style="position:absolute;left:0;right:0;top:8px;height:2px;background:var(--lnsoft)"></div>
            <sc-for list="{{ ticks }}" as="t" hint-placeholder-count="4">
              <div style="position:absolute;top:5px;left:{{ t.pct }};width:1px;height:8px;background:var(--mut)"></div>
            </sc-for>
            <div style="position:absolute;left:0;top:8px;height:2px;background:var(--ink);width:{{ sel.pct }}"></div>
            <div style="position:absolute;top:3px;left:{{ sel.pct }};width:12px;height:12px;margin-left:-6px;background:var(--color-accent,#ec3013);border:2px solid var(--sf)"></div>
          </div>
          <div style="margin-top:2px;font-size:12px;font-weight:700;font-variant-numeric:tabular-nums">km {{ sel.km }} <span style="color:var(--mut);font-weight:500">von 1021</span></div>
        </div>
      </sc-if>
      <div style="flex:1;min-height:0;overflow-y:{{ contentOv }};padding:0 20px 24px;border-top:1px solid var(--lnsoft)">
        <sc-if value="{{ isWp }}" hint-placeholder-val="{{ true }}">
          <sc-for list="{{ sel.notes }}" as="n" hint-placeholder-count="2">
            <div style="display:flex;gap:10px;padding:11px 0;border-bottom:1px solid var(--lnsoft);font-size:14px;line-height:1.45"><span style="flex:none;width:6px;height:6px;background:var(--ink);margin-top:6px"></span><span>{{ n }}</span></div>
          </sc-for>
          <sc-if value="{{ hasSleep }}" hint-placeholder-val="{{ false }}">
            <div style="margin-top:18px;padding-bottom:8px;border-bottom:2px solid var(--ln);font-size:10px;font-weight:700;letter-spacing:.1em;color:var(--mut)">SCHLAFEN</div>
            <sc-for list="{{ sel.sleepList }}" as="s" hint-placeholder-count="1">
              <div style="padding:12px 0;border-bottom:1px solid var(--lnsoft)">
                <div style="display:flex;justify-content:space-between;gap:8px;align-items:baseline">
                  <span style="font-size:15px;font-weight:700">{{ s.name }}</span>
                  <span style="flex:none;font-size:11px;font-weight:600;letter-spacing:.06em;color:var(--mut)">{{ s.typeLabel }}</span>
                </div>
                <div style="margin-top:2px;font-size:12px;color:var(--mut);font-variant-numeric:tabular-nums">Umweg {{ s.detourStr }}</div>
                <a href="{{ s.telHref }}" style="display:flex;align-items:center;gap:10px;min-height:48px;margin-top:8px;border:2px solid var(--ln);padding:0 14px;text-decoration:none;color:var(--ink);font-size:15px;font-weight:700;font-variant-numeric:tabular-nums" style-hover="background:var(--sf2)" style-focus="outline:2px solid #ec3013;outline-offset:2px">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ec3013" stroke-width="2.2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                  <span>{{ s.phone }}</span>
                </a>
              </div>
            </sc-for>
          </sc-if>
        </sc-if>
        <sc-if value="{{ isSl }}" hint-placeholder-val="{{ false }}">
          <div style="display:flex;justify-content:space-between;gap:12px;padding:11px 0;border-bottom:1px solid var(--lnsoft);font-size:14px"><span style="color:var(--mut)">Bei</span><span style="font-weight:600;text-align:right">{{ sel.parent }}</span></div>
          <sc-if value="{{ sel.note }}" hint-placeholder-val="{{ false }}">
            <div style="padding:11px 0;border-bottom:1px solid var(--lnsoft);font-size:14px;line-height:1.45">{{ sel.note }}</div>
          </sc-if>
          <a href="{{ sel.telHref }}" style="display:flex;align-items:center;gap:10px;min-height:52px;margin-top:14px;border:2px solid var(--ln);padding:0 14px;text-decoration:none;color:var(--ink);font-size:16px;font-weight:700;font-variant-numeric:tabular-nums" style-hover="background:var(--sf2)" style-focus="outline:2px solid #ec3013;outline-offset:2px">
            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="#ec3013" stroke-width="2.2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
            <span>{{ sel.phone }}</span>
          </a>
        </sc-if>
        <sc-if value="{{ isCx }}" hint-placeholder-val="{{ false }}">
          <div style="display:flex;justify-content:space-between;gap:12px;padding:11px 0;border-bottom:1px solid var(--lnsoft);font-size:14px"><span style="color:var(--mut)">Betrieb</span><span style="font-weight:600;text-align:right;font-variant-numeric:tabular-nums">{{ sel.hours }}</span></div>
          <sc-if value="{{ sel.backup }}" hint-placeholder-val="{{ false }}">
            <div style="display:flex;justify-content:space-between;gap:12px;padding:11px 0;border-bottom:1px solid var(--lnsoft);font-size:14px"><span style="color:var(--mut)">Ersatz</span><span style="font-weight:600;text-align:right">{{ sel.backup }}</span></div>
          </sc-if>
          <sc-if value="{{ sel.note }}" hint-placeholder-val="{{ false }}">
            <div style="padding:11px 0;border-bottom:1px solid var(--lnsoft);font-size:14px;line-height:1.45">{{ sel.note }}</div>
          </sc-if>
          <sc-if value="{{ sel.pegel }}" hint-placeholder-val="{{ false }}">
            <a href="https://www.pegelonline.wsv.de" target="_blank" style="display:flex;align-items:center;justify-content:space-between;min-height:48px;margin-top:14px;border:2px solid var(--ln);padding:0 14px;text-decoration:none;color:var(--ink);font-size:15px;font-weight:700" style-hover="background:var(--sf2)" style-focus="outline:2px solid #ec3013;outline-offset:2px">
              <span>Pegelstand prüfen</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ec3013" stroke-width="2.5"><path d="M7 17 17 7M8 7h9v9"></path></svg>
            </a>
          </sc-if>
        </sc-if>
        <a href="{{ sel.navUrl }}" target="_blank" style="display:flex;align-items:center;justify-content:space-between;min-height:48px;margin-top:14px;padding:0 14px;border:2px solid var(--lnsoft);text-decoration:none;color:var(--mut);font-size:14px;font-weight:600" style-hover="color:var(--ink);border-color:var(--ln)" style-focus="outline:2px solid #ec3013;outline-offset:2px">
          <span>In Karten-App öffnen</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M7 17 17 7M8 7h9v9"></path></svg>
        </a>
      </div>
    </div>
  </sc-if>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props="{&quot;$preview&quot;:{&quot;width&quot;:390,&quot;height&quot;:844},&quot;markerScale&quot;:{&quot;editor&quot;:&quot;range&quot;,&quot;default&quot;:1,&quot;min&quot;:0.8,&quot;max&quot;:1.6,&quot;step&quot;:0.1,&quot;tsType&quot;:&quot;number&quot;,&quot;section&quot;:&quot;Karte&quot;,&quot;unit&quot;:&quot;×&quot;},&quot;showRoute&quot;:{&quot;editor&quot;:&quot;boolean&quot;,&quot;default&quot;:true,&quot;tsType&quot;:&quot;boolean&quot;,&quot;section&quot;:&quot;Karte&quot;},&quot;flussleiste&quot;:{&quot;editor&quot;:&quot;boolean&quot;,&quot;default&quot;:true,&quot;tsType&quot;:&quot;boolean&quot;,&quot;section&quot;:&quot;Sheet&quot;}}">
class Component extends DCLogic {
  state = { sel: null, sheet: 'peek', mode: 'standard', dark: false, panel: false, dragDy: 0, dragging: false };
  TOTAL = 1021;
  WPS = [
    {id:'quelle',name:'Labská bouda (Elbquelle)',type:'poi',coords:[50.771,15.540],km:0,detour:0,notes:['1387 m ü. NN — Startpunkt','Abfahrt: 14 % Gefälle auf 8 km']},
    {id:'hradec',name:'Hradec Králové',type:'ort',coords:[50.209,15.832],km:102,detour:0,notes:['Bahnhof (Notausstieg)','Radladen am Marktplatz']},
    {id:'litomerice',name:'Litoměřice',type:'ort',coords:[50.534,14.132],km:300,detour:0,notes:['Supermarkt am Radweg','Marktplatz mit Brunnen (Wasser)']},
    {id:'decin',name:'Děčín',type:'ort',coords:[50.782,14.215],km:348,detour:0,notes:['Bahnhof (Notausstieg)','Letzter Geldautomat vor der Grenze (CZK)']},
    {id:'schandau',name:'Bad Schandau',type:'ort',coords:[50.917,14.155],km:372,detour:0,notes:['Grenzübertritt bei km 366','Trinkwasser am Elbkai'],sleep:[{name:'Camping Ostrauer Mühle',type:'camping',phone:'+49 35022 42742',detourKm:2.1}]},
    {id:'dresden',name:'Dresden',type:'ort',coords:[51.053,13.741],km:415,detour:0,notes:['Bahnhof Neustadt (Notausstieg)','Radweg wechselt ans linke Ufer','Viele Radläden'],sleep:[{name:'Pension Elbblick',type:'pension',phone:'+49 351 8996120',detourKm:0.8}]},
    {id:'meissen',name:'Meißen',type:'ort',coords:[51.163,13.472],km:445,detour:0,notes:['Supermarkt am Radweg']},
    {id:'riesa',name:'Riesa',type:'ort',coords:[51.308,13.293],km:482,detour:0,notes:['Supermarkt direkt am Radweg','Stadtbrücke = Ersatzquerung Belgern']},
    {id:'torgau',name:'Torgau',type:'ort',coords:[51.560,13.005],km:528,detour:0,notes:['Bahnhof (Notausstieg)'],sleep:[{name:'Campingplatz Torgau',type:'camping',phone:'+49 3421 712159',detourKm:1.4}]},
    {id:'wittenberg',name:'Lutherstadt Wittenberg',type:'ort',coords:[51.867,12.646],km:598,detour:1.5,notes:['Bahnhof (Notausstieg)','Altstadt liegt 1,5 km ab Radweg']},
    {id:'dessau',name:'Dessau',type:'ort',coords:[51.839,12.242],km:646,detour:0,notes:['Supermarkt am Radweg'],sleep:[{name:'Camping Adria Mildensee',type:'camping',phone:'+49 340 2160945',detourKm:3.2}]},
    {id:'magdeburg',name:'Magdeburg',type:'ort',coords:[52.131,11.635],km:722,detour:0,notes:['Bahnhof (Notausstieg)','Pflaster in der Altstadt']},
    {id:'tangermuende',name:'Tangermünde',type:'ort',coords:[52.545,11.973],km:792,detour:0,notes:['Brücke = Ersatzquerung Sandau'],sleep:[{name:'Pension Alte Brauerei',type:'pension',phone:'+49 39322 43794',detourKm:0.4}]},
    {id:'havelberg',name:'Havelberg',type:'ort',coords:[52.825,12.074],km:828,detour:2,notes:['Havelmündung; 2 km ab Radweg'],sleep:[{name:'Campingplatz Havelberg',type:'camping',phone:'+49 39387 88222',detourKm:2.0}]},
    {id:'wittenberge',name:'Wittenberge',type:'ort',coords:[53.005,11.750],km:855,detour:0,notes:['Bahnhof (Notausstieg)','Supermarkt am Radweg','Danach 70 km dünn besiedelt']},
    {id:'doemitz',name:'Dömitz',type:'ort',coords:[53.140,11.249],km:893,detour:0,notes:['Festung; Wasser auffüllen','Letzter Supermarkt vor Hitzacker']},
    {id:'hitzacker',name:'Hitzacker',type:'ort',coords:[53.152,11.043],km:916,detour:0,notes:['Altstadtinsel'],sleep:[{name:'Camping Elbtalaue',type:'camping',phone:'+49 5862 359',detourKm:1.1}]},
    {id:'lauenburg',name:'Lauenburg',type:'ort',coords:[53.371,10.556],km:963,detour:0,notes:['Bahnhof (Notausstieg)'],sleep:[{name:'Pension Elbterrasse',type:'pension',phone:'+49 4153 55871',detourKm:0.3}]},
    {id:'hamburg',name:'Hamburg',type:'poi',coords:[53.545,9.968],km:1021,detour:0,notes:['Ziel: Landungsbrücken','S-Bahn / Fernbahnhof']}
  ];
  CXS = [
    {id:'rathen',name:'Gierfähre Rathen',kind:'gierfaehre',coords:[50.959,14.083],km:381,status:'gruen',statusDate:'2026-08-18',hours:'05:45–23:00, alle 10 min',note:'Personen + Rad'},
    {id:'pillnitz',name:'Fähre Pillnitz',kind:'faehre',coords:[51.008,13.868],km:402,status:'gruen-check',statusDate:'2026-08-18',hours:'05:00–22:00',backup:'Blaues Wunder (Brücke), +3 km',note:'Bei Pegel < 80 cm Pause'},
    {id:'belgern',name:'Gierfähre Belgern',kind:'gierfaehre',coords:[51.478,13.123],km:505,status:'gelb',statusDate:'2026-08-17',hours:'Mo–Sa 06–18 Uhr',backup:'Stadtbrücke Riesa, +23 km',note:'Wasserstandsabhängig — vorher anrufen'},
    {id:'coswig',name:'Fähre Coswig (Anhalt)',kind:'faehre',coords:[51.883,12.442],km:612,status:'gruen-check',statusDate:'2026-08-18',hours:'06–20 Uhr',backup:'Brücke Wittenberg, +14 km',note:'Wasserstandsabhängig'},
    {id:'aken',name:'Fähre Aken',kind:'faehre',coords:[51.856,12.043],km:662,status:'rot',statusDate:'2026-08-15',hours:'—',backup:'Brücke Dessau (B185), +9 km',note:'Motorschaden — außer Betrieb bis auf Weiteres'},
    {id:'westerhuesen',name:'Gierfähre Westerhüsen',kind:'gierfaehre',coords:[52.072,11.672],km:712,status:'gruen',statusDate:'2026-08-18',hours:'Mo–Fr 05–19, Sa/So 09–18'},
    {id:'rogaetz',name:'Fähre Rogätz',kind:'faehre',coords:[52.318,11.762],km:758,status:'gruen',statusDate:'2026-08-18',hours:'06–20 Uhr'},
    {id:'sandau',name:'Gierfähre Sandau',kind:'gierfaehre',coords:[52.784,12.052],km:824,status:'gruen-check',statusDate:'2026-08-18',hours:'06–19 Uhr',backup:'Brücke Tangermünde, +18 km',note:'Ab Pegel < 90 cm Ausfall'},
    {id:'doemitz-bruecke',name:'Straßenbrücke Dömitz',kind:'bruecke',coords:[53.139,11.258],km:893,status:'gruen',statusDate:'2026-08-18',hours:'jederzeit',critical:true,note:'Einzige verlässliche Querung zwischen Wittenberge und Lauenburg'},
    {id:'darchau',name:'Fähre Darchau',kind:'faehre',coords:[53.232,10.888],km:934,status:'gelb',statusDate:'2026-08-16',hours:'05:30–21:45',backup:'Brücke Dömitz, 41 km zurück',note:'Ersatzfähre mit halber Taktung'},
    {id:'zollenspieker',name:'Zollenspieker Fähre',kind:'faehre',coords:[53.399,10.204],km:992,status:'gruen',statusDate:'2026-08-18',hours:'06–20 Uhr'},
    {id:'elbtunnel',name:'Alter Elbtunnel',kind:'tunnel',coords:[53.546,9.966],km:1021,status:'gruen',statusDate:'2026-08-18',hours:'jederzeit, Rad schieben',note:'Aufzug oder Treppe'}
  ];
  STATUS = {
    'gruen':{c:'#2f7d33',label:'IN BETRIEB'},
    'gruen-check':{c:'#2f7d33',label:'IN BETRIEB · LIVE PRÜFEN',check:true},
    'gelb':{c:'#b26a00',label:'EINGESCHRÄNKT'},
    'rot':{c:'#8f1d1d',label:'AUSSER BETRIEB'}
  };
  KIND = {bruecke:'BRÜCKE',faehre:'FÄHRE',gierfaehre:'GIERFÄHRE',tunnel:'TUNNEL',ort:'ETAPPENORT',poi:'ORT',camping:'CAMPING',pension:'PENSION'};
  WPBLUE = '#3c5a68';
  ACC = '#ec3013';

  constructor(props){
    super(props);
    this.SLEEPS = [];
    this.WPS.forEach(w => (w.sleep||[]).forEach((s,i) => this.SLEEPS.push({
      id: w.id+'-sl'+i, name: s.name, type: s.type, phone: s.phone, detourKm: s.detourKm,
      parent: w.name, km: w.km, coords: [w.coords[0]+0.014+i*0.01, w.coords[1]+0.022]
    })));
  }
  mapRef = (el) => { this.el = el; };
  componentDidMount(){ this.waitL(); }
  waitL(){
    if (window.L && this.el && !this.map) this.initMap();
    else if (!this.map) setTimeout(() => this.waitL(), 120);
  }
  initMap(){
    const L = window.L;
    this.map = L.map(this.el, {zoomControl:false, attributionControl:true});
    this.map.attributionControl.setPrefix(false);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom:19, attribution:'© OpenStreetMap'}).addTo(this.map);
    this.routeLayer = L.polyline(this.WPS.map(w=>w.coords), {color:this.WPBLUE, weight:3, opacity:.45, dashArray:'1 7', lineCap:'round'});
    this.markerLayer = L.layerGroup().addTo(this.map);
    this.map.fitBounds(L.latLngBounds(this.WPS.map(w=>w.coords)), {padding:[30,30]});
    this.map.on('click', () => this.closeSheet());
    this.POS = [51.02, 13.85];
    const posHtml = '<div style="width:20px;height:20px;position:relative"><div class="pos-halo"></div><div style="position:absolute;inset:4px;background:#ec3013;border:2px solid #f3f2f2;border-radius:50%;box-shadow:0 1px 4px rgba(0,0,0,.4)"></div></div>';
    L.marker(this.POS, {icon:this.mk(posHtml,20), interactive:false, zIndexOffset:1000}).addTo(this.map);
    this.rebuild();
  }
  scale(){ return this.props.markerScale ?? 1; }
  pap(){ return this.state.dark ? '#211f1e' : '#f3f2f2'; }
  selRing(){ return `outline:3px solid ${this.ACC};outline-offset:2px;`; }
  mk(html, s){ return window.L.divIcon({html, className:'', iconSize:[s,s], iconAnchor:[s/2,s/2]}); }
  rebuild(){
    if (!this.map) return;
    const L = window.L, {mode, sel, dark} = this.state, k = this.scale(), pap = this.pap();
    this.markerLayer.clearLayers();
    if (this.props.showRoute ?? true) { if (!this.map.hasLayer(this.routeLayer)) this.routeLayer.addTo(this.map); }
    else if (this.map.hasLayer(this.routeLayer)) this.map.removeLayer(this.routeLayer);
    const dimWp = mode !== 'standard', dimSl = mode === 'querungen', dimCx = mode === 'schlaf';
    this.WPS.forEach(p => {
      const isSel = sel && sel.id === p.id;
      const s = Math.round((dimWp ? 10 : 16) * k);
      const html = `<div style="box-sizing:border-box;width:${s}px;height:${s}px;border-radius:50%;background:${this.WPBLUE};border:2px solid ${pap};box-shadow:0 1px 4px rgba(0,0,0,.3);opacity:${dimWp&&!isSel?0.35:1};${isSel?this.selRing():''}"></div>`;
      window.L.marker(p.coords, {icon:this.mk(html, s+10)}).on('click', () => this.select(p,'wp')).addTo(this.markerLayer);
    });
    this.SLEEPS.forEach(p => {
      const isSel = sel && sel.id === p.id;
      const s = Math.round((mode==='schlaf' ? 30 : 22) * k);
      const html = `<div style="box-sizing:border-box;width:${s}px;height:${s}px;background:${pap};border:2px solid ${this.WPBLUE};box-shadow:0 1px 4px rgba(0,0,0,.3);display:flex;align-items:center;justify-content:center;opacity:${dimSl&&!isSel?0.35:1};${isSel?this.selRing():''}">`+
        `<svg width="${Math.round(s*0.6)}" height="${Math.round(s*0.6)}" viewBox="0 0 24 24" fill="none" stroke="${this.WPBLUE}" stroke-width="3" stroke-linejoin="round"><path d="M3 10.5 12 3l9 7.5"></path><path d="M5 9v11h14V9"></path></svg></div>`;
      window.L.marker(p.coords, {icon:this.mk(html, s+10)}).on('click', () => this.select(p,'sl')).addTo(this.markerLayer);
    });
    this.CXS.forEach(p => {
      const isSel = sel && sel.id === p.id;
      const st = this.STATUS[p.status];
      const big = mode === 'querungen';
      const s = Math.round((big ? 30 : (p.critical ? 20 : 15)) * k);
      const inner = Math.round(s * 0.72);
      const showColor = big || p.critical || isSel;
      const html = `<div style="width:${s+12}px;height:${s+12}px;display:flex;align-items:center;justify-content:center;opacity:${dimCx&&!isSel?0.35:1}">`+
        `<div style="box-sizing:border-box;width:${inner}px;height:${inner}px;transform:rotate(45deg);background:${showColor?st.c:this.WPBLUE};border:2px solid ${pap};box-shadow:0 1px 4px rgba(0,0,0,.3);position:relative;${p.critical?`outline:2px solid ${dark?'#eceae6':'#201e1d'};outline-offset:2px;`:''}${isSel?this.selRing():''}">`+
        `${st.check && showColor ? `<div style="position:absolute;inset:28%;background:${pap};border-radius:50%"></div>` : ''}</div></div>`;
      window.L.marker(p.coords, {icon:this.mk(html, s+12)}).on('click', () => this.select(p,'cx')).addTo(this.markerLayer);
    });
  }
  normalize(p, kind){
    const T = this.TOTAL;
    const fmtKm = v => (v % 1 ? v.toFixed(1).replace('.',',') : String(v));
    const o = {
      id: p.id, name: p.name, kindTag: kind, km: p.km,
      pct: Math.max(1, Math.round(p.km / T * 100)) + '%',
      navUrl: `https://www.google.com/maps?q=${p.coords[0]},${p.coords[1]}`,
      coords: p.coords, critical: !!p.critical,
      remainStr: String(T - p.km)
    };
    if (kind === 'wp'){
      o.kicker = 'WEGPUNKT · ' + this.KIND[p.type];
      o.detourStr = p.detour ? '+' + fmtKm(p.detour) + ' km' : '0 km';
      o.notes = p.notes || [];
      o.sleepList = (p.sleep||[]).map(s => ({name:s.name, typeLabel:this.KIND[s.type], phone:s.phone, telHref:'tel:'+s.phone.replace(/\s/g,''), detourStr:'+'+fmtKm(s.detourKm)+' km'}));
    }
    if (kind === 'sl'){
      o.kicker = 'SCHLAFPLATZ · ' + this.KIND[p.type];
      o.detourStr = '+' + fmtKm(p.detourKm) + ' km';
      o.parent = p.parent; o.phone = p.phone; o.telHref = 'tel:' + p.phone.replace(/\s/g,'');
    }
    if (kind === 'cx'){
      const st = this.STATUS[p.status];
      o.kicker = 'QUERUNG · ' + this.KIND[p.kind];
      o.detourStr = '0 km';
      o.status = p.status; o.statusLabel = st.label;
      o.badgeBg = st.check ? 'transparent' : st.c;
      o.badgeFg = st.check ? st.c : '#f8f7f5';
      o.badgeBd = st.c;
      const d = p.statusDate.split('-');
      o.statusDateFmt = d[2] + '.' + d[1] + '.';
      o.hours = p.hours; o.backup = p.backup || ''; o.note = p.note || '';
      o.pegel = p.status === 'gruen-check' || p.status === 'gelb';
    }
    return o;
  }
  setSt(patch){ this.setState(patch); setTimeout(() => this.rebuild(), 0); }
  select(p, kind){
    this.setSt({sel: this.normalize(p, kind), sheet:'peek', panel:false, dragDy:0, dragging:false});
    const L = window.L, m = this.map;
    const z = Math.max(m.getZoom(), 10);
    const pt = m.project(L.latLng(p.coords), z).add([0, m.getSize().y * 0.14]);
    m.setView(m.unproject(pt, z), z, {animate:true});
  }
  closeSheet(){ if (this.state.sel) this.setSt({sel:null, dragDy:0, dragging:false}); }
  handleDown = (e) => {
    if (e.target.closest && e.target.closest('button,a')) return;
    this.drag = {y0: e.clientY, moved: false};
    this.setState({dragging:true, dragDy:0});
    window.addEventListener('pointermove', this.onDragMove);
    window.addEventListener('pointerup', this.onDragUp);
  };
  onDragMove = (e) => {
    let dy = e.clientY - this.drag.y0;
    if (Math.abs(dy) > 6) this.drag.moved = true;
    if (this.state.sheet === 'full') dy = Math.max(-20, dy);
    this.setState({dragDy: dy});
  };
  onDragUp = () => {
    window.removeEventListener('pointermove', this.onDragMove);
    window.removeEventListener('pointerup', this.onDragUp);
    const dy = this.state.dragDy, sheet = this.state.sheet;
    let next = sheet;
    if (!this.drag.moved) next = sheet === 'full' ? 'peek' : 'full';
    else if (dy < -50) next = 'full';
    else if (dy > 60) next = sheet === 'full' ? 'peek' : null;
    if (next === null) this.setSt({sel:null, dragging:false, dragDy:0});
    else this.setState({sheet: next, dragging:false, dragDy:0});
  };
  componentDidUpdate(prevProps){
    if (prevProps && (prevProps.markerScale !== this.props.markerScale || prevProps.showRoute !== this.props.showRoute)) this.rebuild();
  }
  renderVals(){
    const s = this.state;
    const base = s.sheet === 'full' ? '0px' : 'calc(100% - 272px)';
    const acc = 'var(--color-accent, #ec3013)';
    return {
      mapRef: this.mapRef,
      darkAttr: s.dark ? '1' : '0',
      hasSel: !!s.sel,
      sel: s.sel || {},
      isWp: !!s.sel && s.sel.kindTag === 'wp',
      isSl: !!s.sel && s.sel.kindTag === 'sl',
      isCx: !!s.sel && s.sel.kindTag === 'cx',
      hasSleep: !!s.sel && !!(s.sel.sleepList && s.sel.sleepList.length),
      isFull: s.sheet === 'full',
      showLeiste: s.sheet === 'full' && (this.props.flussleiste ?? true) && !!s.sel,
      sheetTf: s.dragging ? `translateY(calc(${base} + ${s.dragDy}px))` : `translateY(${base})`,
      sheetTrans: s.dragging ? 'none' : 'transform .18s ease-out',
      contentOv: s.sheet === 'full' ? 'auto' : 'hidden',
      panelOpen: s.panel,
      toggPanel: () => this.setState({panel: !s.panel}),
      setModeStd: () => this.setSt({mode:'standard'}),
      setModeCx: () => this.setSt({mode:'querungen'}),
      setModeSl: () => this.setSt({mode:'schlaf'}),
      toggDark: () => this.setSt({dark: !s.dark}),
      stdFill: s.mode === 'standard' ? acc : 'transparent',
      cxFill: s.mode === 'querungen' ? acc : 'transparent',
      slFill: s.mode === 'schlaf' ? acc : 'transparent',
      darkFill: s.dark ? acc : 'transparent',
      handleDown: this.handleDown,
      close: () => this.closeSheet(),
      locate: () => { if (this.map) this.map.setView(this.POS, 12, {animate:true}); },
      ticks: [415,528,722,855].map(km => ({pct: Math.round(km/this.TOTAL*100)+'%'}))
    };
  }
}
</script>
</body>
</html>

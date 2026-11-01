from pathlib import Path
import json, math
R=Path(__file__).resolve().parents[1]
dots=json.loads((R/'assets/img/world-dots.json').read_text())
cities={'SEA':(-122.33,47.61),'MSP':(-93.27,44.98),'CHI':(-87.63,41.88),'NYC':(-74.01,40.71),'MEX':(-99.13,19.43),'GRU':(-46.63,-23.55),'LON':(-.12,51.51),'LIS':(-9.14,38.72),'IST':(28.98,41.01),'DXB':(55.27,25.20),'DEL':(77.21,28.61),'SIN':(103.82,1.35),'TYO':(139.69,35.68),'JNB':(28.05,-26.20),'SYD':(151.21,-33.87)}
links=[('CHI','SEA'),('CHI','MSP'),('CHI','NYC'),('CHI','MEX'),('CHI','GRU'),('CHI','LON'),('CHI','LIS'),('LON','IST'),('IST','DXB'),('DXB','DEL'),('DEL','SIN'),('SIN','TYO'),('SIN','SYD'),('LON','JNB'),('CHI','TYO')]
def point(lon,lat): return ((lon+180)*3,(72-lat)*3+42)
s=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 450" role="img" aria-label="World network with Chicago headquarters and Minneapolis and Seattle offices"><defs><radialGradient id="glow"><stop stop-color="#5ED6AA" stop-opacity=".5"/><stop offset="1" stop-color="#5ED6AA" stop-opacity="0"/></radialGradient></defs><g fill="#637b8e" opacity=".65">']
for lon,lat in dots:
 x,y=point(lon,lat);s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.4"/>')
s.append('</g><g fill="none" stroke-width="1.1">')
for a,b in links:
 x,y=point(*cities[a]);X,Y=point(*cities[b]);hub=a=='CHI'; lift=min(155,math.hypot(X-x,Y-y)*.3+15)
 s.append(f'<path stroke="{"#5ED6AA" if hub else "#7FB8FF"}" opacity=".6" d="M{x:.1f},{y:.1f} Q{(x+X)/2:.1f},{min(y,Y)-lift:.1f} {X:.1f},{Y:.1f}"/>')
s.append('</g>')
for name,(lon,lat) in cities.items():
 x,y=point(lon,lat); hub=name in ['SEA','MSP','CHI'];color='#5ED6AA' if hub else '#EEF1F4'
 if hub:s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{35 if name=="CHI" else 19}" fill="url(#glow)"/>')
 dx,dy={'SEA':(-25,-13),'MSP':(-36,-15),'CHI':(8,20),'NYC':(9,-2)}.get(name,(8,-9))
 s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{4.4 if name=="CHI" else 2.9}" fill="{color}"/><text x="{x+dx:.1f}" y="{y+dy:.1f}" fill="{color}" font-family="monospace" font-size="10">{name}</text>')
s.append('</svg>');world=''.join(s);(R/'assets/img/world.svg').write_text(world)
orbit='<svg class="orbit" viewBox="0 0 600 460" role="img" aria-label="Systems, Data and Field orbit operating experience at the core"><circle cx="300" cy="215" r="160" fill="none" stroke="#223040" stroke-dasharray="2 8"/>'
for a,c in [(-28,'#5ED6AA'),(28,'#7FB8FF'),(90,'#EEF1F4')]:orbit+=f'<ellipse cx="300" cy="215" rx="214" ry="73" transform="rotate({a} 300 215)" fill="none" stroke="{c}" stroke-opacity=".65"/>'
orbit+='<circle cx="300" cy="215" r="57" fill="#121821" stroke="#223040"/><image href="/assets/img/logo.png" x="277" y="186" width="46" height="58"/><g font-family="monospace" font-size="11" letter-spacing="2"><text x="430" y="100" fill="#5ED6AA">SYSTEMS</text><text x="86" y="100" fill="#7FB8FF">DATA</text><text x="316" y="433" fill="#EEF1F4">FIELD</text><text x="300" y="311" text-anchor="middle" fill="#C5CDD6">EXPERIENCE AT THE CORE</text></g><circle cx="483" cy="106" r="4" fill="#5ED6AA"/><circle cx="117" cy="106" r="4" fill="#7FB8FF"/><circle cx="300" cy="429" r="4" fill="#EEF1F4"/></svg>'

print('Rebuilt assets/img/world.svg from the cached Natural Earth dots.')

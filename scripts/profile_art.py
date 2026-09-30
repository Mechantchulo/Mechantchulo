"""Generate repository-owned animated profile art. Python standard library only."""
import datetime as dt
import html
import json
from pathlib import Path
import urllib.request
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)

def svg(width, height, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img"><title>Erick Mutua — backend engineer</title><rect width="{width}" height="{height}" rx="16" fill="#0d1117"/><rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="16" fill="none" stroke="#30363d"/><style>text{{font-family:monospace}} .line{{animation:reveal .6s both}} @keyframes reveal{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:translateY(0)}}}} @media(prefers-reduced-motion:reduce){{.line{{animation:none}}}}</style>{body}</svg>'''

def text(x,y,value,size=16,color='#c9d1d9',delay=0):
    return f'<text class="line" style="animation-delay:{delay}s" x="{x}" y="{y}" font-size="{size}" fill="{color}">{html.escape(value)}</text>'

body = ''.join(f'<circle cx="{24+i*20}" cy="22" r="5" fill="{c}"/>' for i,c in enumerate(['#ff5f57','#febc2e','#28c840']))
body += text(90,27,'erick@github ~ /profile',13,'#8b949e')
body += text(30,78,'$ whoami',17,'#39d353',.1)
body += text(30,126,'Erick Mutua',36,'#f0f6fc',.3)
body += text(30,163,'Backend Engineer • Real-Time Systems Developer',18,'#c9d1d9',.5)
body += text(30,201,'APIs / WebSockets / Cloud / AI integrations',15,'#8b949e',.7)
(ASSETS/'header.svg').write_text(svg(860,235,body))

rows = [('USER','Mechantchulo'),('FOCUS','Backend & real-time systems'),('LANG','Python · JavaScript · Java · Bash'),('WEB','Django · FastAPI · Node.js · React'),('OPS','Docker · Linux · Git · MySQL'),('BUILD','Reliable systems for real problems')]
body = text(24,35,'$ neofetch --profile',17,'#39d353')
for i,(key,value) in enumerate(rows):
    body += text(24,79+i*33,key,13,'#39d353',.15*i)
    body += text(90,79+i*33,value,13,'#c9d1d9',.15*i)
(ASSETS/'info-card.svg').write_text(svg(490,280,body))

class Contributions(HTMLParser):
    def __init__(self):
        super().__init__(); self.cells={}; self.tooltips={}; self.tip=None; self.parts=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('data-date') and a.get('data-level'):
            self.cells[a['data-date']]={'date':a['data-date'],'level':int(a['data-level']),'id':a.get('id'),'count':int(a['data-count']) if a.get('data-count','').isdigit() else None}
        if tag=='tool-tip': self.tip=a.get('for'); self.parts=[]
    def handle_data(self,data):
        if self.tip: self.parts.append(data)
    def handle_endtag(self,tag):
        if tag=='tool-tip' and self.tip:
            self.tooltips[self.tip]=''.join(self.parts).strip(); self.tip=None

def heatmap():
    req=urllib.request.Request('https://github.com/users/Mechantchulo/contributions',headers={'User-Agent':'Erick-Profile-Art'})
    with urllib.request.urlopen(req,timeout=30) as response: raw=response.read().decode()
    parser=Contributions(); parser.feed(raw)
    if len(parser.cells)<300: raise RuntimeError('Contribution response incomplete; retaining previous art')
    days=sorted(parser.cells.values(),key=lambda d:d['date'])
    for d in days:
        tip=parser.tooltips.get(d['id'],'')
        first=tip.split(' ')[0].replace(',','')
        if first.isdigit(): d['count']=int(first)
        elif tip.startswith('No contributions'): d['count']=0
        d.pop('id',None)
    body=text(24,35,'$ ./contributions.sh',17,'#39d353')
    start=dt.date.fromisoformat(days[0]['date']); start-=dt.timedelta(days=(start.weekday()+1)%7)
    colors=['#161b22','#0e4429','#006d32','#26a641','#39d353']
    for d in days:
        date=dt.date.fromisoformat(d['date']); offset=(date-start).days; col,row=divmod(offset,7)
        body+=f'<rect class="line" style="animation-delay:{col*.015+row*.035:.3f}s" x="{28+col*15}" y="{64+row*15}" width="11" height="11" rx="2" fill="{colors[min(d["level"],4)]}"><title>{d["date"]}: {d["count"] if d["count"] is not None else "activity level "+str(d["level"])} contributions</title></rect>'
    label=f'{sum(d["count"] for d in days):,} contributions in the displayed calendar' if all(d['count'] is not None for d in days) else 'Public GitHub contribution calendar'
    body+=text(28,199,label,13,'#8b949e',1)
    body+=text(28,228,'Updated '+dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')+' UTC',12,'#8b949e',1)
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'data/contributions.json').write_text(json.dumps(days,indent=2)+'\n')
    (ASSETS/'contributions.svg').write_text(svg(860,250,body))

if __name__=='__main__': heatmap()

from pathlib import Path
import json, math, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / 'data/dashboard-data.json'
QUERIES = {
    'material-handling':'warehouse automation OR intralogistics OR ASRS OR AMR',
    'process':'process automation OR instrumentation OR DCS industrial',
    'heavy-industries':'mining automation OR metals industry OR cement automation',
    'manufacturing-assembly':'manufacturing automation OR industrial robotics OR machine vision',
    'packaging':'packaging machinery OR PMMI OR packaging robotics',
    'converting-printing-web':'web handling OR roll-to-roll converting OR printing automation'
}
TOPICS = {
    'material-handling': [('Mixed-fleet orchestration',['orchestration','mixed fleet','amr']),('Robotics at scale',['robot','automation']),('Lifecycle performance',['maintenance','lifecycle','uptime']),('Modular architecture',['modular','decentralized'])],
    'process': [('Industrial AI in context',['industrial ai','artificial intelligence']),('Brownfield modernization',['brownfield','modernization','migration']),('OT cybersecurity',['cybersecurity','62443','security']),('Workforce knowledge',['workforce','operator','skills'])],
    'heavy-industries': [('Autonomous operations',['autonomous','remote operations']),('Critical materials',['critical mineral','copper','lithium']),('Energy economics',['energy','power']),('Asset reliability',['maintenance','reliability','uptime'])],
    'manufacturing-assembly': [('Flexible automation',['flexible','high mix']),('Robotics adoption',['robot','cobot']),('Vision and quality',['machine vision','quality','inspection']),('Digital engineering',['digital twin','simulation','virtual commissioning'])],
    'packaging': [('Flexible machinery',['flexible','changeover','sku']),('End-of-line robotics',['robot','pallet']),('Lifecycle and obsolescence',['obsolescence','lifecycle']),('Sustainable packaging',['sustainability','recyclable','epr'])],
    'converting-printing-web': [('Web control performance',['tension','registration','web handling']),('Waste reduction',['waste','yield','scrap']),('Workflow automation',['workflow','automation']),('New substrates and coatings',['substrate','coating','laminating'])]
}
POS = ['growth','expand','increase','investment','record','demand','adoption','recovery','strong','accelerat','opportunity','resilien','productivity']
NEG = ['decline','slow','risk','shortage','tariff','cost','uncertain','layoff','downturn','weak','pressure','delay','volatile']
TECH = ['automation','robot','ai ','digital','software','vision','autonomous','analytics','connected']
CAPITAL = ['investment','order','project','capacity','plant','facility','capital','shipment']
WORK = ['labor','workforce','skills','hiring','operator','talent']

def fetch_news(query):
    url = 'https://news.google.com/rss/search?q=' + urllib.parse.quote(query) + '&hl=en-US&gl=US&ceid=US:en'
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 OEM-Intelligence-Dashboard/1.0'})
    with urllib.request.urlopen(req, timeout=30) as response:
        root = ET.fromstring(response.read())
    items=[]
    for item in root.findall('.//item')[:20]:
        title=item.findtext('title','').strip(); link=item.findtext('link','').strip()
        pub=item.findtext('pubDate','').strip(); source=item.findtext('source','').strip()
        if title and link: items.append({'title':title,'url':link,'published':pub,'source':source or 'Google News'})
    return items

def hits(text, words): return sum(text.count(w) for w in words)
def clamp(x,lo=0,hi=100): return max(lo,min(hi,int(round(x))))
def label(score):
    if score>=85:return 'Strongly positive'
    if score>=75:return 'Positive'
    if score>=65:return 'Constructive'
    if score>=55:return 'Selectively constructive'
    if score>=45:return 'Mixed'
    if score>=30:return 'Cautious'
    return 'Negative'

def select_topics(slug,text):
    ranked=sorted(((hits(text,words),name) for name,words in TOPICS[slug]),reverse=True)
    chosen=[name for score,name in ranked if score>0]
    defaults=[name for name,_ in TOPICS[slug]]
    return (chosen + [x for x in defaults if x not in chosen])[:4]

def derive(slug, segment, news, now):
    text=' '.join(n['title'].lower() for n in news)
    pos=hits(text,POS); neg=hits(text,NEG); total=max(pos+neg,1)
    tone=50+30*(pos-neg)/total
    tech=clamp(45+5*hits(text,TECH),25,95)
    capital=clamp(45+6*hits(text,CAPITAL)+0.15*(tone-50),25,95)
    workforce=clamp(70-7*hits(text,WORK),20,80)
    prior=segment.get('score',65)
    raw=0.32*tone+0.24*tech+0.22*capital+0.12*workforce+0.10*prior
    score=clamp(max(prior-5,min(prior+5,raw)),25,95)
    posture='Accelerating' if score>=80 else 'Disciplined' if score>=65 else 'Selective' if score>=50 else 'Cautious'
    topics=select_topics(slug,text)
    segment['score']=score; segment['label']=label(score); segment['leaders']=topics; segment['news']=news[:5]
    segment['summary']=(f"The {segment['name']} signal is {segment['label'].lower()} at {score}. "
        f"Current evidence shows {'more growth and investment signals than constraints' if pos>=neg else 'meaningful cost and execution constraints alongside opportunity'}. "
        f"Technology adoption remains {'strong' if tech>=70 else 'selective'}, while capital conversion remains {posture.lower()}.")
    segment['drivers']=[
        {'name':'Market demand','score':clamp(tone)}, {'name':'Technology adoption','score':tech},
        {'name':'Capital confidence','score':capital}, {'name':'Workforce availability','score':workforce},
        {'name':'External risk clarity','score':clamp(62-5*hits(text,NEG),20,80)}, {'name':'Strategic resilience','score':clamp(60+4*hits(text,['resilien','regional','secure','lifecycle']),40,90)}]
    segment['metrics']=[
        {'label':'Composite sentiment','value':str(score),'note':segment['label']},
        {'label':'Articles analyzed','value':str(len(news)),'note':'Current monthly evidence set'},
        {'label':'Positive signal share','value':f"{round(100*pos/total)}%",'note':'Headline-language indicator'},
        {'label':'Technology signal','value':str(tech),'note':'Rules-based evidence score'},
        {'label':'Investment posture','value':posture,'note':now.strftime('%B %Y')}]
    theme=', '.join(topics[:2])
    segment['brief']=[
        f"The monthly evidence set places {segment['name']} at a {segment['label'].lower()} composite score of {score}. The balance of current headlines and source signals indicates {segment['summary'].split('. ',1)[1]}",
        f"Leadership attention is concentrating on {theme}. These themes were selected from repeated terms in the current segment-specific evidence set, then mapped to the dashboard's established strategic taxonomy.",
        f"For OEMs, the practical implication is to pursue opportunities with measurable operating outcomes and a clear implementation path. The current investment posture is {posture.lower()}, so reusable architecture, lifecycle confidence and proof of value remain important to conversion."
    ]
    segment['outlook']=[
        {'case':'Base case','text':f"The {segment['name']} market remains {segment['label'].lower()}, with disciplined conversion around measurable outcomes."},
        {'case':'Upside','text':'A stronger demand mix and improving capital confidence accelerate scalable modernization and new capacity.'},
        {'case':'Downside','text':'Cost, trade or financing pressure delays larger projects while service, retrofit and essential reliability work remain active.'}]
    segment['economics']=(f"The current evidence set contains {pos} positive-growth references and {neg} constraint references across {len(news)} selected items. "
        f"The resulting capital-confidence score is {capital}, with a {posture.lower()} investment posture. This is a directional headline-based indicator rather than an official economic index; use the linked ISM and Federal Reserve sources for primary economic data.")
    segment['opportunities']=[
        {'title':topics[0],'text':'Highest-ranked leadership theme in the current monthly evidence set.'},
        {'title':topics[1],'text':'Second-ranked recurring theme with direct relevance to OEM differentiation.'},
        {'title':'Lifecycle modernization','text':'Use installed-base visibility, serviceability and migration planning to reduce customer risk.'},
        {'title':'Scalable architecture','text':'Translate demand into reusable controls, data, safety and application patterns.'}]
    segment['automation_note']='Automatically generated from public headline metadata using transparent rules. Review before external distribution.'

data=json.loads(DATA_PATH.read_text(encoding='utf-8')); now=datetime.now(timezone.utc); successes=0
for slug,query in QUERIES.items():
    try:
        news=fetch_news(query)
        if not news: raise RuntimeError('No news items returned')
        derive(slug,data['segments'][slug],news,now); successes+=1
    except Exception as exc:
        print(f'WARNING {slug}: {exc}; retaining last successful segment data')
if successes:
    data['last_refreshed']=now.isoformat().replace('+00:00','Z')
    data['refresh_scope']='Monthly automatic refresh of newsroom, indicators, scores, drivers, briefs, outlook, economics and opportunity areas.'
DATA_PATH.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f'Refreshed {successes} of {len(QUERIES)} segments')

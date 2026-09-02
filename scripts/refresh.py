from pathlib import Path
import json, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
DATA_PATH=ROOT/'data/dashboard-data.json'
QUERIES={
 "material-handling":"warehouse automation OR intralogistics OR ASRS OR AMR",
 "process":"process automation OR instrumentation OR DCS industrial",
 "heavy-industries":"mining automation OR metals industry OR cement automation",
 "manufacturing-assembly":"manufacturing automation OR industrial robotics OR machine vision",
 "packaging":"packaging machinery OR PMMI OR packaging robotics",
 "converting-printing-web":"web handling OR roll-to-roll converting OR printing automation"
}
TOPICS={
 "material-handling":{"Mixed-fleet orchestration":["orchestration","mixed fleet","amr"],"Robotics at scale":["robot","automation"],"Lifecycle performance":["maintenance","lifecycle","uptime"],"Modular architecture":["modular","decentralized"]},
 "process":{"Industrial AI in context":["industrial ai","artificial intelligence"],"Brownfield modernization":["brownfield","modernization","migration"],"OT cybersecurity":["cybersecurity","62443","security"],"Workforce knowledge":["workforce","operator","skills"]},
 "heavy-industries":{"Autonomous operations":["autonomous","remote operations"],"Critical materials":["critical mineral","copper","lithium"],"Energy economics":["energy","power"],"Asset reliability":["maintenance","reliability","uptime"]},
 "manufacturing-assembly":{"Flexible automation":["flexible","high mix"],"Robotics adoption":["robot","cobot"],"Vision and quality":["machine vision","quality","inspection"],"Digital engineering":["digital twin","simulation","virtual commissioning"]},
 "packaging":{"Flexible machinery":["flexible","changeover","sku"],"End-of-line robotics":["robot","pallet"],"Lifecycle and obsolescence":["obsolescence","lifecycle"],"Sustainable packaging":["sustainability","recyclable","epr"]},
 "converting-printing-web":{"Web control performance":["tension","registration","web handling"],"Waste reduction":["waste","yield","scrap"],"Workflow automation":["workflow","automation"],"New substrates and coatings":["substrate","coating","laminating"]}
}
def fetch(slug,query):
 url='https://news.google.com/rss/search?q='+urllib.parse.quote(query)+'&hl=en-US&gl=US&ceid=US:en'
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 OEM-Intelligence-POC/1.0'})
 with urllib.request.urlopen(req,timeout=25) as response: xml=response.read()
 root=ET.fromstring(xml); items=[]
 for item in root.findall('.//item')[:10]:
  title=item.findtext('title','').strip(); link=item.findtext('link','').strip(); pub=item.findtext('pubDate','').strip(); source=item.findtext('source','').strip()
  if title and link: items.append({'title':title,'url':link,'published':pub,'source':source or 'Google News'})
 return items

def leader_topics(slug,news):
 text=' '.join(n['title'].lower() for n in news); scored=[]
 for topic,words in TOPICS[slug].items(): scored.append((sum(text.count(w) for w in words),topic))
 scored.sort(reverse=True); chosen=[t for score,t in scored if score>0][:4]
 return chosen or list(TOPICS[slug].keys())[:4]

data=json.loads(DATA_PATH.read_text())
for slug,q in QUERIES.items():
 try:
  news=fetch(slug,q); data['segments'][slug]['news']=news[:5]; data['segments'][slug]['leaders']=leader_topics(slug,news)
 except Exception as exc:
  print(f'WARNING {slug}: {exc}; retaining prior data')
data['last_refreshed']=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
DATA_PATH.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
print('Updated',DATA_PATH)

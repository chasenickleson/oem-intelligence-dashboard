from pathlib import Path
import json
d=json.loads((Path(__file__).resolve().parents[1]/'data/dashboard-data.json').read_text())
assert len(d['segments'])==6
summaries=set(); economics=set(); outlooks=set(); opportunities=set()
for slug,s in d['segments'].items():
 assert 0<=s['score']<=100 and len(s['metrics'])==5 and len(s['drivers'])==6
 assert len(s['brief'])>=3 and len(s['outlook'])==3 and len(s['opportunities'])==4
 assert len(s.get('executive_takeaway',''))>=50 and len(s.get('economics',''))>=250 and s['sources']
 summaries.add(s['summary']); economics.add(s['economics']); outlooks.add(json.dumps(s['outlook'],sort_keys=True)); opportunities.add(json.dumps(s['opportunities'],sort_keys=True))
assert len(summaries)==6 and len(economics)==6 and len(outlooks)==6 and len(opportunities)==6
print('Validation passed: all six segments have distinct summaries, economics, outlooks and opportunities')

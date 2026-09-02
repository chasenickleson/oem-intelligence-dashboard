from pathlib import Path
import json
d=json.loads((Path(__file__).resolve().parents[1]/'data/dashboard-data.json').read_text())
assert len(d['segments'])==6
for s in d['segments'].values():
 assert 0<=s['score']<=100 and len(s['metrics'])==5 and len(s['drivers'])==6 and len(s['brief'])>=3 and len(s['outlook'])==3 and len(s['opportunities'])==4 and s['sources'] and len(s.get('executive_takeaway',''))>=50
print('Validation passed')

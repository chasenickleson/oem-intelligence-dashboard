from pathlib import Path
import json
p=Path(__file__).resolve().parents[1]/'data/dashboard-data.json'
d=json.loads(p.read_text())
assert 'last_refreshed' in d and len(d['segments'])==6
for k,s in d['segments'].items():
 assert 0<=s['score']<=100 and s['name'] and isinstance(s['news'],list) and isinstance(s['leaders'],list)
print('Validation passed for',len(d['segments']),'segments')

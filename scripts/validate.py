from pathlib import Path
import json
p=Path(__file__).resolve().parents[1]/'data/dashboard-data.json';d=json.loads(p.read_text())
assert len(d['segments'])==6
for slug,s in d['segments'].items():
    assert 0 <= s['score'] <= 100
    assert len(s['metrics'])==5 and len(s['drivers'])==6
    assert len(s['brief'])>=3 and len(s['outlook'])==3 and len(s['opportunities'])==4
    assert s['sources']
print('Validation passed for all expanded dashboard fields')

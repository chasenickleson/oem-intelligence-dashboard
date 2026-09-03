from pathlib import Path
import json

data=json.loads((Path(__file__).resolve().parents[1]/"data/dashboard-data.json").read_text())
assert len(data["segments"])==6
summaries=set(); economics=set(); outlooks=set(); opportunities=set()
for slug,segment in data["segments"].items():
    assert 0 <= segment["score"] <= 100
    assert len(segment["metrics"])==5 and len(segment["drivers"])==6
    assert len(segment["brief"])>=3 and len(segment["outlook"])==3 and len(segment["opportunities"])==4
    assert segment["sources"] and len(segment.get("executive_takeaway",""))>=50
    stats=segment.get("evidence_stats",{})
    if stats:
        assert stats["selected"] <= 20 and stats["searches"] >= 1 and stats["publishers"] >= 1
    summaries.add(segment["summary"]); economics.add(segment["economics"])
    outlooks.add(json.dumps(segment["outlook"],sort_keys=True)); opportunities.add(json.dumps(segment["opportunities"],sort_keys=True))
assert len(summaries)==6 and len(economics)==6 and len(outlooks)==6 and len(opportunities)==6
print("Validation passed: six distinct segments and valid evidence metadata")

import json
import sys
import tempfile
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

ROOT=Path(__file__).parents[1]
p=ROOT/"02_AGENTS"/"runtime"/"motore_multi_target_v2.py"
spec=spec_from_file_location("m",p)
m=module_from_spec(spec); spec.loader.exec_module(m)
q=ROOT/"02_AGENTS"/"runtime"/"qa_scoring_engine_v2.py"
qa_spec=spec_from_file_location("qa",q)
qa=module_from_spec(qa_spec); qa_spec.loader.exec_module(qa)

dims=["prezzo","finanziamento","rata","trasparenza_economica","azione"]

def O(dim,level,state="VERIFICATO_WEB"):
    return m.Observation(dim,level,"evidence","https://example.com",state,"2026-08-12","sede")

r=m.evaluate_path("Demo","D2",[O(d,2) for d in dims],dims)
assert r["status"]=="PASS" and r["coverage_ratio"]==1.0 and r["normalized_0_100"]==67

r=m.evaluate_path("Demo","D2",[O(d,2) for d in dims[:4]],dims)
assert r["status"]=="BLOCKED" and r["coverage_ratio"]==0.8 and r["normalized_0_100"] is None

r=m.evaluate_path("Demo","D2",[O(d,0) for d in dims],dims)
assert r["status"]=="BLOCKED" and any("NOT_FOUND_AFTER_PROTOCOL" in i for i in r["issues"])

r=m.evaluate_path("Demo","D2",[O(d,0,"NOT_FOUND_AFTER_PROTOCOL") for d in dims],dims)
assert r["status"]=="PASS" and r["normalized_0_100"]==0

obs=[O(d,2) for d in dims]+[O("prezzo",2)]
r=m.evaluate_path("Demo","D2",obs,dims)
assert r["status"]=="BLOCKED" and r["duplicate_dimensions"]==["prezzo"]

r=m.evaluate_path("Demo","D2",[O("prezzo",2), O("inattesa",2)],dims)
assert r["status"]=="BLOCKED" and r["unexpected_dimensions"]==["inattesa"]

for state in ["UNRESOLVED","COLLECTION_RESTRICTED","CONTRADICTORY"]:
    r=m.evaluate_path("Demo","D2",[O(d,2,state) for d in dims],dims)
    assert r["status"]=="BLOCKED" and r["normalized_0_100"] is None
    assert state in r["blocking_states"]

r=m.validate_saturated_multi_target({"D1":"FOUND","D2":"FOUND","D3":"UNRESOLVED"},["D1","D2","D3"])
assert r["status"]=="BLOCKED" and r["non_terminal_targets"]==["D3"]

r=m.validate_saturated_multi_target({"D1":"FOUND","D2":"FOUND","D3":"NOT_FOUND_AFTER_PROTOCOL"},["D1","D2","D3"])
assert r["status"]=="PASS"

with tempfile.TemporaryDirectory() as td:
    root=Path(td)
    target_master=root/"target_master.json"
    target_master.write_text(json.dumps({"D2":{"dimensions":dims}}), encoding="utf-8")
    blocked=root/"blocked_score.json"
    cell=m.evaluate_path("Demo","D2",[O(d,2) for d in dims[:4]],dims)
    cell["status"]="PASS"
    cell["normalized_0_100"]=53
    blocked.write_text(json.dumps({"companies":[{"company":"Demo","targets":{"D2":cell}}]}), encoding="utf-8")
    issues=qa.validate(str(blocked),str(target_master))
    assert any("blocked target must not produce normalized_0_100" in i[3] for i in issues)
    assert any("status PASS is invalid for blocked target" in i[3] for i in issues)

print(json.dumps({"suite":"SCORING_INTEGRITY_V2","tests":11,"status":"PASS"}))

import json
import sys
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

ROOT=Path(__file__).parents[1]
p=ROOT/"02_AGENTS"/"runtime"/"motore_multi_target_v2.py"
spec=spec_from_file_location("m",p)
m=module_from_spec(spec); spec.loader.exec_module(m)

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

print(json.dumps({"suite":"SCORING_INTEGRITY_V2","tests":5,"status":"PASS"}))

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_step(label, cmd):
    print(f"\n[RRT:E2E] {label}")
    proc = subprocess.run(cmd, text=True)
    return proc.returncode == 0, proc.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-id", required=True)
    ap.add_argument("--company", required=True)
    ap.add_argument("--official-domain", required=True)
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()

    runtime = Path(__file__).resolve().parent
    py = sys.executable
    mode = ["--live"] if args.live else []

    steps = [
        ("Wave 1: A1 Discovery + A2 Entity Scope",
         [py, str(runtime / "canary.py"), "--case-id", args.case_id, "--company", args.company, "--official-domain", args.official_domain, *mode]),
        ("Wave 2: A3 target-specific Deep Scan",
         [py, str(runtime / "wave2_a3_runner.py"), "--case-id", args.case_id, "--company", args.company, "--official-domain", args.official_domain, *mode]),
    ]

    for label, cmd in steps:
        ok, rc = run_step(label, cmd)
        if not ok:
            print(json.dumps({"case_id": args.case_id, "current_run_status": {"status": "BLOCKED", "step": label, "returncode": rc}}, ensure_ascii=False, indent=2))
            return rc or 1

    wave3_cmd = [py, str(runtime / "wave3_a4_a5_runner.py"), "--case-id", args.case_id, *mode]
    ok, rc = run_step("Wave 3: A4 Evidence Audit -> A5 Target Match", wave3_cmd)
    if not ok and rc == 4:
        repair_cmd = [py, str(runtime / "wave2_a3_repair_runner.py"), "--case-id", args.case_id,
                      "--company", args.company, "--official-domain", args.official_domain, *mode]
        repair_ok, repair_rc = run_step("Wave 2R: automatic A3 repair", repair_cmd)
        if not repair_ok:
            print(json.dumps({"case_id": args.case_id, "current_run_status": {"status": "BLOCKED", "step": "Wave 2R: automatic A3 repair", "returncode": repair_rc}}, ensure_ascii=False, indent=2))
            return repair_rc or 1
        ok, rc = run_step("Wave 3R: A4 re-audit -> A5 Target Match", wave3_cmd)

    if not ok:
        print(json.dumps({"case_id": args.case_id, "current_run_status": {"status": "BLOCKED", "step": "Wave 3: A4 Evidence Audit -> A5 Target Match", "returncode": rc}}, ensure_ascii=False, indent=2))
        return rc or 1

    wave4_cmd = [py, str(runtime / "wave4_7_runner.py"), "--case-id", args.case_id, *mode, "--resume"]
    ok, rc = run_step("Wave 4-7: A6 Benchmark -> A7 Red Team -> A8 Commercial Gate -> A9 QA", wave4_cmd)
    if not ok:
        print(json.dumps({"case_id": args.case_id, "current_run_status": {"status": "BLOCKED", "step": "Wave 4-7: A6 Benchmark -> A7 Red Team -> A8 Commercial Gate -> A9 QA", "returncode": rc}}, ensure_ascii=False, indent=2))
        return rc or 1

    print(json.dumps({
        "case_id": args.case_id,
        "company": args.company,
        "official_domain": args.official_domain,
        "current_run_status": {"status": "PASS", "final_stage": "A9_QA_ORCHESTRATOR"}
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

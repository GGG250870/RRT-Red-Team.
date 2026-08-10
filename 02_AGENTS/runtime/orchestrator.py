import json, subprocess, sys, uuid
from pathlib import Path

from cost_control import BudgetPolicy
from state_store import StateStore

class Orchestrator:
    def __init__(self, runtime_dir):
        self.runtime=Path(runtime_dir)
        self.db=self.runtime/"state"/"rrt_agents.sqlite"
        self.registry=self.runtime/"agent_registry.json"
        self.store=StateStore(self.db)
        self.budget=BudgetPolicy()

    def enqueue_case(self, case_id, payload):
        for agent_id,stage in [("A1_DISCOVERY","DISCOVERY"),("A2_ENTITY_SCOPE","ENTITY_SCOPE")]:
            task={
              "task_id":f"{case_id}-{agent_id}-{uuid.uuid4().hex[:8]}",
              "case_id":case_id,
              "agent_id":agent_id,
              "stage":stage,
              "payload":payload,
              "status":"PENDING"
            }
            self.store.enqueue(task)

    def enqueue_agent_task(self, case_id, agent_id, stage, payload):
        task={
          "task_id":f"{case_id}-{agent_id}-{uuid.uuid4().hex[:8]}",
          "case_id":case_id,"agent_id":agent_id,"stage":stage,
          "payload":payload,"status":"PENDING"
        }
        self.store.enqueue(task)

    def _budget_ok(self, case_id):
        case_cost=self.store.cost_for_case(case_id)
        total_cost=self.store.total_cost()
        if case_cost >= self.budget.per_case_usd:
            return False, f"CASE_BUDGET_EXCEEDED ${case_cost:.4f}/${self.budget.per_case_usd:.4f}"
        if total_cost >= self.budget.per_run_usd:
            return False, f"RUN_BUDGET_EXCEEDED ${total_cost:.4f}/${self.budget.per_run_usd:.4f}"
        return True, "PASS"

    def run_agents_parallel(self, agent_ids, live=False, case_id=None):
        if live and case_id:
            ok,reason=self._budget_ok(case_id)
            if not ok:
                return {"status":"BLOCKED","reason":reason}

        procs=[]
        for aid in agent_ids:
            cmd=[sys.executable,str(self.runtime/"worker.py"),
                 "--agent",aid,"--db",str(self.db),"--registry",str(self.registry)]
            if case_id:
                cmd.extend(["--case-id",case_id])
            if live:
                cmd.append("--live")
            procs.append((aid,subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)))
        out={}
        for aid,p in procs:
            stdout,stderr=p.communicate()
            out[aid]={"returncode":p.returncode,"stdout":stdout.strip(),"stderr":stderr.strip()}
        return out

    def status(self):
        return {
            "tasks": self.store.stats(),
            "total_cost_usd": round(self.store.total_cost(),6),
        }

import json, subprocess, sys, uuid, time
from pathlib import Path
from state_store import StateStore

class Orchestrator:
    def __init__(self, runtime_dir):
        self.runtime=Path(runtime_dir)
        self.db=self.runtime/"state"/"rrt_agents.sqlite"
        self.registry=self.runtime/"agent_registry.json"
        self.store=StateStore(self.db)

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

    def run_agents_parallel(self, agent_ids, live=False):
        procs=[]
        for aid in agent_ids:
            cmd=[sys.executable,str(self.runtime/"worker.py"),
                 "--agent",aid,"--db",str(self.db),"--registry",str(self.registry)]
            if live:
                cmd.append("--live")
            procs.append((aid,subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)))
        out={}
        for aid,p in procs:
            stdout,stderr=p.communicate()
            out[aid]={"returncode":p.returncode,"stdout":stdout.strip(),"stderr":stderr.strip()}
        return out

    def status(self):
        return self.store.stats()

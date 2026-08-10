import sqlite3, json, time
from pathlib import Path

class StateStore:
    def __init__(self, db_path):
        self.db_path=str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _conn(self):
        c=sqlite3.connect(self.db_path, timeout=30)
        c.row_factory=sqlite3.Row
        return c

    def _init(self):
        with self._conn() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS tasks(
                task_id TEXT PRIMARY KEY,
                case_id TEXT,
                agent_id TEXT,
                stage TEXT,
                payload TEXT,
                status TEXT,
                attempts INTEGER DEFAULT 0,
                created_at REAL,
                started_at REAL,
                completed_at REAL,
                error TEXT
            )""")
            c.execute("""CREATE TABLE IF NOT EXISTS outputs(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                agent_id TEXT,
                case_id TEXT,
                output_json TEXT,
                created_at REAL
            )""")
            c.execute("""CREATE TABLE IF NOT EXISTS audit_log(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                task_id TEXT,
                agent_id TEXT,
                case_id TEXT,
                details TEXT,
                created_at REAL
            )""")
            c.execute("""CREATE TABLE IF NOT EXISTS cost_ledger(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                agent_id TEXT,
                case_id TEXT,
                model TEXT,
                input_tokens INTEGER,
                output_tokens INTEGER,
                total_tokens INTEGER,
                actual_cost_usd REAL,
                created_at REAL
            )""")

    def enqueue(self, task):
        now=time.time()
        with self._conn() as c:
            c.execute("""INSERT OR REPLACE INTO tasks
              (task_id,case_id,agent_id,stage,payload,status,attempts,created_at)
              VALUES (?,?,?,?,?,?,?,?)""",
              (task["task_id"],task["case_id"],task["agent_id"],task["stage"],
               json.dumps(task.get("payload",{}),ensure_ascii=False),
               task.get("status","PENDING"),task.get("attempts",0),now))
            self.log("ENQUEUE", task["task_id"], task["agent_id"], task["case_id"], {"stage":task["stage"]}, conn=c)

    def claim_next(self, agent_id):
        with self._conn() as c:
            row=c.execute("""SELECT * FROM tasks WHERE agent_id=? AND status='PENDING'
                             ORDER BY created_at LIMIT 1""",(agent_id,)).fetchone()
            if not row:
                return None
            now=time.time()
            updated=c.execute("""UPDATE tasks SET status='RUNNING',started_at=?,attempts=attempts+1
                         WHERE task_id=? AND status='PENDING'""",(now,row["task_id"]))
            if updated.rowcount != 1:
                return None
            fresh=c.execute("SELECT * FROM tasks WHERE task_id=?",(row["task_id"],)).fetchone()
            return dict(fresh)

    def complete(self, task_id, agent_id, case_id, output, status="PASS"):
        now=time.time()
        with self._conn() as c:
            c.execute("""UPDATE tasks SET status=?,completed_at=?,error=NULL WHERE task_id=?""",
                      (status,now,task_id))
            c.execute("""INSERT INTO outputs(task_id,agent_id,case_id,output_json,created_at)
                         VALUES (?,?,?,?,?)""",
                      (task_id,agent_id,case_id,json.dumps(output,ensure_ascii=False),now))
            usage=output.get("usage") or {}
            c.execute("""INSERT INTO cost_ledger(task_id,agent_id,case_id,model,input_tokens,output_tokens,total_tokens,actual_cost_usd,created_at)
                         VALUES (?,?,?,?,?,?,?,?,?)""",
                      (task_id,agent_id,case_id,output.get("model"),usage.get("input_tokens"),usage.get("output_tokens"),usage.get("total_tokens"),output.get("actual_cost_usd",0.0),now))
            self.log("COMPLETE",task_id,agent_id,case_id,{"status":status,"actual_cost_usd":output.get("actual_cost_usd",0.0)},conn=c)

    def fail(self, task_id, agent_id, case_id, error):
        with self._conn() as c:
            c.execute("UPDATE tasks SET status='FAIL',completed_at=?,error=? WHERE task_id=?",
                      (time.time(),str(error),task_id))
            self.log("FAIL",task_id,agent_id,case_id,{"error":str(error)},conn=c)

    def outputs_for_case(self, case_id):
        with self._conn() as c:
            rows=c.execute("SELECT * FROM outputs WHERE case_id=? ORDER BY id",(case_id,)).fetchall()
            return [json.loads(r["output_json"]) for r in rows]

    def cost_for_case(self, case_id):
        with self._conn() as c:
            row=c.execute("SELECT COALESCE(SUM(actual_cost_usd),0) total FROM cost_ledger WHERE case_id=?",(case_id,)).fetchone()
            return float(row["total"] or 0.0)

    def total_cost(self):
        with self._conn() as c:
            row=c.execute("SELECT COALESCE(SUM(actual_cost_usd),0) total FROM cost_ledger").fetchone()
            return float(row["total"] or 0.0)

    def stats(self):
        with self._conn() as c:
            rows=c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status").fetchall()
            return {r["status"]:r["n"] for r in rows}

    def log(self,event_type,task_id,agent_id,case_id,details,conn=None):
        own=False
        if conn is None:
            conn=self._conn(); own=True
        conn.execute("""INSERT INTO audit_log(event_type,task_id,agent_id,case_id,details,created_at)
                        VALUES (?,?,?,?,?,?)""",
                     (event_type,task_id,agent_id,case_id,json.dumps(details,ensure_ascii=False),time.time()))
        if own:
            conn.commit(); conn.close()

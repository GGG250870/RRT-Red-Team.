import sqlite3, json, time
from pathlib import Path

class StateStore:
    def __init__(self, db_path):
        self.db_path=str(db_path)
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
            c.execute("""UPDATE tasks SET status='RUNNING',started_at=?,attempts=attempts+1
                         WHERE task_id=?""",(now,row["task_id"]))
            return dict(row)

    def complete(self, task_id, agent_id, case_id, output, status="PASS"):
        now=time.time()
        with self._conn() as c:
            c.execute("""UPDATE tasks SET status=?,completed_at=?,error=NULL WHERE task_id=?""",
                      (status,now,task_id))
            c.execute("""INSERT INTO outputs(task_id,agent_id,case_id,output_json,created_at)
                         VALUES (?,?,?,?,?)""",
                      (task_id,agent_id,case_id,json.dumps(output,ensure_ascii=False),now))
            self.log("COMPLETE",task_id,agent_id,case_id,{"status":status},conn=c)

    def fail(self, task_id, agent_id, case_id, error):
        with self._conn() as c:
            c.execute("UPDATE tasks SET status='FAIL',completed_at=?,error=? WHERE task_id=?",
                      (time.time(),str(error),task_id))
            self.log("FAIL",task_id,agent_id,case_id,{"error":str(error)},conn=c)

    def outputs_for_case(self, case_id):
        with self._conn() as c:
            rows=c.execute("SELECT * FROM outputs WHERE case_id=? ORDER BY id",(case_id,)).fetchall()
            return [json.loads(r["output_json"]) for r in rows]

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

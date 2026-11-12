"""Dump the user-data tables to a JSON file. Output is encrypted by the workflow, never stored in plain text."""
import datetime as dt
import json
import os
import sys
from urllib.parse import unquote, urlparse

import pg8000.dbapi

TABLES = ["users", "posts", "likes", "follows", "observations", "held_posts", "reports"]


def connect():
    u = urlparse(os.environ["DATABASE_URL"])
    return pg8000.dbapi.connect(
        user=unquote(u.username or ""), password=unquote(u.password or ""),
        host=u.hostname, port=u.port or 5432, database=u.path.lstrip("/"), ssl_context=True)


def main(out_path):
    conn = connect()
    cur = conn.cursor()
    dump = {"exported_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "tables": {}}
    for table in TABLES:
        cur.execute(f"SELECT * FROM {table}")
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        dump["tables"][table] = rows
        print(f"{table}: {len(rows)} rows", flush=True)
    conn.close()
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(dump, f, default=str)
    print(f"wrote {out_path}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "backup.json")

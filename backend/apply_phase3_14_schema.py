import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
import psycopg

url = os.getenv("DATABASE_URL", "").replace("postgresql+psycopg://", "postgresql://").replace("postgresql+asyncpg://", "postgresql://")
if not url:
    print("ERROR: DATABASE_URL not available.")
    exit(1)

sql_path = Path(__file__).parent / "sql" / "cadastral_phase3_14.sql"
sql_content = sql_path.read_text(encoding="utf-8")

with psycopg.connect(url, autocommit=True) as conn:
    with conn.cursor() as cur:
        cur.execute(sql_content)
print("PostGIS schema extension completed successfully.")

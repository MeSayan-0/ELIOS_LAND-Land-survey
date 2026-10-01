import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
import psycopg

url = os.getenv("DATABASE_URL", "").replace("postgresql+psycopg://", "postgresql://").replace("postgresql+asyncpg://", "postgresql://")
if not url:
    print("No database URL configured in .env.")
    exit(0)

sql_path = Path(__file__).parent / "sql" / "cadastral_schema.sql"
sql_content = sql_path.read_text(encoding="utf-8")

try:
    with psycopg.connect(url, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(sql_content)
    print("PostGIS cadastral schema applied successfully via psycopg.")
except Exception as e:
    print(f"Schema application notice: {e}")

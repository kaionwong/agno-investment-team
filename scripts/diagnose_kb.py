"""Diagnostic script for knowledge base state."""
import sys
sys.path.insert(0, '/app')

from db.url import db_url
import psycopg

# psycopg requires plain postgres:// URL, not postgresql+psycopg://
pg_url = db_url.replace("postgresql+psycopg://", "postgresql://")

print("=== Knowledge Base Diagnostic ===\n")
print(f"Connecting to: {pg_url}\n")

with psycopg.connect(pg_url) as conn:
    with conn.cursor() as cur:
        # Check all tables in ai schema
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'ai'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cur.fetchall()]
        print(f"Tables in 'ai' schema: {tables}\n")

        # Count rows in knowledge-related tables
        for t in tables:
            try:
                cur.execute(f'SELECT COUNT(*) FROM ai."{t}"')
                count = cur.fetchone()[0]
                print(f"  ai.{t}: {count} rows")
            except Exception as e:
                print(f"  ai.{t}: ERROR - {e}")

print()

# Check if team_knowledge table exists and what columns it has
with psycopg.connect(pg_url) as conn:
    with conn.cursor() as cur:
        try:
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns
                WHERE table_schema = 'ai' AND table_name = 'team_knowledge'
                ORDER BY ordinal_position
            """)
            cols = cur.fetchall()
            if cols:
                print("team_knowledge columns:")
                for col_name, col_type in cols:
                    print(f"  {col_name}: {col_type}")
            else:
                print("team_knowledge table: NOT FOUND")
        except Exception as e:
            print(f"Error checking columns: {e}")

print("\n=== PgVector search_type check ===")
from db import create_knowledge
k = create_knowledge('Team Knowledge', 'team_knowledge')
print(f"Search type: {k.vector_db.search_type if k.vector_db else 'None'}")
print(f"Embedder: {k.vector_db.embedder if k.vector_db else 'None'}")

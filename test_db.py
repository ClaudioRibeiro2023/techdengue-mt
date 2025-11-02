import psycopg2

conn = psycopg2.connect('postgresql://techdengue:techdengue@localhost:5432/techdengue')
cur = conn.cursor()

# List tables
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
tables = cur.fetchall()

print("=== TABELAS NO BANCO ===")
for table in tables:
    print(f"  - {table[0]}")

# Check Flyway history
cur.execute("SELECT version, description, installed_on, success FROM flyway_schema_history ORDER BY installed_rank")
migrations = cur.fetchall()

print("\n=== MIGRAÇÕES FLYWAY ===")
for mig in migrations:
    status = "✅" if mig[3] else "❌"
    print(f"  {status} V{mig[0]} - {mig[1]} ({mig[2]})")

# Check hypertable
cur.execute("SELECT hypertable_name FROM timescaledb_information.hypertables")
hypertables = cur.fetchall()

print("\n=== HYPERTABLES TIMESCALEDB ===")
for ht in hypertables:
    print(f"  - {ht[0]}")

conn.close()
print("\n✅ Teste concluído!")

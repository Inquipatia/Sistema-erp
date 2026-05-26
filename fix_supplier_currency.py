import sqlite3

DB_NAME = "db.sqlite3"

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

# Ver columnas reales actuales de la tabla suppliers_supplier
columns = [row[1] for row in cur.execute("PRAGMA table_info(suppliers_supplier)").fetchall()]

print("Columns:", columns)

if "currency_id" in columns:
    print("Using column: currency_id")
    cur.execute("UPDATE suppliers_supplier SET currency_id = 1")
elif "currency" in columns:
    print("Using column: currency")
    cur.execute("UPDATE suppliers_supplier SET currency = 1")
else:
    raise Exception("No currency or currency_id column found in suppliers_supplier")

conn.commit()

print("Rows fixed:", cur.rowcount)

rows = cur.execute("SELECT id, id_supplier, name FROM suppliers_supplier").fetchall()
print("Suppliers:", rows)

conn.close()
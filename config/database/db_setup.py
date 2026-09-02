import sqlite3
import os

def init_db():
    # Ensure database folder exists
    os.makedirs('database', exist_ok=True)
    
    conn = sqlite3.connect('database/audit_engine.db')
    cursor = conn.cursor()

    # Table 1: Vendors
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendors (
            vendor_id TEXT PRIMARY KEY,
            vendor_name TEXT NOT NULL,
            service_type TEXT NOT NULL,
            handles_pii INTEGER NOT NULL,
            annual_contract_val REAL NOT NULL,
            has_soc2 INTEGER NOT NULL,
            risk_score INTEGER NOT NULL,
            risk_tier TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table 2: Audit Trail
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            vendor_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            actor TEXT NOT NULL,
            previous_state TEXT,
            new_state TEXT NOT NULL,
            rule_triggered TEXT,
            hash_signature TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully at database/audit_engine.db")

if __name__ == "__main__":
    init_db()
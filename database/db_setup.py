import sqlite3
import os
from pathlib import Path

def init_db():
    # Resolve project root and force creation of database directory
    project_root = Path(__file__).resolve().parent.parent
    db_dir = project_root / "database"
    os.makedirs(db_dir, exist_ok=True)
    
    db_path = db_dir / "audit_engine.db"
    
    conn = sqlite3.connect(str(db_path))
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
    print(f"Database initialized successfully at: {db_path}")

if __name__ == "__main__":
    init_db()

    
import sqlite3
import pandas as pd
from pathlib import Path

# Resolve database path
project_root = Path(__file__).resolve().parent
db_path = project_root / "database" / "audit_engine.db"
output_path = project_root / "EY_TPRM_Compliance_Audit_Report.xlsx"

def generate_excel_report():
    if not db_path.exists():
        print("Error: Database file not found. Please run the Streamlit app first.")
        return

    conn = sqlite3.connect(str(db_path))
    
    # Read tables
    df_vendors = pd.read_sql_query("SELECT * FROM vendors", conn)
    df_logs = pd.read_sql_query("SELECT * FROM audit_logs", conn)
    conn.close()

    # Write multi-tab formatted Excel sheet using openpyxl
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_vendors.to_excel(writer, sheet_name='Vendor Inventory', index=False)
        df_logs.to_excel(writer, sheet_name='Regulatory Audit Trail', index=False)

    print(f"Compliance Report exported successfully to: {output_path}")

if __name__ == "__main__":
    generate_excel_report()

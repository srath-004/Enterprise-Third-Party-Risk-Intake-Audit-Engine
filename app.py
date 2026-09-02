import sys
import os
from pathlib import Path

# Add project root and src folder to system path
project_root = Path(__file__).resolve().parent
src_path = project_root / "src"

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import streamlit as st
import pandas as pd
import sqlite3
import uuid
from src.risk_scorer import RiskScorer
from src.audit_logger import AuditLogger

# Ensure database exists automatically before running queries
DB_PATH = project_root / "database" / "audit_engine.db"

def check_db_initialized():
    if not DB_PATH.exists():
        from database.db_setup import init_db
        init_db()

check_db_initialized()

st.set_page_config(page_title="EY Risk Engine", layout="wide")

# ==========================================
# CUSTOM EY EXECUTIVE BANNER STYLING
# ==========================================
st.markdown("""
   <style>
    /* Global Background Adjustments */
    .stApp {
        background-color: #121217;
        color: #FFFFFF !important;
    }

    /* Force Table Text & Header Visibility */
    .stTable, div[data-testid="stTable"] table {
        background-color: #1A1A24 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    .stTable th, div[data-testid="stTable"] th {
        background-color: #2E2E38 !important;
        color: #FFE600 !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        border-bottom: 2px solid #3E3E4A !important;
    }
    .stTable td, div[data-testid="stTable"] td {
        color: #E0E0E6 !important;
        font-size: 13px !important;
        border-bottom: 1px solid #2E2E38 !important;
    }

    /* Force Streamlit Tab Text Visibility */
    button[data-baseweb="tab"] {
        color: #B0B0B8 !important;
        font-weight: 600 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FFE600 !important;
        border-bottom-color: #FFE600 !important;
    }

    /* Form Labels, Inputs & Headings */
    label, p, h1, h2, h3, h4, span {
        color: #FFFFFF !important;
    }

    /* Top Executive Navbar */
    .ey-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #1A1A24;
        padding: 14px 30px;
        border-bottom: 2px solid #2E2E38;
        margin-top: -60px;
        margin-bottom: 25px;
    }
    .ey-logo-text {
        font-size: 24px;
        font-weight: 900;
        color: #FFFFFF !important;
        letter-spacing: -1px;
    }
    .ey-logo-text span {
        color: #FFE600 !important;
    }
    .ey-tagline {
        font-size: 13px;
        color: #B0B0B8 !important;
        font-weight: 400;
    }

    /* Executive Hero Card Container */
    .ey-hero-card {
        background: linear-gradient(135deg, #0D232A 0%, #163C46 50%, #0F1B22 100%);
        border-radius: 12px;
        padding: 35px 40px;
        margin-bottom: 30px;
        border: 1px solid #234E59;
        box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.4);
    }
    
    /* Category Tag */
    .ey-category-tag {
        color: #FFE600 !important;
        font-size: 12px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 12px;
    }

    /* Main Title */
    .ey-hero-title {
        font-size: 30px;
        font-weight: 800;
        color: #FFFFFF !important;
        line-height: 1.25;
        margin-bottom: 16px;
    }

    /* Subtitle with Left Border Callout */
    .ey-callout-box {
        border-left: 3px solid #FFE600;
        padding-left: 15px;
        color: #E0E0E6 !important;
        font-size: 15px;
        line-height: 1.5;
        font-weight: 400;
    }
    </style>

    <!-- Top Navbar -->
    <div class="ey-navbar">
        <div>
            <span class="ey-logo-text">EY<span>/</span></span>
            <span class="ey-tagline" style="margin-left: 10px;">Shape the future with confidence</span>
        </div>
        <div class="ey-tagline">Third-Party Risk Engine</div>
    </div>

    <!-- Hero Card Banner -->
    <div class="ey-hero-card">
        <div class="ey-category-tag">ENTERPRISE RISK INSIGHTS</div>
        <div class="ey-hero-title">How will automated governance quantify risks not yet imagined?</div>
        <div class="ey-callout-box">
            Continuous third-party evaluation, SHA-256 cryptographic audit logs, and instant policy compliance scorecards built for modern enterprise ecosystems.
        </div>
    </div>
""", unsafe_allow_html=True)

scorer = RiskScorer()
logger = AuditLogger()

tab1, tab2, tab3 = st.tabs(["Vendor Intake Form", "Vendor Registry", "Audit Trail Logs"])

# TAB 1: INTAKE FORM
with tab1:
    st.subheader("Submit New Third-Party Vendor for Intake")
    with st.form("intake_form"):
        v_name = st.text_input("Vendor Company Name")
        s_type = st.selectbox("Service Category", ["Cloud Infrastructure", "HR/Payroll", "Consulting", "Software SaaS"])
        pii = st.checkbox("Vendor handles Personally Identifiable Information (PII)?")
        soc2 = st.checkbox("Vendor holds valid SOC 2 Type II Certification?")
        contract_val = st.number_input("Annual Contract Value ($ USD)", min_value=1000, value=50000)
        
        submitted = st.form_submit_button("Submit & Evaluate Risk")

    if submitted and v_name:
        vendor_id = f"VEN-{uuid.uuid4().hex[:6].upper()}"
        input_data = {
            "handles_pii": pii,
            "has_soc2": soc2,
            "annual_contract_val": contract_val
        }
        
        res = scorer.calculate_risk(input_data)
        
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute('''
            INSERT INTO vendors (vendor_id, vendor_name, service_type, handles_pii, annual_contract_val, has_soc2, risk_score, risk_tier, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (vendor_id, v_name, s_type, int(pii), contract_val, int(soc2), res['risk_score'], res['risk_tier'], res['status']))
        conn.commit()
        conn.close()

        logger.log_event(
            vendor_id=vendor_id,
            action_type="VENDOR_INTAKE_EVALUATION",
            actor="SYSTEM_AUTOMATION",
            new_state={"risk_score": res['risk_score'], "status": res['status']},
            rule_triggered=",".join(res['rules_flagged'])
        )

        st.success(f"Vendor Processed! Assigned ID: **{vendor_id}**")
        st.metric(label="Calculated Risk Score", value=res['risk_score'])
        st.info(f"Risk Tier: **{res['risk_tier']}** | Decision Status: **{res['status']}**")

# TAB 2: VENDOR REGISTRY
with tab2:
    st.subheader("Active Third-Party Inventory")
    conn = sqlite3.connect(str(DB_PATH))
    df_vendors = pd.read_sql_query("SELECT * FROM vendors ORDER BY created_at DESC", conn)
    conn.close()
    
    if not df_vendors.empty:
        st.table(df_vendors)
    else:
        st.info("No vendors currently registered.")

# TAB 3: AUDIT TRAIL
with tab3:
    st.subheader("Immutable Audit Logs (Regulatory Evidence)")
    conn = sqlite3.connect(str(DB_PATH))
    df_logs = pd.read_sql_query("SELECT * FROM audit_logs ORDER BY timestamp DESC", conn)
    conn.close()
    
    if not df_logs.empty:
        st.table(df_logs)
    else:
        st.info("No audit logs available.")
        # TAB 3: AUDIT TRAIL
with tab3:
    st.subheader("Immutable Audit Logs (Regulatory Evidence)")
    conn = sqlite3.connect(str(DB_PATH))
    df_logs = pd.read_sql_query("SELECT * FROM audit_logs ORDER BY timestamp DESC", conn)
    df_vendors = pd.read_sql_query("SELECT * FROM vendors ORDER BY created_at DESC", conn)
    conn.close()
    
    if not df_logs.empty:
        st.table(df_logs)
        
        # Add Excel Download Button
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_vendors.to_excel(writer, sheet_name='Vendor Inventory', index=False)
            df_logs.to_excel(writer, sheet_name='Regulatory Audit Trail', index=False)
            
        st.download_button(
            label="Download EY Compliance Excel Report",
            data=buffer.getvalue(),
            file_name="EY_TPRM_Compliance_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No audit logs available.")

        # Summary KPI Row
conn = sqlite3.connect(str(DB_PATH))
total_vendors = pd.read_sql_query("SELECT COUNT(*) as count FROM vendors", conn)['count'][0]
high_risk_vendors = pd.read_sql_query("SELECT COUNT(*) as count FROM vendors WHERE risk_tier='HIGH'", conn)['count'][0]
total_logs = pd.read_sql_query("SELECT COUNT(*) as count FROM audit_logs", conn)['count'][0]
conn.close()

col1, col2, col3 = st.columns(3)
col1.metric("Total Vendors Onboarded", total_vendors)
col2.metric("High Risk Flags", high_risk_vendors, delta_color="inverse")
col3.metric("Immutable Audit Records", total_logs)

st.markdown("<br>", unsafe_allow_html=True)
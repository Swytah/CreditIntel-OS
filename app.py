import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
import hashlib
import os
import requests  # Clean REST connectivity for production scale API pipelines
from dotenv import load_dotenv

# --- FORCE DOTENV TO SEARCH CAREFULLY ---
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(dotenv_path=env_path, override=True)
load_dotenv()

# --- 1. GLOBAL SYSTEM SETUP & PREMIUM THEME ---
st.set_page_config(
    page_title="CreditIntel OS — Financial Suite",
    page_icon="💳",
    layout="wide"
)

# Fetching the Gemini API Key securely from environmental states
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- UI/UX CSS RE-ENGINEERING FOR TEXT READABILITY ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600;700;800&display=swap');
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', sans-serif;
            background-color: #FAFAFA;
        }
        [data-testid="stSidebar"] {
            background-color: #0F172A !important;
            color: #F8FAFC !important;
            border-right: 1px solid #1E293B;
        }
        [data-testid="stSidebar"] *, [data-testid="stSidebar"] p {
            color: #F8FAFC !important;
        }
        
        /* 🎨 DYNAMIC FIX: High readability text-box engine for typing inputs clearly */
        div[data-testid="stSidebarUserContent"] div.stTextInput input {
            color: #0F172A !important; /* Rich deep corporate black text while typing */
            background-color: #FFFFFF !important; /* Pure white background block */
            border: 1px solid #334155 !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
        }
        
        div.stButton > button {
            background-color: #2563EB !important;
            color: #FFFFFF !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            border: none !important;
            padding: 10px 24px !important;
        }
        div.stButton > button:hover {
            background-color: #1D4ED8 !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 2. SECURITY & HASHING ENGINE ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_password):
    if make_hashes(password) == hashed_password:
        return True
    return False

# --- 3. LOCAL SQLITE DATABASE INITIALIZATION ---
DB_FILE = "system_users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            logged_by TEXT,
            applicant_name TEXT,
            employment_type TEXT,
            annual_income REAL,
            requested_loan REAL,
            cibil_score INTEGER,
            risk_score INTEGER,
            verdict TEXT
        )
        """
    )
    conn.commit()
    conn.close()

init_db()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""


# --- 4. AUTHENTICATION ENGINE (SIGN UP & LOGIN) ---
if not st.session_state.authenticated:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.4, 1])
    
    with col_b:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 24px;">
                <span style="font-size: 32px;">💳</span>
                <h2 style="margin: 10px 0 0 0; font-weight: 800; color: #0F172A;">CreditIntel OS</h2>
                <p style="color: #64748B; font-size: 14px;">Enterprise Gateway & Risk Portal</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        auth_mode = st.tabs(["🔒 Secure Login", "📝 Create New Account (Sign Up)"])
        
        with auth_mode[0]:
            with st.form("login_form"):
                login_user = st.text_input("Username / Registered Email").strip()
                login_pass = st.text_input("Password", type="password")
                btn_login = st.form_submit_button("Authenticate Access", use_container_width=True)
                
                if btn_login:
                    if login_user == "" or login_pass == "":
                        st.error("Fields cannot be empty.")
                    else:
                        conn = sqlite3.connect(DB_FILE)
                        cursor = conn.cursor()
                        cursor.execute("SELECT password FROM users WHERE username = ?", (login_user,))
                        result = cursor.fetchone()
                        conn.close()
                        
                        if result and check_hashes(login_pass, result[0]):
                            st.session_state.authenticated = True
                            st.session_state.current_user = login_user
                            st.success("Access Granted! Loading parameters...")
                            st.rerun()
                        else:
                            st.error("Invalid Username or Password.")
                            
        with auth_mode[1]:
            with st.form("signup_form"):
                new_user = st.text_input("Choose Username / Email").strip()
                new_pass = st.text_input("Choose Strong Password", type="password")
                confirm_pass = st.text_input("Confirm Password", type="password")
                btn_signup = st.form_submit_button("Register & Initialize Account", use_container_width=True)
                
                if btn_signup:
                    if new_user == "" or new_pass == "":
                        st.error("Please fill in all mandatory fields.")
                    elif new_pass != confirm_pass:
                        st.error("Passwords do not match!")
                    else:
                        try:
                            hashed_register_password = make_hashes(new_pass)
                            conn = sqlite3.connect(DB_FILE)
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_user, hashed_register_password))
                            conn.commit()
                            conn.close()
                            st.success("🎉 Account created securely! Switch to the Login tab to access.")
                        except sqlite3.IntegrityError:
                            st.error("This username already exists.")
    st.stop()


# --- 5. SECURE DASHBOARD WORKSPACE ---
clean_display_name = st.session_state.current_user.split('@')[0]

st.sidebar.markdown(
    f"""
    <div style="padding: 15px 0px; border-bottom: 1px solid #334155; margin-bottom: 20px;">
        <h3 style="font-size: 16px; margin: 0; color: #F8FAFC;">💳 CREDITINTEL OS</h3>
        <p style="font-size: 11px; color: #10B981; margin: 4px 0 0 0;">● LIVE CONNECTION SECURED</p>
        <p style="font-size: 12px; color: #94A3B8; margin: 2px 0 0 0;">User: <b>{clean_display_name}</b></p>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.subheader("Navigation")
st.sidebar.info("📊 Underwriting Simulation Node Active")
st.sidebar.markdown("<br>", unsafe_allow_html=True)


# --- MAIN SCREEN INTERFACE ARCHITECTURE ---
st.markdown("<h2 style='color:#0F172A; font-weight:800; font-size:30px; letter-spacing:-0.5px;'>Credit Risk Evaluation Terminal</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748B; font-size:14px; margin-top:-10px;'>Simulate credit applications, test data indices, and analyze predictive decision models instantly.</p>", unsafe_allow_html=True)
st.markdown("<hr style='border-top:1px solid #E2E8F0; margin-bottom:24px;' />", unsafe_allow_html=True)

st.markdown("### 🛠️ Live Simulation Controls")
box1, box2, box3 = st.columns(3)

with box1:
    applicant_name = st.text_input("Applicant Full Name", value="Sweta Nath")
    employment = st.selectbox("Job Risk Category Pool", ["Salaried", "Self-Employed", "Unemployed"])
with box2:
    income = st.number_input("Annual Gross Income (₹)", min_value=100000, value=1200000, step=50000)
    loan_amount = st.number_input("Requested Credit Exposure Limit (₹)", min_value=10000, value=350000, step=25000)
with box3:
    cibil = st.slider("Bureau Track Score Index (CIBIL)", min_value=300, max_value=900, value=534)
    age = st.slider("Applicant Demographic Age Profile", min_value=18, max_value=80, value=25)


# Automated Core Risk Calculations Matrix
dti_ratio = (loan_amount / income) if income > 0 else 0
reliability_index = 100
risk_justifications = []

if cibil < 600:
    reliability_index -= 40
    risk_justifications.append("🚨 <b>Bureau Severity:</b> CIBIL index signals dangerous default behavior history.")
elif cibil < 750:
    reliability_index -= 15
    risk_justifications.append("⚠️ <b>Moderate Score Clearance:</b> Slight repayment variance noted over previous settlement windows.")

if dti_ratio > 0.5:
    reliability_index -= 30
    risk_justifications.append("🚨 <b>Over-Leveraged:</b> Principal allocation limits are dangerously wide for current income brackets.")
elif dti_ratio > 0.3:
    risk_justifications.append("⚠️ <b>Elevated Leverage Profile:</b> Operational savings buffer is compressed under ongoing debt loads.")

if employment == "Unemployed":
    reliability_index -= 50
    risk_justifications.append("🚨 <b>Zero Liquid Stream:</b> Zero incoming income tracks represent a high direct default risk.")

reliability_index = max(0, min(100, reliability_index))

if reliability_index >= 75:
    status, status_color, status_bracket = "APPROVED", "#10B981", "Low Core Risk Profile"
elif reliability_index >= 45:
    status, status_color, status_bracket = "UNDER REVIEW", "#F59E0B", "Medium Tier Variance Profile"
else:
    status, status_color, status_bracket = "REJECTED", "#EF4444", "High Volatility Bracket Profile"


# --- 🤖 SIDEBAR HYBRID AI CHATBOT NODE (PRODUCTION INFRASTRUCTURE) ---
st.sidebar.markdown("<h4 style='color: #F8FAFC; margin-bottom: 5px;'>🤖 AI Assistant Copilot</h4>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-size: 12px; color: #94A3B8; margin-top: 0;'>Ask context underwriting or policy routing questions:</p>", unsafe_allow_html=True)

user_chat_query = st.sidebar.text_input("Query Terminal Input Box", placeholder="Type here...", label_visibility="collapsed")

if user_chat_query:
    if not GEMINI_API_KEY or GEMINI_API_KEY.startswith("AIzaSy...Your"):
        st.sidebar.error("Set a valid GEMINI_API_KEY string key inside your config root .env layer.")
    else:
        with st.sidebar.spinner("Processing Model Node Query..."):
            try:
                # Upstream Gateway target initialization
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
                headers = {'Content-Type': 'application/json'}
                
                # Dynamic Parameter injection framing core application states directly into context layer
                system_instruction = (
                    f"You are an elite financial banking risk officer assistant. "
                    f"Context: Applicant '{applicant_name}' ({employment}), Income: ₹{income:,}, Loan Request: ₹{loan_amount:,}, "
                    f"CIBIL: {cibil}, Risk score: {reliability_index}/100, Automated verdict: {status}. "
                    f"Answer the user's banking query concisely in 2-3 structured clear bullet sentences."
                )
                
                payload = {
                    "contents": [{
                        "parts": [{"text": f"{system_instruction}\nUser Query: {user_chat_query}"}]
                    }],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": 200
                    }
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=8)
                response_json = response.json()
                
                # Check 1: API Token Response Validation
                if response.status_code == 200 and 'candidates' in response_json:
                    ai_reply = response_json['candidates'][0]['content']['parts'][0]['text']
                    st.sidebar.markdown(
                        f"""
                        <div style="background-color: #1E293B; padding: 12px; border-radius: 8px; font-size: 13px; color: #F1F5F9; border: 1px solid #334155; margin-top: 10px;">
                            💡 <b>Gemini Production Instance:</b><br>{ai_reply}
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                
                # Check 2: Automated Failover Strategy Engine triggered if system detects Quota limits depletion
                elif response.status_code == 429 or response_json.get('error', {}).get('status') == 'RESOURCE_EXHAUSTED':
                    query_lower = user_chat_query.lower()
                    
                    if "cibil" in query_lower or "score" in query_lower:
                        fallback_reply = f"System routing note for applicant {applicant_name}: The evaluated bureau profile states a {cibil} score index. Deleveraging short credit facilities is necessary to shift out of high portfolio risk margins."
                    elif "approve" in query_lower or "verdict" in query_lower:
                        fallback_reply = f"The automated engine structural matrix has locked the application status as {status} based on safety index evaluations of {reliability_index}/100."
                    else:
                        fallback_reply = f"Fintech Ledger Flag: Credit framework parameters tracking metrics render a risk stability profile index of {reliability_index}/100 for this {employment} application entry."
                    
                    st.sidebar.markdown(
                        f"""
                        <div style="background-color: #1E293B; padding: 12px; border-radius: 8px; font-size: 13px; color: #F59E0B; border: 1px solid #D97706; margin-top: 10px;">
                            ⚠️ <b>Policy Node (Fallback Mode):</b><br>{fallback_reply}<br><br>
                            <span style="font-size:10px; color:#FCD34D;">[Notice: Cloud API Quota Limit reached. Serving deterministic banking rules layer.]</span>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                else:
                    srv_error = response_json.get('error', {}).get('message', 'Unknown Infrastructure Breakpoint Node.')
                    st.sidebar.error(f"Gateway Gateway Error Code {response.status_code}: {srv_error}")
                    
            except Exception as e:
                st.sidebar.error(f"Orchestration Routing Failure: {str(e)}")

st.sidebar.markdown("<br><hr style='border-top:1px solid #334155;' />", unsafe_allow_html=True)

if st.sidebar.button("Log Out of Session", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.current_user = ""
    st.rerun()


# --- LAYOUT PRESENTATION RENDERING ---
st.markdown("<br>", unsafe_allow_html=True)
layout_left, layout_right = st.columns([1.1, 0.9])

with layout_left:
    st.markdown(
        f"""
        <div style="background-color: #FFFFFF; padding: 25px; border-radius: 12px; border-left: 8px solid {status_color}; border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;">
            <p style="margin: 0; font-size: 12px; color: #64748B; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Automated Credit Verdict</p>
            <h1 style="margin: 6px 0; color: {status_color}; font-weight: 800; font-size: 36px;">{status}</h1>
            <p style="margin: 0; font-size: 14px; color: #334155;">Risk Segment Tier: <b>{status_bracket}</b></p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.markdown("<br><h4 style='color:#0F172A; font-weight:700;'>📋 Audit Flag Breakdown Analysis</h4>", unsafe_allow_html=True)
    if not risk_justifications:
        st.success("✅ **Optimal Risk Compliance:** Parameters strictly match safety metrics.")
    else:
        for alert in risk_justifications:
            st.markdown(f"<div style='background:#F8FAFC; padding:12px; border-radius:8px; margin-bottom:8px; border:1px solid #E2E8F0; font-size:14px; color:#1E293B;'>{alert}</div>", unsafe_allow_html=True)

with layout_right:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=reliability_index,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Calculated Reliability Score Index", 'font': {'size': 14, 'color': '#64748B'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#CBD5E1"},
            'bar': {'color': "#0F172A"},
            'steps': [
                {'range': [0, 45], 'color': "#FEE2E2"},
                {'range': [45, 75], 'color': "#FEF3C7"},
                {'range': [75, 100], 'color': "#D1FAE5"}
            ],
            'threshold': {
                'line': {'color': status_color, 'width': 4},
                'thickness': 0.75,
                'value': reliability_index
            }
        }
    ))
    fig.update_layout(height=230, margin=dict(l=20, r=20, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# Record Archival Hub
st.markdown("<br><hr style='border-top:1px solid #E2E8F0;' />", unsafe_allow_html=True)
st.markdown("### 💾 Record Archival Hub")

if st.button("Commit Current Simulation to SQLite DB"):
    if applicant_name.strip() == "":
        st.warning("Please provide a valid Applicant Name before saving.")
    else:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO applications (logged_by, applicant_name, employment_type, annual_income, requested_loan, cibil_score, risk_score, verdict)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (clean_display_name, applicant_name, employment, income, loan_amount, cibil, reliability_index, status)
        )
        conn.commit()
        conn.close()
        st.success(f"🎉 Success! Record for '{applicant_name}' has been safely archived.")

# Historical Data Audit Rail View
st.markdown("<br><h4>📜 Historical Evaluation Registry (Real-Time Database Fetch)</h4>", unsafe_allow_html=True)

conn = sqlite3.connect(DB_FILE)
history_df = pd.read_sql_query("SELECT id, logged_by, applicant_name, employment_type, annual_income, requested_loan, cibil_score, risk_score, verdict FROM applications ORDER BY id DESC", conn)
conn.close()

if history_df.empty:
    st.info("No records archived yet.")
else:
    history_df.columns = ["Record ID", "Logged By PM", "Applicant Name", "Employment", "Income (₹)", "Loan Request (₹)", "CIBIL Score", "Reliability Index", "Verdict"]
    st.dataframe(history_df, use_container_width=True, hide_index=True)
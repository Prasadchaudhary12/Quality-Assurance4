import streamlit as st
import pandas as pd
import datetime

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Internal Audit QA Tool", layout="wide")

st.markdown("""
<style>
html, body {
    font-family: Calibri;
}
.stApp {
    background-color: #f2f2f2;
}
.stButton>button {
    background-color: #f1c40f;
    color: black;
    border-radius: 6px;
    font-weight:bold;
}
.sidebar .sidebar-content {
    background-color: #222;
}
</style>
""", unsafe_allow_html=True)

# -------------------- SESSION INIT --------------------
def init():
    defaults = {
        "users": {"admin":"admin"},
        "login": False,
        "user": "",
        "clients": [],
        "engagements": [],
        "qa": [],
        "logs": [],
        "archive": []
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k]=v

init()

def log(action):
    st.session_state.logs.append({
        "user": st.session_state.user,
        "action": action,
        "time": datetime.datetime.now()
    })

# -------------------- LOGIN --------------------
def login():
    st.title("🔐 Internal Audit QA Tool")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in st.session_state.users and st.session_state.users[u] == p:
            st.session_state.login = True
            st.session_state.user = u
            log("Login")
            st.rerun()
        else:
            st.error("Invalid credentials")

# -------------------- DASHBOARD --------------------
def dashboard():
    st.title("📊 Dashboard")

    df = pd.DataFrame(st.session_state.qa)

    total = len(df)
    pass_c = len(df[df.result=="Pass"]) if not df.empty else 0
    fail_c = len(df[df.result=="Fail"]) if not df.empty else 0

    completed = total
    inprogress = 0
    not_started = max(0, len(st.session_state.engagements) - completed)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total QA", total)
    c2.metric("Completed", completed)
    c3.metric("In Progress", inprogress)
    c4.metric("Not Started", not_started)

    st.progress(completed/(len(st.session_state.engagements)+1))

    st.success(f"✅ Pass: {pass_c}")
    st.error(f"❌ Fail: {fail_c}")

# -------------------- CLIENT --------------------
def create_client():
    st.title("🏢 Create Client")

    name = st.text_input("Client Name")

    if st.button("Save Client") and name:
        st.session_state.clients.append(name)
        log(f"Client created {name}")
        st.success("Client Created")

# -------------------- ENGAGEMENT --------------------
def create_engagement():
    st.title("📁 Create Engagement")

    if not st.session_state.clients:
        st.warning("Create client first")
        return

    client = st.selectbox("Client", st.session_state.clients)
    fy = st.text_input("Financial Year")
    process = st.text_input("Audit Process")
    auditor = st.text_input("Auditor Name")
    auditee = st.text_input("Auditee Name")
    dept = st.text_input("Department")
    title = st.text_input("Title")

    if st.button("Create Engagement"):
        st.session_state.engagements.append({
            "id": len(st.session_state.engagements),
            "client": client,
            "fy": fy,
            "process": process,
            "auditor": auditor,
            "auditee": auditee,
            "dept": dept,
            "title": title,
            "signed_off": False
        })
        log("Engagement Created")
        st.success("Engagement Created")

# -------------------- CHECKLIST --------------------
CHECKLIST = [
    "Planning",
    "Risk Assessment",
    "Control Testing",
    "Evidence Review",
    "Conclusion"
]

MANDATORY = [
    "Scoping Memo",
    "Audit Report",
    "RCM",
    "Audit Program",
    "Workpapers",
    "Evidence"
]

def checklist():
    st.title("✅ QA Checklist")

    if not st.session_state.engagements:
        st.warning("Create engagement first")
        return

    eng = st.selectbox(
        "Select Engagement",
        st.session_state.engagements,
        format_func=lambda x: f"{x['client']} - {x['process']}"
    )

    st.subheader("📎 Mandatory Documents")
    for doc in MANDATORY:
        st.file_uploader(doc, key=f"{eng['id']}_{doc}")

    st.divider()

    for step in CHECKLIST:
        st.subheader(f"🔹 {step}")

        st.file_uploader("Upload Evidence", key=f"{eng['id']}_{step}")

        remarks = st.text_area("Remarks / Justification", key=f"{eng['id']}_{step}_r")

        col1,col2,col3 = st.columns(3)

        if col1.button("✔ Pass", key=f"{eng['id']}_{step}_p"):
            save(step,"Pass",remarks)

        if col2.button("❌ Fail", key=f"{eng['id']}_{step}_f"):
            save(step,"Fail",remarks)

        if col3.button("N/A", key=f"{eng['id']}_{step}_na"):
            save(step,"NA",remarks)

        if st.button("💬 Chat Assist", key=f"{eng['id']}_{step}_chat"):
            st.info("Suggestion: Improve control documentation and validation.")

    # SIGN OFF
    st.divider()
    if st.button("✅ Sign-off QA (Human Review)"):
        eng["signed_off"] = True
        log("QA Signed Off")
        st.success("Signed-off completed ✅")

# -------------------- SAVE --------------------
def save(step, result, remarks):
    st.session_state.qa.append({
        "step": step,
        "result": result,
        "remarks": remarks,
        "user": st.session_state.user,
        "time": datetime.datetime.now()
    })
    log(f"{step} {result}")
    st.success("Saved")

# -------------------- REPORT --------------------
def report():
    st.title("📄 Final Report")

    df = pd.DataFrame(st.session_state.qa)

    st.dataframe(df)

    st.download_button("📥 Export Excel", df.to_csv(index=False), "QA_Report.csv")

    if st.button("💬 Refine Report"):
        st.info("AI Suggestion: Improve executive summary and findings clarity.")

# -------------------- LOGS --------------------
def logs():
    st.title("📜 Audit Logs")
    st.dataframe(pd.DataFrame(st.session_state.logs))

# -------------------- ARCHIVE --------------------
def archive():
    st.title("📦 Archive")

    if st.button("Archive Data"):
        st.session_state.archive.append(st.session_state.qa)
        st.session_state.qa = []
        log("Archived QA Data")
        st.success("Archived Successfully")

# -------------------- MAIN --------------------
if not st.session_state.login:
    login()
else:
    st.sidebar.title("🚆 QA System Menu")
    st.sidebar.write(f"👤 {st.session_state.user}")

    if st.sidebar.button("🚪 Logout"):
        log("Logout")
        st.session_state.login = False
        st.session_state.user = ""
        st.rerun()

    menu = st.sidebar.radio("Navigate", [
        "Home",
        "Dashboard",
        "Create Client",
        "Create Engagement",
        "Checklist",
        "Report",
        "Logs",
        "Archive"
    ])

    if menu == "Home":
        st.title("🏠 QA Portal Home")
        st.info("Structured workflow system similar to enterprise tools.")

    elif menu == "Dashboard":
        dashboard()

    elif menu == "Create Client":
        create_client()

    elif menu == "Create Engagement":
        create_engagement()

    elif menu == "Checklist":
        checklist()

    elif menu == "Report":
        report()

    elif menu == "Logs":
        logs()

    elif menu == "Archive":
        archive()

import streamlit as st
import pandas as pd
import datetime

# ---------------- UI CONFIG ----------------
st.set_page_config(page_title="QA Tool", layout="wide")

st.markdown("""
<style>
html, body {
    font-family: Calibri;
}
.stApp {
    background-color: #f4f4f4;
}
.main-header {
    background-color: #222;
    color: white;
    padding: 12px;
    border-radius: 5px;
}
.stButton>button {
    background-color: #f1c40f;
    color: black;
    border-radius: 6px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION INIT ----------------
def init():
    keys = {
        "users":{"admin":"admin"},
        "login":False,
        "user":"",
        "clients":[],
        "eng":[],
        "qa":[],
        "logs":[],
        "archive":[]
    }
    for k,v in keys.items():
        if k not in st.session_state:
            st.session_state[k]=v

init()

def log(action):
    st.session_state.logs.append({
        "User":st.session_state.user,
        "Action":action,
        "Time":datetime.datetime.now()
    })

# ---------------- LOGIN ----------------
def login():
    st.markdown("<div class='main-header'><h2>🔐 Internal Audit QA Tool</h2></div>", unsafe_allow_html=True)

    u=st.text_input("Username")
    p=st.text_input("Password", type="password")

    if st.button("Login"):
        if u in st.session_state.users and st.session_state.users[u]==p:
            st.session_state.login=True
            st.session_state.user=u
            log("Login")
            st.rerun()
        else:
            st.error("Invalid credentials")

# ---------------- HEADER ----------------
def header():
    col1, col2 = st.columns([8,2])

    col1.markdown("<div class='main-header'><h3>🚆 Internal Audit QA System</h3></div>", unsafe_allow_html=True)

    with col2:
        st.write(f"👤 {st.session_state.user}")
        if st.button("Logout"):
            log("Logout")
            st.session_state.login=False
            st.session_state.user=""
            st.rerun()

# ---------------- DASHBOARD ----------------
def dashboard():
    st.subheader("📊 Dashboard")

    df=pd.DataFrame(st.session_state.qa)

    total=len(df)
    pass_c=len(df[df.result=="Pass"]) if not df.empty else 0
    fail_c=len(df[df.result=="Fail"]) if not df.empty else 0

    completed=total
    inprogress=0
    notstarted=max(0,len(st.session_state.eng)-total)

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Total QA", total)
    c2.metric("Completed", completed)
    c3.metric("In Progress", inprogress)
    c4.metric("Not Started", notstarted)

    st.progress(completed/(len(st.session_state.eng)+1))

    st.success(f"✅ Pass: {pass_c}")
    st.error(f"❌ Fail: {fail_c}")

# ---------------- CLIENT ----------------
def client():
    st.subheader("🏢 Create Client")

    name=st.text_input("Client Name")

    if st.button("Add Client") and name:
        st.session_state.clients.append(name)
        log("Client added")
        st.success("Client Created")

# ---------------- ENGAGEMENT ----------------
def engagement():
    st.subheader("📁 Create Engagement")

    if not st.session_state.clients:
        st.warning("Create client first")
        return

    client=st.selectbox("Client",st.session_state.clients)
    fy=st.text_input("Financial Year")
    process=st.text_input("Audit Process")
    auditor=st.text_input("Auditor")
    auditee=st.text_input("Auditee")
    dept=st.text_input("Department")
    title=st.text_input("Title")

    if st.button("Create Engagement"):
        st.session_state.eng.append({
            "id":len(st.session_state.eng),
            "client":client,
            "process":process,
            "fy":fy,
            "signed":False
        })
        log("Eng created")
        st.success("Created")

# ---------------- CHECKLIST ----------------
CHECKLIST=["Planning","Risk Assessment","Control Testing","Evidence","Conclusion"]
DOCS=["Scoping Memo","Audit Report","RCM","Audit Program","Workpapers","Evidence"]

def checklist():
    st.subheader("✅ QA Checklist")

    if not st.session_state.eng:
        st.warning("Create engagement first")
        return

    e=st.selectbox(
        "Select Engagement",
        st.session_state.eng,
        format_func=lambda x:f"{x['client']} | {x['process']}"
    )

    st.markdown("### 📎 Mandatory Documents")
    for d in DOCS:
        st.file_uploader(d, key=f"{e['id']}_{d}")

    st.divider()

    for step in CHECKLIST:
        st.markdown(f"### 🔹 {step}")

        st.file_uploader("Upload Evidence", key=f"{e['id']}{step}")

        remark=st.text_area("Remarks", key=f"{e['id']}{step}r")

        col1,col2,col3=st.columns(3)

        if col1.button("✔ Pass",key=f"{e['id']}{step}p"):
            save(step,"Pass",remark)

        if col2.button("❌ Fail",key=f"{e['id']}{step}f"):
            save(step,"Fail",remark)

        if col3.button("N/A",key=f"{e['id']}{step}n"):
            save(step,"NA",remark)

        if st.button("💬 Improve Step",key=f"{e['id']}{step}chat"):
            st.info("Suggestion: Enhance documentation and control rationale.")

    if st.button("✅ Human Sign‑off"):
        e["signed"]=True
        log("Signed off")
        st.success("QA Signed Off")

def save(step,res,remark):
    st.session_state.qa.append({
        "step":step,
        "result":res,
        "remark":remark,
        "user":st.session_state.user,
        "time":datetime.datetime.now()
    })
    log(f"{step}-{res}")
    st.success("Saved")

# ---------------- REPORT ----------------
def report():
    st.subheader("📄 Final Report")

    df=pd.DataFrame(st.session_state.qa)
    st.dataframe(df)

    st.download_button("📥 Export Excel",df.to_csv(index=False),"QA_Report.csv")

    if st.button("💬 Improve Report"):
        st.info("Suggestion: Improve executive summary.")

# ---------------- LOGS ----------------
def logs():
    st.subheader("📜 Audit Logs")
    st.dataframe(pd.DataFrame(st.session_state.logs))

# ---------------- ARCHIVE ----------------
def archive():
    st.subheader("📦 Archive")

    if st.button("Archive All"):
        st.session_state.archive.append(st.session_state.qa)
        st.session_state.qa=[]
        log("Archived")
        st.success("Archived")

# ---------------- MAIN ----------------
if not st.session_state.login:
    login()
else:
    header()

    # ✅ MAIN DROPDOWN MENU
    menu = st.selectbox("Navigate", [
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
        st.title("🏠 Home")
        st.info("Structured QA system similar to enterprise workflow tools.")

    elif menu == "Dashboard":
        dashboard()

    elif menu == "Create Client":
        client()

    elif menu == "Create Engagement":
        engagement()

    elif menu == "Checklist":
        checklist()

    elif menu == "Report":
        report()

    elif menu == "Logs":
        logs()

    elif menu == "Archive":
        archive()

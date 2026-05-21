import streamlit as st
import pandas as pd
import datetime

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Internal Audit QA Tool", layout="wide")

# ------------------ STYLING ------------------
st.markdown("""
<style>
html, body {
    font-family: Calibri;
}
.stApp {
    background-color: #f2f2f2;
}

/* Header */
.header {
    background-color: #222;
    color: white;
    padding: 15px;
    border-radius: 6px;
    text-align: center;
}

/* Login box */
.login-box {
    border: 2px solid #f1c40f;
    padding: 25px;
    border-radius: 10px;
    background-color: white;
}

/* Buttons */
.stButton>button {
    background-color: #f1c40f;
    color: black;
    font-weight: bold;
    border-radius: 6px;
}

/* sections */
.section {
    padding: 15px;
    background-color: white;
    border-radius: 8px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ------------------ SESSION ------------------
def init():
    keys={
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
        "user":st.session_state.user,
        "action":action,
        "time":datetime.datetime.now()
    })

# ------------------ LOGIN ------------------
def login():
    st.markdown("<h2 class='header'>Internal Audit QA System</h2>", unsafe_allow_html=True)

    st.write("")

    col1,col2,col3=st.columns([2,2,2])

    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)

        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("🔐 Login", use_container_width=True):
            if u in st.session_state.users and st.session_state.users[u]==p:
                st.session_state.login=True
                st.session_state.user=u
                log("Login")
                st.rerun()
            else:
                st.error("Invalid credentials")

        st.markdown("</div>", unsafe_allow_html=True)

# ------------------ HEADER ------------------
def header():
    col1,col2=st.columns([8,2])

    col1.markdown("<h3 class='header'>🚆 Internal Audit QA Tool</h3>", unsafe_allow_html=True)

    with col2:
        st.write(f"👤 {st.session_state.user}")
        if st.button("Logout"):
            log("Logout")
            st.session_state.login=False
            st.rerun()

# ------------------ DASHBOARD ------------------
def dashboard():
    st.markdown("<div class='section'>", unsafe_allow_html=True)

    st.subheader("📊 Dashboard Overview")

    df=pd.DataFrame(st.session_state.qa)

    total=len(df)
    pass_c=len(df[df.result=="Pass"]) if not df.empty else 0
    fail_c=len(df[df.result=="Fail"]) if not df.empty else 0

    col1,col2,col3,col4=st.columns(4)
    col1.metric("Total QA", total)
    col2.metric("Completed", total)
    col3.metric("Pass", pass_c)
    col4.metric("Fail", fail_c)

    st.divider()

    # Chart without external lib
    if total > 0:
        chart_data = pd.DataFrame({
            "Category":["Pass","Fail","N/A"],
            "Count":[
                pass_c,
                fail_c,
                total - pass_c - fail_c
            ]
        })
        st.bar_chart(chart_data.set_index("Category"))

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ CLIENT ------------------
def client():
    st.markdown("<div class='section'>", unsafe_allow_html=True)

    st.subheader("🏢 Client Management")

    name=st.text_input("Client Name")

    if st.button("Add Client") and name:
        st.session_state.clients.append(name)
        log("Client Added")
        st.success("✅ Client Added")

    st.dataframe(pd.DataFrame(st.session_state.clients, columns=["Clients"]))

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ ENGAGEMENT ------------------
def engagement():
    st.markdown("<div class='section'>", unsafe_allow_html=True)

    st.subheader("📁 Engagement Setup")

    if not st.session_state.clients:
        st.warning("Create client first")
        return

    client=st.selectbox("Client",st.session_state.clients)
    fy=st.text_input("Financial Year")
    process=st.text_input("Audit Process")
    auditor=st.text_input("Auditor Name")
    auditee=st.text_input("Auditee Name")
    dept=st.text_input("Department")
    title=st.text_input("Title")

    if st.button("Create Engagement"):
        st.session_state.eng.append({
            "id":len(st.session_state.eng),
            "client":client,
            "process":process,
            "fy":fy,
            "documents":{},
            "signed":False
        })
        log("Engagement Created")
        st.success("✅ Engagement Created")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ CHECKLIST ------------------
CHECKLIST=["Planning","Risk Assessment","Control Testing","Evidence","Conclusion"]
DOCS=["Scoping Memo","Audit Report","RCM","Audit Program","Workpapers","Evidence"]

def checklist():
    st.markdown("<div class='section'>", unsafe_allow_html=True)

    st.subheader("✅ QA Workflow")

    if not st.session_state.eng:
        st.warning("Create engagement first")
        return

    e=st.selectbox("Select Engagement", st.session_state.eng, format_func=lambda x:x['client'])

    st.write("### 📎 Mandatory Documents + Archival")

    for d in DOCS:
        file=st.file_uploader(d, key=f"{e['id']}_{d}")
        if st.button(f"Archive {d}", key=f"{e['id']}_{d}_archive"):
            st.session_state.archive.append(d)
            log(f"{d} archived")
            st.success(f"{d} archived ✅")

    st.divider()

    for step in CHECKLIST:
        st.write(f"### 🔹 {step}")

        st.file_uploader("Upload Evidence", key=f"{e['id']}_{step}")

        remark=st.text_area("Remarks", key=f"{e['id']}_{step}_remark")

        c1,c2,c3=st.columns(3)

        if c1.button("✔ Pass", key=f"{e['id']}_{step}_p"):
            save(step,"Pass",remark)

        if c2.button("❌ Fail", key=f"{e['id']}_{step}_f"):
            save(step,"Fail",remark)

        if c3.button("N/A", key=f"{e['id']}_{step}_na"):
            save(step,"NA",remark)

        if st.button("💬 Suggest Improvement", key=f"{e['id']}_{step}_chat"):
            st.info("Improve documentation clarity and evidence traceability.")

    if st.button("✅ Human Sign-off"):
        e["signed"]=True
        log("Signed Off")
        st.success("✅ QA Signed Off")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ SAVE ------------------
def save(step,res,remark):
    st.session_state.qa.append({
        "step":step,
        "result":res,
        "remark":remark
    })
    log(f"{step} {res}")
    st.success("Saved ✅")

# ------------------ REPORT ------------------
def report():
    st.markdown("<div class='section'>", unsafe_allow_html=True)

    st.subheader("📄 Final Report")

    df=pd.DataFrame(st.session_state.qa)
    st.dataframe(df)

    st.download_button("Export Excel", df.to_csv(index=False), "QA_Report.csv")

    if st.button("Refine Report"):
        st.info("Improve executive summary and key findings.")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ LOGS ------------------
def logs():
    st.markdown("<div class='section'>", unsafe_allow_html=True)

    st.subheader("📜 Audit Logs")
    st.dataframe(pd.DataFrame(st.session_state.logs))

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ ARCHIVE ------------------
def archive():
    st.markdown("<div class='section'>", unsafe_allow_html=True)

    st.subheader("📦 Archive Repository")

    st.write(st.session_state.archive)

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ MAIN ------------------
if not st.session_state.login:
    login()
else:
    header()

    menu=st.selectbox("Navigate",[
        "Home","Dashboard","Client","Engagement","Checklist","Report","Logs","Archive"
    ])

    if menu=="Home":
        st.info("Enterprise QA workflow system with structured navigation")

    elif menu=="Dashboard":
        dashboard()

    elif menu=="Client":
        client()

    elif menu=="Engagement":
        engagement()

    elif menu=="Checklist":
        checklist()

    elif menu=="Report":
        report()

    elif menu=="Logs":
        logs()

    elif menu=="Archive":
        archive()

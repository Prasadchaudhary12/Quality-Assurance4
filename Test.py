import streamlit as st
import pandas as pd
import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="QA Tool", layout="wide")

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
body, html {font-family: Calibri;}
.stApp {background-color: #e6e6e6;}

.header {
    background: black;
    color: #f1c40f;
    padding: 15px;
    border-radius: 6px;
    text-align: center;
}

.login-box {
    border: 3px solid #f1c40f;
    padding: 25px;
    border-radius: 10px;
    background: white;
}

.section {
    background: white;
    padding: 15px;
    border-radius: 8px;
    margin-top: 10px;
    border-left: 5px solid #f1c40f;
}

.stButton>button {
    background-color: #f1c40f;
    color: black;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
def init():
    defaults={
        "users":{"admin":"admin"},
        "login":False,
        "user":"",
        "clients":[],
        "eng":[],
        "qa":[],
        "logs":[],
        "archives":[]
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k]=v
init()

def log(action):
    st.session_state.logs.append({
        "user":st.session_state.user,
        "action":action,
        "time":datetime.datetime.now()
    })

# ---------------- LOGIN ----------------
def login():
    st.markdown("<h2 class='header'>Internal Audit QA System</h2>", unsafe_allow_html=True)

    col1,col2,col3=st.columns([2,2,2])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)

        u=st.text_input("Username")
        p=st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            if u in st.session_state.users and st.session_state.users[u] == p:
                st.session_state.login=True
                st.session_state.user=u
                log("Login")
                st.rerun()
            else:
                st.error("Invalid Login")

        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- HEADER ----------------
def header():
    col1,col2=st.columns([8,2])
    col1.markdown("<div class='header'>🚆 Internal Audit QA Tool</div>", unsafe_allow_html=True)

    with col2:
        st.write(f"👤 {st.session_state.user}")
        if st.button("Logout"):
            log("Logout")
            st.session_state.login=False
            st.rerun()

# ---------------- DASHBOARD ----------------
def dashboard():
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("📊 Dashboard")

    df=pd.DataFrame(st.session_state.qa)
    total=len(df)
    pass_c=len(df[df.result=="Pass"]) if not df.empty else 0
    fail_c=len(df[df.result=="Fail"]) if not df.empty else 0

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Total QA", total)
    c2.metric("Completed", total)
    c3.metric("Pass", pass_c)
    c4.metric("Fail", fail_c)

    if total>0:
        chart=pd.DataFrame({
            "Status":["Pass","Fail","N/A"],
            "Count":[pass_c,fail_c,total-pass_c-fail_c]
        })
        st.bar_chart(chart.set_index("Status"))

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- CLIENT ----------------
def client():
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("Client Management")

    name=st.text_input("Client Name")

    if st.button("Add Client") and name:
        st.session_state.clients.append(name)
        log("Client Added")
        st.success("Added")

    st.dataframe(pd.DataFrame(st.session_state.clients, columns=["Clients"]))
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- ENGAGEMENT ----------------
def engagement():
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("Engagement")

    if not st.session_state.clients:
        st.warning("Create client first")
        return

    client=st.selectbox("Client",st.session_state.clients)
    process=st.text_input("Process")

    if st.button("Create Engagement"):
        st.session_state.eng.append({
            "id":len(st.session_state.eng),
            "client":client,
            "process":process
        })
        log("Eng Created")
        st.success("Created")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- CHECKLIST ----------------
CHECK=["Planning","Risk","Testing","Evidence","Conclusion"]
DOCS=["RCM","Audit Report","Workpapers","Program","Evidence","Memo"]

def checklist():
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("QA Checklist")

    if not st.session_state.eng:
        st.warning("No engagement")
        return

    e=st.selectbox("Select Engagement", st.session_state.eng, format_func=lambda x:x["client"])

    st.write("### Document Upload + Archive")

    for d in DOCS:
        file=st.file_uploader(d, key=f"{e['id']}_{d}")

        if st.button(f"Archive {d}", key=f"{e['id']}_{d}_a"):
            st.session_state.archives.append({
                "doc":d,
                "user":st.session_state.user,
                "time":datetime.datetime.now()
            })
            st.success(f"{d} Archived")

    st.divider()

    for step in CHECK:
        st.write(f"### {step}")

        remark=st.text_area("Remarks", key=f"{e['id']}_{step}")

        col1,col2,col3=st.columns(3)
        if col1.button("Pass", key=f"{e['id']}_{step}_p"):
            save(step,"Pass",remark)
        if col2.button("Fail", key=f"{e['id']}_{step}_f"):
            save(step,"Fail",remark)
        if col3.button("N/A", key=f"{e['id']}_{step}_n"):
            save(step,"NA",remark)

        if st.button("Suggest", key=f"{e['id']}_{step}_s"):
            st.info("Improve control description")

    st.markdown("</div>", unsafe_allow_html=True)

def save(step,res,remark):
    st.session_state.qa.append({
        "step":step,
        "result":res,
        "remark":remark
    })
    log(f"{step}-{res}")
    st.success("Saved")

# ---------------- REPORT ----------------
def report():
    st.markdown("<div class='section'>", unsafe_allow_html=True)

    st.subheader("Final Report")
    df=pd.DataFrame(st.session_state.qa)
    st.dataframe(df)

    st.download_button("Download Excel", df.to_csv(index=False), "report.csv")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- ARCHIVE ----------------
def archive():
    st.markdown("<div class='section'>", unsafe_allow_html=True)

    st.subheader("Archive")
    st.dataframe(pd.DataFrame(st.session_state.archives))

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- MAIN ----------------
if not st.session_state.login:
    login()
else:
    header()

    menu = st.selectbox("Menu",[
        "Home","Dashboard","Client","Engagement","Checklist","Report","Archive"
    ])

    if menu=="Home":
        st.info("Professional QA application dashboard")

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

    elif menu=="Archive":
        archive()

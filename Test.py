import streamlit as st
import pandas as pd
import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="QA Tool", layout="wide")

st.markdown("""
<style>
html, body {font-family: Calibri;}
.stApp {background-color:#f2f2f2;}
.stButton>button {background-color:#f1c40f; color:black;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
def init():
    if "users" not in st.session_state: st.session_state.users={"admin":"admin"}
    if "logged" not in st.session_state: st.session_state.logged=False
    if "user" not in st.session_state: st.session_state.user=""
    if "clients" not in st.session_state: st.session_state.clients=[]
    if "eng" not in st.session_state: st.session_state.eng=[]
    if "qa" not in st.session_state: st.session_state.qa=[]
    if "logs" not in st.session_state: st.session_state.logs=[]

init()

def log(action):
    st.session_state.logs.append({
        "user":st.session_state.user,
        "action":action,
        "time":datetime.datetime.now()
    })

# ---------------- LOGIN ----------------
def login():
    st.title("🔐 QA Tool Login")
    u=st.text_input("Username")
    p=st.text_input("Password",type="password")

    if st.button("Login"):
        if u in st.session_state.users and st.session_state.users[u]==p:
            st.session_state.logged=True
            st.session_state.user=u
            log("login")
            st.rerun()
        else:
            st.error("Invalid")

# ---------------- DASHBOARD ----------------
def dashboard():
    st.title("📊 Dashboard")
    df=pd.DataFrame(st.session_state.qa)

    total=len(df)
    pass_c=len(df[df.result=="Pass"]) if not df.empty else 0
    fail_c=len(df[df.result=="Fail"]) if not df.empty else 0

    c1,c2,c3=st.columns(3)
    c1.metric("Total",total)
    c2.metric("Pass",pass_c)
    c3.metric("Fail",fail_c)

# ---------------- CLIENT ----------------
def client():
    st.title("Create Client")
    name=st.text_input("Name")

    if st.button("Save") and name:
        st.session_state.clients.append(name)
        log("client added")
        st.success("Saved")

# ---------------- ENG ----------------
def engagement():
    st.title("Create Engagement")

    if not st.session_state.clients:
        st.warning("Create client first")
        return

    c=st.selectbox("Client",st.session_state.clients)
    fy=st.text_input("FY")

    if st.button("Create"):
        st.session_state.eng.append({"id":len(st.session_state.eng),"client":c,"fy":fy})
        log("eng created")
        st.success("Created")

# ---------------- CHECKLIST ----------------
CHECK=["Planning","Risk","Testing","Evidence","Conclusion"]

def checklist():
    st.title("Checklist")

    if not st.session_state.eng:
        st.warning("No engagement")
        return

    e=st.selectbox("Select",st.session_state.eng,format_func=lambda x:x["client"])

    for step in CHECK:
        st.subheader(step)
        st.file_uploader("Upload",key=f"{e['id']}{step}")

        r=st.text_input("Remark",key=f"{e['id']}{step}r")

        col1,col2,col3=st.columns(3)

        if col1.button("Pass",key=f"{e['id']}{step}p"):
            save(step,"Pass",r)

        if col2.button("Fail",key=f"{e['id']}{step}f"):
            save(step,"Fail",r)

        if col3.button("N/A",key=f"{e['id']}{step}n"):
            save(step,"NA",r)

def save(step,res,remark):
    st.session_state.qa.append({
        "step":step,"result":res,"remark":remark
    })
    log(f"{step}-{res}")
    st.success("Saved")

# ---------------- REPORT ----------------
def report():
    st.title("Report")
    df=pd.DataFrame(st.session_state.qa)
    st.dataframe(df)

    st.download_button("Download Excel",df.to_csv(index=False),"report.csv")

# ---------------- LOG ----------------
def logs():
    st.dataframe(pd.DataFrame(st.session_state.logs))

# ---------------- MAIN ----------------
if not st.session_state.logged:
    login()
else:
    st.sidebar.write(f"👤 {st.session_state.user}")

    if st.sidebar.button("Logout"):
        log("logout")
        st.session_state.logged=False
        st.rerun()

    menu=st.sidebar.radio("Menu",[
        "Dashboard","Client","Engagement","Checklist","Report","Logs"
    ])

    if menu=="Dashboard": dashboard()
    if menu=="Client": client()
    if menu=="Engagement": engagement()
    if menu=="Checklist": checklist()
    if menu=="Report": report()
    if menu=="Logs": logs()

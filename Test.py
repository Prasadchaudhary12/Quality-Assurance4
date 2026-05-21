import streamlit as st
import pandas as pd
import datetime

# -------------------- CONFIG --------------------
st.set_page_config(page_title="QA Tool", layout="wide")

# -------------------- THEME --------------------
st.markdown("""
<style>
html, body {
    font-family: Calibri;
    color: #000;
}
.stApp {
    background-color: #e6e6e6;
}

/* HEADER */
.header {
    background: black;
    color: #f1c40f;
    padding: 12px;
    border-radius: 6px;
    text-align: center;
}

/* LOGIN */
.login-box {
    border: 3px solid #f1c40f;
    padding: 25px;
    border-radius: 10px;
    background: white;
}

/* SECTIONS */
.section {
    background: white;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 12px;
    border-left: 5px solid #f1c40f;
}

/* BUTTON */
.stButton>button {
    background-color: #f1c40f;
    color: black;
    font-weight: bold;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

# -------------------- SESSION --------------------
def init():
    defaults = {
        "users":{"admin":"admin"},
        "login":False,
        "user":"",
        "clients":[],
        "eng":[],
        "qa":[],
        "logs":[],
        "archive_docs":[]
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k]=v
init()

def log(action):
    st.session_state.logs.append({
        "User":st.session_state.user,
        "Action":action,
        "Time":datetime.datetime.now()
    })

# -------------------- LOGIN --------------------
def login():
    st.markdown("<h2 class='header'>Internal Audit QA System</h2>", unsafe_allow_html=True)

    col1,col2,col3 = st.columns([2,2,2])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            if user in st.session_state

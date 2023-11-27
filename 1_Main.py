

import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
import database as db
from streamlit__authenticator.authenticate import Authenticate



# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="IfcStudio", page_icon=":bar_chart:", layout="wide")

hide_bar= """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        visibility:hidden;
        width: 0px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        visibility:hidden;
    }
    </style>
"""

# --- USER AUTHENTICATION ---
users = db.fetch_all_users()

usernames = [user["key"] for user in users]
names = [user["name"] for user in users]
hashed_passwords = [user["password"] for user in users]

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    "SIPL_dashboard", "abcdef")

name, authentication_status, username = authenticator.login("Acceso", "main")

if authentication_status == False:
    st.error("usuario/contraseña es incorrecta")
    st.markdown(hide_bar, unsafe_allow_html=True)

if authentication_status == None:
    st.warning("Por favor ingresar su usuario y contraseña")
    st.markdown(hide_bar, unsafe_allow_html=True)
    
if st.session_state["authentication_status"]:
    try:
        if authenticator.reset_password(st.session_state["username"], 'Reset password'):
            st.success('Password modified successfully')
    except Exception as e:
        st.error(e)
##registros
try:
    if Authenticate.register_user("registro","main", preauthorization=False):
        st.success('User registered successfully')
except Exception as e:
    st.error(e)

if authentication_status:
    # # ---- SIDEBAR ----
    st.sidebar.title(f"Bienvenido {name}")
    # st.sidebar.header("select page here :")
    st.write("# Bienvenido a IfcStudio")

    ###about ....
    st.subheader("Introduction :")
    st.text("1. \n2. \n3. \n4. \n5. \n")

    st.sidebar.success("Seleccione una herramienta ")

    ###---- HIDE STREAMLIT STYLE ----
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)


    authenticator.logout("Logout", "sidebar")

    

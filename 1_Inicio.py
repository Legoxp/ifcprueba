

import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import streamlit_authenticator as stauth  # pip install streamlit-authenticator

from streamlit__authenticator.authenticate import Authenticate
from database import  databases 


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


users = databases.fetch_users()
emails = []
usernames = []
passwords = []
nameuser=[]
empresa=[]
cargo=[]
areaempresa=[]

for user in users:
    emails.append(user['key'])
    usernames.append(user['username'])
    passwords.append(user['password'])

credentials = {'usernames': {}}
for index in range(len(emails)):
    credentials['usernames'][usernames[index]] = {'name': emails[index], 'password': passwords[index]}

Authenticator = Authenticate(credentials, cookie_name='Streamlit', key='abcdef', cookie_expiry_days=4)
st.write("# Bienvenido a IfcStudio")
st.image("./imagen/logo.jpeg",width=400)
email, authentication_status, username = Authenticator.login('Acceso', 'main')

if authentication_status == False:
    st.error("Usuario/Contraseña es incorrecta")
    st.markdown(hide_bar, unsafe_allow_html=True)

if authentication_status == None:
    st.warning("Por favor, ingresa tu usuario  y contraseña")
    st.markdown(hide_bar, unsafe_allow_html=True)

info, info1 = st.columns(2)

if not authentication_status:
    databases.sign_up()

if authentication_status:
    # # ---- SIDEBAR ----
    st.sidebar.title(f"Bienvenido {username}")
    # st.sidebar.header("select page here :")
    

    ###about ....
    st.subheader("Introducción  :")
    ##st.text("1. \n2. \n3. \n4. \n5. \n")


    video_file = open('./imagen/IFC STUDIO.mp4', 'rb')
    video_bytes = video_file.read()

    st.video(video_bytes)

    st.sidebar.success("Seleccione una herramienta ")

    st.sidebar.image("./imagen/openbim.png", use_column_width=True) 

    ###---- HIDE STREAMLIT STYLE ----
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)


    Authenticator.logout("Cerrar sesión", "sidebar")

    

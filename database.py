import re
from deta import Deta  # pip install deta
from dotenv import load_dotenv  # pip install python-dotenv
import streamlit as st
from streamlit__authenticator.validator import Validator
from datetime import datetime, timedelta
import extra_streamlit_components as stx
import streamlit_authenticator as stauth
from streamlit__authenticator.hasher import Hasher
from streamlit__authenticator.utils import generate_random_pw
from streamlit__authenticator.exceptions import CredentialsError, ForgotError, RegisterError, ResetError, UpdateError

# Load the environment variables

DETA_KEY = "e0sknhunkhw_ParrzfW9q1WayDGrYJzCRtEXSHuLSa2s"

# Initialize with a project key
deta = Deta(DETA_KEY)

# This is how to create/connect a database
db = deta.Base("ifcstudioUser")

class databases :
    def __init__(self, credentials: dict, cookie_name: str, key: str, cookie_expiry_days: float=30.0, 
            preauthorized: list=None, validator: Validator=None):
            """
            Create a new instance of "Authenticate".

            Parameters
            ----------
            credentials: dict
                The dictionary of usernames, names, passwords, and emails.
            cookie_name: str
                The name of the JWT cookie stored on the client's browser for passwordless reauthentication.
            key: str
                The key to be used for hashing the signature of the JWT cookie.
            cookie_expiry_days: float
                The number of days before the cookie expires on the client's browser.
            preauthorized: list
                The list of emails of unregistered users authorized to register.
            validator: Validator
                A Validator object that checks the validity of the username, name, and email fields.
            """
            self.credentials = credentials
            self.credentials['usernames'] = {key.lower(): value for key, value in credentials['usernames'].items()}
            self.cookie_name = cookie_name
            self.key = key
            self.cookie_expiry_days = cookie_expiry_days
            self.preauthorized = preauthorized
            self.cookie_manager = stx.CookieManager()
            self.validator = validator if validator is not None else validator.Validator()

            if 'name' not in st.session_state:
                st.session_state['name'] = None
            if 'authentication_status' not in st.session_state:
                st.session_state['authentication_status'] = None
            if 'username' not in st.session_state:
                st.session_state['username'] = None
            if 'logout' not in st.session_state:
                st.session_state['logout'] = None


    def insert_user(username, name, password):
        """Returns the user on a successful user creation, otherwise raises and error"""
        return db.put({"key": username, "name": name, "password": password})


    def fetch_all_users():
        """Returns a dict of all users"""
        res = db.fetch()
        return res.items


    def get_user(username):
        """If not found, the function will return None"""
        return db.get(username)


    def update_user(username, updates):
        """If the item is updated, returns None. Otherwise, an exception is raised"""
        return db.update(updates, username)


    def delete_user(username):
        """Always returns None, even if the key does not exist"""
        return db.delete(username)


    def insert_user(email, username, password):
        """
        Inserts Users into the DB
        :param email:
        :param username:
        :param password:
        :return User Upon successful Creation:
        """
        date_joined = str(datetime.datetime.now())

        return db.put({'key': email, 'username': username, 'password': password, 'date_joined': date_joined})


    def fetch_users():
        """
        Fetch Users
        :return Dictionary of Users:
        """
        users = db.fetch()
        return users.items


    def get_user_emails():
        """
        Fetch User Emails
        :return List of user emails:
        """
        users = db.fetch()
        emails = []
        for user in users.items:
            emails.append(user['key'])
        return emails


    def get_usernames():
        """
        Fetch Usernames
        :return List of user usernames:
        """
        users = db.fetch()
        usernames = []
        for user in users.items:
            usernames.append(user['key'])
        return usernames


    def validate_email(email):
        """
        Check Email Validity
        :param email:
        :return True if email is valid else False:
        """
        pattern = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$" #tesQQ12@gmail.com

        if re.match(pattern, email):
            return True
        return False


    def validate_username(username):
        """
        Checks Validity of userName
        :param username:
        :return True if username is valid else False:
        """

        pattern = "^[a-zA-Z0-9]*$"
        if re.match(pattern, username):
            return True
        return False

    def logout(self, button_name: str, location: str='main', key: str=None):
            """
            Creates a logout button.

            Parameters
            ----------
            button_name: str
                The rendered name of the logout button.
            location: str
                The location of the logout button i.e. main or sidebar.
            """
            if location not in ['main', 'sidebar']:
                raise ValueError("Location must be one of 'main' or 'sidebar'")
            if location == 'main':
                if st.button(button_name, key):
                    self.cookie_manager.delete(self.cookie_name)
                    st.session_state['logout'] = True
                    st.session_state['name'] = None
                    st.session_state['username'] = None
                    st.session_state['authentication_status'] = None
            elif location == 'sidebar':
                if st.sidebar.button(button_name, key):
                    self.cookie_manager.delete(self.cookie_name)
                    st.session_state['logout'] = True
                    st.session_state['name'] = None
                    st.session_state['username'] = None
                    st.session_state['authentication_status'] = None

    def sign_up():
        with st.form(key='signup', clear_on_submit=True):
            st.subheader(':green[Sign Up]')
            email = st.text_input(':blue[Email]', placeholder='Enter Your Email')
            username = st.text_input(':blue[Username]', placeholder='Enter Your Username')
            password1 = st.text_input(':blue[Password]', placeholder='Enter Your Password', type='password')
            password2 = st.text_input(':blue[Confirm Password]', placeholder='Confirm Your Password', type='password')

            if email:
                if databases.validate_email(email):
                    if email not in databases.get_user_emails():
                        if databases.validate_username(username):
                            if username not in databases.get_usernames():
                                if len(username) >= 2:
                                    if len(password1) >= 6:
                                        if password1 == password2:
                                            # Add User to DB
                                            hashed_password = stauth.Hasher([password2]).generate()
                                            databases.insert_user(email, username, hashed_password[0])
                                            st.success('Account created successfully!!')
                                            st.balloons()
                                        else:
                                            st.warning('Passwords Do Not Match')
                                    else:
                                        st.warning('Password is too Short')
                                else:
                                    st.warning('Username Too short')
                            else:
                                st.warning('Username Already Exists')

                        else:
                            st.warning('Invalid Username')
                    else:
                        st.warning('Email Already exists!!')
                else:
                    st.warning('Invalid Email')

            btn1, bt2, btn3, btn4, btn5 = st.columns(5)

            with btn3:
                st.form_submit_button('Sign Up')

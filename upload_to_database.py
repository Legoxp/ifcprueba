import streamlit_authenticator as stauth

import database as db

usernames = ["pparker", "legoxp"]
names = ["Peter Parker", "kevin oipip"]
passwords = ["abc123", "333333"]
hashed_passwords = stauth.Hasher(passwords).generate()


for (username, name, hash_password) in zip(usernames, names, hashed_passwords):
    db.insert_user(username, name, hash_password)
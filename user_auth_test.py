import os
from random import randint
import sqlite3
import streamlit as st
import streamlit_authenticator as stauth
import smtplib
import ssl
from email.message import EmailMessage

# "C:\Users\jedidiah\AppData\Local\Programs\Python\Python311\Lib\site-packages\streamlit_authenticator"


def register_user():
    if "activation_code" not in st.session_state:
        st.session_state["activation_code"] = randint(100000, 999999)

    try:
        # NB: st_authenticator.py.register_user() (line 347 & 352) was modified to return the email
        register_email = authenticator.register_user("Sign Up", preauthorization=False)

        if register_email:
            activation_code = st.session_state["activation_code"]

            # verify email
            send_email(
                recipient=register_email,
                subject="PollenQ. Verify Email",
                body=f"""
Your PollenQ activation code is {activation_code}

Please enter this code in the website to complete your registration

Thank you,
PollenQ
""",
            )
            update_db()
            st.success("Welcome On Board! Please login with your detials above")
            entered_code = st.text_input("Activation Code", max_chars=6)

            if st.button("Submit"):
                if int(entered_code) == st.session_state["activation_code"]:

                    # notify user
                    send_email(
                        recipient=register_email,
                        subject="Welcome On Board PollenQ!",
                        body=f"""
You have successful created a PollenQ account. Ensure you keep your login detials safe.

Thank you,
PollenQ
""",
                    )
                else:
                    st.error("Incorrect Code")

    except Exception as e:
        st.error(e)


def forgot_password():
    try:
        (
            email_forgot_pw,
            random_password,
        ) = authenticator.forgot_password("Reset Password")

        if email_forgot_pw:
            # notify user and update password
            send_email(
                recipient=email_forgot_pw,
                subject="PollenQ. Forgot Password",
                body=f"""
Dear {authenticator.credentials["usernames"][email_forgot_pw]["name"]},

Your new password for pollenq.com is {random_password}

Please keep this password safe.

Thank you,
PollenQ
""",
            )
            update_db()
            st.success("Your new password has been sent your email!")

        elif email_forgot_pw == False:
            st.error("Email not found")
    except Exception as e:
        st.error(e)


def reset_password(email):
    try:
        if authenticator.reset_password(email, ""):
            update_db()
            send_email(
                recipient=email,
                subject="PollenQ. Password Changed",
                body=f"""
Dear {authenticator.credentials["usernames"][email]["name"]},

You are recieving this email because your password for pollenq.com has been changed.
If you did not authorize this change please contact us immediately.

Thank you,
PollenQ
""",
            )
            st.success("Password changed successfully")

    except Exception as e:
        st.error(e)


def send_email(recipient, subject, body):

    # Define email sender and receiver
    pollenq_gmail = "jehddie@gmail.com"  # os.environ.get('pollenq_gmail')
    pollenq_gmail_app_pw = "rjcbvvsryyzoiect"  # os.environ.get('pollenq_gmail_app_pw')

    em = EmailMessage()
    em["From"] = pollenq_gmail
    em["To"] = recipient
    em["Subject"] = subject
    em.set_content(body)

    # Add SSL layer of security
    context = ssl.create_default_context()

    # Log in and send the email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(pollenq_gmail, pollenq_gmail_app_pw)
        smtp.sendmail(pollenq_gmail, recipient, em.as_string())


def update_db():
    cur.execute("DELETE FROM users")

    for user, user_detials in credentials["usernames"].items():
        email = user
        password = user_detials["password"]
        name = user_detials["name"]
        signup_date = user_detials["signup_date"]
        last_login_date = user_detials["last_login_date"]
        login_count = user_detials["login_count"]

        cur.execute(
            "INSERT INTO users VALUES(?, ?, ?, ?, ?, ?)",
            (email, password, name, signup_date, last_login_date, login_count),
        )
    con.commit()


con = sqlite3.connect("db/users.db")
cur = con.cursor()

# cur.execute("DROP TABLE users")
# cur.execute("CREATE TABLE users(email, password, name, signup_date)")

# Read usernames and convert to nested dict
users = cur.execute("SELECT * FROM users").fetchall()
credentials = {}
for user in users:
    credentials[user[0]] = {
        "password": user[1],
        "name": user[2],
        "signup_date": user[3],
        "last_login_date": user[4],
        "login_count": user[5],
    }
credentials = {"usernames": credentials}


# Create authenticator object
authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="pollen_user_auth",  # os.environ.get("cookie_name"),
    key="pollen321",  # os.environ.get("cookie_key"),
    cookie_expiry_days=30,  # int(os.environ.get("cookie_expiry_days")),
    preauthorized={"emails": "na"},
)

# Check login. Automatically gets stored in session state
name, authentication_status, email = authenticator.login("Login", "main")

# login successful; proceed
if authentication_status:
    update_db()

    authenticator.logout("Logout", "main")
    detials_cols = st.columns(2)
    detials_cols[0].write(f"Welcome *{name}*")
    with detials_cols[1].expander("Reset Password"):
        reset_password(email)

# login unsucessful; forgot password or create account
elif authentication_status == False:
    st.error("Email/password is incorrect")
    with st.expander("Forgot Password"):
        forgot_password()
    with st.expander("New User"):
        register_user()

# no login trial; create account
elif authentication_status == None:
    st.warning("Please enter your email and password")
    with st.expander("New User"):
        register_user()


# Proceed if authentication is successful
if authentication_status:
    st.title("PollenQ Homepage")
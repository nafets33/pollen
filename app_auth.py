import os
from random import randint
from dotenv import load_dotenv
import sqlite3
import streamlit as st
import streamlit_authenticator as stauth
import smtplib
import ssl
from email.message import EmailMessage


def signin_main():
    """Return True or False if the user is signed in"""

    load_dotenv(os.path.join(os.getcwd(), ".env"))

    def register_user():
        write_flying_bee(54, 54)

        if "verification_code" not in st.session_state:
            st.session_state["verification_code"] = randint(100000, 999999)

        try:
            register_status = authenticator.register_user(
                form_name="Sign Up", preauthorization=False, location="main"
            )

            if register_status:
                register_email = register_status[0]
                register_password = register_status[1]

                verification_code = st.session_state["verification_code"]

                # verify email
                send_email(
                    recipient=register_email,
                    subject="PollenQ. Verify Email",
                    body=f"""
                Your PollenQ verification code is {verification_code}

                Please enter this code in the website to complete your registration

                Thank you,
                PollenQ
                """,
                )
                # TODO user activiation code
                update_db()

                authenticator.direct_login(register_email, register_password)

                send_email(
                    recipient=register_email,
                    subject="Welcome On Board PollenQ!",
                    body=f"""
                You have successful created a PollenQ account. Ensure you keep your login detials safe.

                Thank you,
                PollenQ
                """,
                )
                st.info(
                    "A verification code has been sent to your email. Please enter the code below"
                )
                entered_code = st.text_input("Verification Code", max_chars=6)

                if st.button("Submit"):
                    if int(entered_code) == st.session_state["verification_code"]:

                        # verification successful
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
            write_flying_bee(54, 54)
        except Exception as e:
            st.error(e)

    def forgot_password():
        try:
            (email_forgot_pw, random_password,) = authenticator.forgot_password(
                form_name="Reset Password", location="sidebar"
            )

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
            if authenticator.reset_password(email, "", location="sidebar"):
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
        pollenq_gmail = os.environ.get("pollenq_gmail")
        pollenq_gmail_app_pw = os.environ.get("pollenq_gmail_app_pw")

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
            phone_no = user_detials["phone_no"]
            signup_date = user_detials["signup_date"]
            last_login_date = user_detials["last_login_date"]
            login_count = user_detials["login_count"]

            cur.execute(
                "INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?)",
                (
                    email,
                    password,
                    name,
                    phone_no,
                    signup_date,
                    last_login_date,
                    login_count,
                ),
            )
        con.commit()

    def write_flying_bee(width="45", height="45", frameBorder="0"):
        return st.markdown(
            '<iframe src="https://giphy.com/embed/ksE4eFvxZM3oyaFEVo" width={} height={} frameBorder={} class="giphy-embed" allowFullScreen></iframe><p><a href="https://giphy.com/gifs/bee-traveling-flying-into-next-week-like-ksE4eFvxZM3oyaFEVo"></a></p>'.format(
                width, height, frameBorder
            ),
            unsafe_allow_html=True,
        )

    con = sqlite3.connect("db/users.db")
    cur = con.cursor()

    # cur.execute("DROP TABLE users")
    # cur.execute("CREATE TABLE users(email, password, name, phone_no, signup_date, last_login_date, login_count)")

    # Read usernames and convert to nested dict
    users = cur.execute("SELECT * FROM users").fetchall()
    credentials = {}
    for user in users:
        credentials[user[0]] = {
            "password": user[1],
            "name": user[2],
            "phone_no": user[3],
            "signup_date": user[4],
            "last_login_date": user[5],
            "login_count": user[6],
        }
    credentials = {"usernames": credentials}

    # Create authenticator object
    authenticator = stauth.Authenticate(
        credentials=credentials,
        cookie_name=os.environ.get("cookie_name"),
        key=os.environ.get("cookie_key"),
        cookie_expiry_days=int(os.environ.get("cookie_expiry_days")),
        preauthorized={"emails": "na"},
    )

    # Check login. Automatically gets stored in session state
    name, authentication_status, email = authenticator.login("Login", "main")

    # login successful; proceed
    if authentication_status:
        update_db()

        authenticator.logout("Logout", "sidebar")
        # detials_cols = st.columns(2)
        # detials_cols[0].write(f"Welcome *{name}*")
        # with detials_cols[1].expander("Reset Password"):
        st.sidebar.write(f"Welcome *{name}*")
        reset_password(email)
        return True

    # login unsucessful; forgot password or create account
    elif authentication_status == False:
        st.error("Email/password is incorrect")
        with st.expander("Forgot Password"):
            forgot_password()
        with st.expander("New User"):
            register_user()
        return False

    # no login trial; create account
    elif authentication_status == None:
        st.warning("Please enter your email and password")
        with st.expander("New User"):
            register_user()
        return False


if __name__ == "__main__":
    signin_main()
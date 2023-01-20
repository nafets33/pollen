import os
from random import randint
from dotenv import load_dotenv
import sqlite3
import streamlit as st
import streamlit_authenticator as stauth
import smtplib
import ssl
from email.message import EmailMessage
from chess_piece.king import (
    kingdom__grace_to_find_a_Queen,
    hive_master_root,
    init_clientUser_dbroot,
    local__filepaths_misc,
)
from chess_piece.app_hive import local_gif, live_sandbox__setup_switch
from chess_piece.queen_hive import init_pollen_dbs
import ipdb

# from QueenHive import init_pollen_dbs


def signin_main():
    """Return True or False if the user is signed in"""

    load_dotenv(os.path.join(os.getcwd(), ".env"))
    main_root = hive_master_root()  # os.getcwd()  # hive root
    MISC = local__filepaths_misc()
    floating_queen_gif = MISC["floating_queen_gif"]

    def register_user():
        # write_flying_bee(54, 54)

        try:
            register_status = authenticator.register_user(
                form_name="Sign Up", preauthorization=False, location="main"
            )

            if ("register_status" not in st.session_state) or (
                st.session_state["register_status"] == None
            ):
                st.session_state["register_status"] = register_status

            # generate and store verification code
            if "verification_code" not in st.session_state:
                st.session_state["verification_code"] = randint(100000, 999999)
            verification_code = st.session_state["verification_code"]

            if register_status:

                register_email = st.session_state["register_status"][0]

                # send user verification code
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
                st.success("A verification code has been sent to your email")

            entered_code = st.text_input("Verification Code", max_chars=6)

            if st.button("Submit"):

                if int(entered_code) == verification_code:

                    register_email = st.session_state["register_status"][0]
                    register_password = st.session_state["register_status"][1]

                    # verification successful
                    update_db(register_email, append_db=True)
                    send_email(
                        recipient=register_email,
                        subject="Welcome On Board PollenQ!",
                        body=f"""
                     You have successful created a PollenQ account. Ensure you keep your login detials safe.

                     Thank you,
                     PollenQ
                     """,
                    )

                    authenticator.direct_login(register_email, register_password)

                    # st.session_state["username"] = register_email
                    # self.password = register_password,

                else:
                    st.error("Incorrect Code")

            # write_flying_bee(54, 54)
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
                update_db(email_forgot_pw)
                st.success("Your new password has been sent your email!")

            elif email_forgot_pw == False:
                st.error("Email not found")
        except Exception as e:
            st.error(e)

    def reset_password(email):
        try:
            if authenticator.reset_password(email, "", location="sidebar"):
                update_db(email)
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

    def update_db(email_to_update, append_db=False):
        """Update a user's record, or add a new user"""

        # new user detials are stored in session state
        if append_db:
            detials = st.session_state["new_user_creds"]
        else:
            detials = credentials["usernames"][email_to_update]

        password = detials["password"]
        name = detials["name"]
        phone_no = detials["phone_no"]
        signup_date = detials["signup_date"]
        last_login_date = detials["last_login_date"]
        login_count = detials["login_count"]

        # add new user
        if append_db:
            cur.execute(
                "INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?)",
                (
                    email_to_update,
                    password,
                    name,
                    phone_no,
                    signup_date,
                    last_login_date,
                    login_count,
                ),
            )

        # update value
        else:
            cur.execute(
                f"""
            UPDATE users
            SET password = "{password}",
                name = "{name}",
                phone_no = "{phone_no}",
                signup_date = "{signup_date}",
                last_login_date = "{last_login_date}",
                login_count = "{login_count}"
            
            WHERE email = "{email_to_update}"
            """
            )

        con.commit()
        authenticator.credentials = read_user_db()

    def write_flying_bee(width="45", height="45", frameBorder="0"):
        return st.markdown(
            '<iframe src="https://giphy.com/embed/ksE4eFvxZM3oyaFEVo" width={} height={} frameBorder={} class="giphy-embed" allowFullScreen></iframe><p><a href="https://giphy.com/gifs/bee-traveling-flying-into-next-week-like-ksE4eFvxZM3oyaFEVo"></a></p>'.format(
                width, height, frameBorder
            ),
            unsafe_allow_html=True,
        )

    def setup_user_pollenqdbs(main_root):

        if st.session_state["authorized_user"]:
            st.session_state["client_user"] = st.session_state["username"].split("@")[0]
            
            if 'admin__client_user' in st.session_state:
                st.session_state["client_user"] = st.session_state['admin__client_user']
                db_client_user_name = st.session_state['admin__client_user']
                st.sidebar.write(f"Swarm *{db_client_user_name}*")
            else:
                db_client_user_name = st.session_state["username"].split("@")[0]

            # st.sidebar.write(f"Welcome *{st.session_state['name']}*")
            
            db_root = init_clientUser_dbroot(client_user=db_client_user_name)  # main_root = os.getcwd() // # db_root = os.path.join(main_root, 'db')
            # prod = True if 'production' in st.session_state and st.session_stat['production'] == True else False
            prod = (
                True
                if "production" in st.session_state and st.session_state["production"] == True
                else False
            )
            prod_name = (
                "LIVE"
                if "production" in st.session_state and st.session_state["production"] == True
                else "Sandbox"
            )
            st.session_state["prod_name"] = prod_name
            prod_name_oppiste = "Sandbox" if prod  else "LIVE"
            
            st.session_state["production"] = prod
            
            if st.sidebar.button(f'Switch to {"sb"}'):
                st.session_state["production"] = False
                prod, admin, prod_name = live_sandbox__setup_switch(client_user=st.session_state["client_user"])
            if st.sidebar.button(f'Switch to {"prod"}'):
                st.session_state["production"] = True
                prod, admin, prod_name = live_sandbox__setup_switch(client_user=st.session_state["client_user"])
            
            init_pollen_dbs(db_root=db_root, prod=prod, queens_chess_piece='queen', queenKING=True)


            st.sidebar.warning("Your Queen is Awaiting")
        else:
            db_root = os.path.join(
                main_root, "db"
            )  ## Force to Main db and Sandbox API

        st.session_state["db_root"] = db_root



        return db_root

    # Read usernames and convert to nested dict

    con = sqlite3.connect("db/users.db")
    cur = con.cursor()

    def read_user_db():
        users = cur.execute("SELECT * FROM users").fetchall()

        creds = {}
        for user in users:
            creds[user[0]] = {
                "password": user[1],
                "name": user[2],
                "phone_no": user[3],
                "signup_date": user[4],
                "last_login_date": user[5],
                "login_count": user[6],
            }
        return {"usernames": creds}

    credentials = read_user_db()

    # Create authenticator object
    authenticator = stauth.Authenticate(
        credentials=credentials,
        cookie_name=os.environ.get("cookie_name"),
        key=os.environ.get("cookie_key"),
        cookie_expiry_days=int(os.environ.get("cookie_expiry_days")),
        preauthorized={"emails": "na"},
    )

    # Check login. Automatically gets stored in session state
    name, authentication_status, email = authenticator.login("Login", "sidebar")

    # login successful; proceed
    if authentication_status:
        update_db(email)

        authenticator.logout("Logout", "sidebar")

        reset_password(email)
        # ipdb.set_trace()

        if st.session_state["logout"] != True:
            (
                users_allowed_queen_email,
                users_allowed_queen_emailname,
                users_allowed_queen_emailname__db,
            ) = kingdom__grace_to_find_a_Queen()
            if st.session_state["username"] in users_allowed_queen_email:
                st.session_state["authorized_user"] = True
            else:
                st.session_state["authorized_user"] = False

            st.session_state["admin"] = (
                True
                if st.session_state["username"] in ["stefanstapinski@gmail.com"]
                else False
            )
            setup_user_pollenqdbs(main_root)

        return True

    # login unsucessful; forgot password or create account
    elif authentication_status == False:
        st.session_state["authorized_user"] = False
        st.error("Email/password is incorrect")
        with st.expander("Forgot Password", expanded=True):
            forgot_password()
        with st.expander("New User"):
            register_user()
        return False

    # no login trial; create account
    elif authentication_status == None:
        cols = st.columns((6, 1, 2))
        with cols[0]:
            st.subheader("Create an Account To Get a QueenTraderBot")
        with cols[1]:
            local_gif(gif_path=floating_queen_gif, width="123", height="123")
        with st.expander("New User Create Account"):
            register_user()
        return False


if __name__ == "__main__":
    st.session_state["logout"] = True
    signin_main()

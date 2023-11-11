import os
from random import randint
from dotenv import load_dotenv
import sqlite3
import streamlit as st
import streamlit_authenticator as stauth
import smtplib
import ssl
from email.message import EmailMessage
# from streamlit_extras.switch_page_button import switch_page
from chess_piece.king import kingdom__grace_to_find_a_Queen,  hive_master_root, local__filepaths_misc
from chess_piece.queen_hive import setup_instance, print_line_of_error
import ipdb

# from QueenHive import init_pollen_dbs

main_root = hive_master_root()  # os.getcwd()  # hive root
load_dotenv(os.path.join(main_root, ".env"))

def signin_main(page):
    """Return True or False if the user is signed in"""
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
                    update_db(cur=cur, email=register_email, append_db=True)
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
                form_name="Reset Password", location="main"
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
                update_db(cur=cur, email=email_forgot_pw)
                st.success("Your new password has been sent your email!")

            elif email_forgot_pw == False:
                st.error("Email not found")
        except Exception as e:
            st.error(e)

    def reset_password(authenticator, email, location):
        try:
            if authenticator.reset_password(email, "", location=location):
                update_db(cur=cur, email=email)
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

    def update_db(cur, email, append_db=False):
        """Update a user's record, or add a new user"""

        # new user detials are stored in session state
        if append_db:
            detials = st.session_state["new_user_creds"]
        else:
            detials = credentials["usernames"][email]

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
                    email,
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
            
            WHERE email = "{email}"
            """
            )

        con.commit()
        authenticator.credentials = read_user_db(cur=cur)

    def setup_user_pollenqdbs():
        if 'sneak_key' in st.session_state and st.session_state['sneak_key'] == 'family':
            prod = setup_instance(client_username=st.session_state["username"], switch_env=False, force_db_root=False, queenKING=True, prod=False, init=True)
            st.session_state['instance_setup'] = True
            return prod

        if st.session_state["authorized_user"]:
            if 'admin__client_user' in st.session_state and st.session_state['admin__client_user'] != False:
                st.session_state["username"] = st.session_state['admin__client_user']
                st.sidebar.write(f'Swarm *{st.session_state["username"]}')

            # st.sidebar.warning("Your Queen is Awaiting")
            force_db_root = False
        else:
            # st.sidebar.info("Request For a Queen")
            st.info("Below is a Preview")
            force_db_root = True
            if st.button("Request A Queen"):
                send_email(recipient=os.environ.get('pollenq_gmail'), subject="QueenRequest", body=f'{st.session_state["username"]} Asking for a Queen')
                st.success("Message Sent To Hive Master, We'll talk soon")


        prod = setup_instance(client_username=st.session_state["username"], switch_env=False, force_db_root=force_db_root, queenKING=True, init=True)

        st.session_state['instance_setup'] = True

        return prod

    def define_authorized_user():
        KING, users_allowed_queen_email, users_allowed_queen_emailname__db = kingdom__grace_to_find_a_Queen()
        # print(st.session_state["username"])
        if st.session_state["username"] in users_allowed_queen_email:
            st.session_state["authorized_user"] = True
        else:
            st.session_state["authorized_user"] = False

        st.session_state["admin"] = (
            True
            if st.session_state["username"] in ["stefanstapinski@gmail.com"]
            else False
        )
        
        return setup_user_pollenqdbs()

    def read_user_db(cur):
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
    
    # def main_func__signIn():
    try:
        con = sqlite3.connect("db/client_users.db")
        cur = con.cursor()
        credentials = read_user_db(cur=cur)

        # Create authenticator object
        authenticator = stauth.Authenticate(
            credentials=credentials,
            cookie_name=os.environ.get("cookie_name"),
            key=os.environ.get("cookie_key"),
            cookie_expiry_days=int(os.environ.get("cookie_expiry_days")),
            preauthorized={"emails": "na"},
        )


        # Check login. Automatically gets stored in session state
        if 'sneak_key' in st.session_state and st.session_state['sneak_key'] == 'family':
            authentication_status = True
            st.session_state['name'] = 'stefanstapinski@yahoo.com'
            st.session_state['auth_email'] = "stefanstapinski@yahoo.com"
            st.session_state['auth_name'] = "Kings Guest"
            st.session_state['auth_pw'] = os.environ.get("quantqueen_pw")
            name, authentication_status, email = authenticator.direct_login(st.session_state['auth_email'], os.environ.get("quantqueen_pw"))
            st.session_state['authentication_status'] = True
            authenticator.logout("Logout", location='sidebar')
            define_authorized_user()
            return authenticator
        else:
            name, authentication_status, email = authenticator.login("Login", "main")
            st.session_state['auth_email'] = email
            st.session_state['auth_name'] = name
        
        if authentication_status:
            if 'logout' in st.session_state and st.session_state["logout"] != True:
                authenticator.logout("Logout", location='sidebar')
                reset_password(authenticator, email, location='sidebar')
                
                # Returning Customer
                if 'authorized_user' in st.session_state and st.session_state['authorized_user'] == True:
                    if 'instance_setup' in st.session_state and st.session_state['instance_setup']:
                        return True # no need to setup again right?
                    define_authorized_user()
                    return authenticator
                else:    
                    update_db(cur=cur, email=email)
                    define_authorized_user()
                    return authenticator

        # login unsucessful; forgot password or create account
        elif authentication_status == False:
            st.session_state["authorized_user"] = False
            st.error("Email/password is incorrect")
            with st.expander("Forgot Password", expanded=True):
                forgot_password()
            with st.expander("New User"):
                register_user()
            
            return authenticator

        # no login trial; create account
        elif authentication_status == None:
            with st.expander("New User Create Account"):
                register_user()

            # display_for_unAuth_client_user()

            return authenticator
    
    except Exception as e:
        print('ERROR auth', e)
        print_line_of_error()

if __name__ == "__main__":
    st.session_state["logout"] = True
    signin_main(page='pollenq')

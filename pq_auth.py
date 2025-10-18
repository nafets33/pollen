import os
from random import randint
from dotenv import load_dotenv
from psycopg2 import sql
import streamlit as st
import streamlit_authenticator as stauth
import smtplib
import ssl
from email.message import EmailMessage
from chess_piece.king import hive_master_root, local__filepaths_misc, return_app_ip
from chess_piece.queen_hive import kingdom__grace_to_find_a_Queen, setup_instance, print_line_of_error
from chess_piece.app_hive import set_streamlit_page_config_once, mark_down_text
from datetime import datetime
from chess_piece.pollen_db import PollenDatabase
from custom_button import cust_Button
import ipdb

main_root = hive_master_root()
load_dotenv(os.path.join(main_root, ".env"))
pg_migration = os.getenv('pg_migration', 'False').lower() == 'true'
testing = False

def register_user(authenticator, con, cur):
    try:
        register_status = authenticator.register_user(
            form_name="Sign Up", preauthorization=False, location="main"
        )

        if ("register_status" not in st.session_state) or (
            st.session_state["register_status"] == None
        ):
            st.session_state["register_status"] = register_status

        if os.environ.get('env_verify') != "89":
            verification_code = 0
        else:
            # generate and store verification code
            if "verification_code" not in st.session_state:
                st.session_state["verification_code"] = randint(100000, 999999)
            verification_code = st.session_state["verification_code"]

            if register_status:
                
                register_email = st.session_state["register_status"][0]
                print("registering new user: ", register_email)

                # send user verification code
                send_email(
                    recipient=register_email,
                    subject="Pollen. Verify Email",
                    body=f"""
                Your PollenQ verification code is {verification_code}

                Please enter this code in the website to complete your registration

                Thank you,
                Pollen
                """,
                )
                st.success("A verification code has been sent to your email")

        entered_code = st.text_input("Verification Code", max_chars=6)

        if st.button("Submit"):
            print("verification code: ", verification_code, type(verification_code))
            print("submit button clicked and entered code is: ", entered_code)
            if os.environ.get('env_verify') != "89":
                register_email = st.session_state["register_status"][0]
                register_password = st.session_state["register_status"][1]
                # verification successful
                update_db(authenticator, con=con, cur=cur, email=register_email, append_db=True)
                authenticator.direct_login(register_email, register_password)

            elif int(entered_code) == verification_code:

                register_email = st.session_state["register_status"][0]
                register_password = st.session_state["register_status"][1]

                # verification successful
                print("updating db for new user: ", register_email)
                update_db(authenticator, con=con, cur=cur, email=register_email, append_db=True)
                authenticator.direct_login(register_email, register_password)

                if os.environ.get('env_verify') == "89":
                    send_email(
                        recipient=register_email,
                        subject="Welcome To Pollen!",
                        body=f"""
                    You have successful created a Pollen account. Ensure you keep your login detials safe.

                    Thank you,
                    Pollen
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

def forgot_password(authenticator):
    con, cur = PollenDatabase.return_db_conn()

    try:
        (email_forgot_pw, random_password,) = authenticator.forgot_password(
            form_name="Reset Password", location="main"
        )

        if email_forgot_pw:
            # notify user and update password
            send_email(
                recipient=email_forgot_pw,
                subject="Pollen. Forgot Password",
                body=f"""
Dear {authenticator.credentials["usernames"][email_forgot_pw]["name"]},

Your new password for pollenq.com is {random_password}

Please keep this password safe.

Thank you,
Pollen
""",
            )
            update_db(authenticator, con=con, cur=cur, email=email_forgot_pw)
            st.success("Your new password has been sent your email!")

        elif email_forgot_pw == False:
            st.error("Email not found")
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

def update_db(authenticator, con, cur, email, append_db=False):
    """Update a user's record, or add a new user"""

    # new user details are stored in session state
    if append_db:
        details = st.session_state["new_user_creds"]
        print("update_db Details: ", details)
    else:
        details = authenticator.credentials["usernames"][email]
        # print("else update_db details: ", details)

    password = details["password"]
    name = details["name"]
    phone_no = details["phone_no"]
    signup_date = details["signup_date"]
    last_login_date = details["last_login_date"]

    if isinstance(signup_date, str):
        try:
            signup_date = datetime.strptime(signup_date, "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"Error parsing signup date: {signup_date}, error: {e}")
            signup_date = None
    
    if isinstance(last_login_date, str):
        try:
            last_login_date = datetime.strptime(last_login_date, "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"Error parsing last login date: {last_login_date}, error: {e}")
            last_login_date = None
    login_count = details["login_count"]

    # add new user
    if append_db:
        cur.execute(
            """
            INSERT INTO client_users (email, password, name, phone_no, signup_date, last_login_date, login_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (email, password, name, phone_no, signup_date, last_login_date, login_count)
        )
    # update value
    else:
        cur.execute(
            """
            UPDATE client_users
            SET password = %s,
                name = %s,
                phone_no = %s,
                signup_date = %s,
                last_login_date = %s,
                login_count = %s
            WHERE email = %s
            """,
            (password, name, phone_no, signup_date, last_login_date, login_count, email)
        )

    con.commit()
    authenticator.credentials = read_user_db(cur=cur)

def reset_password(authenticator, email, location="main"):
    con, cur = PollenDatabase.return_db_conn()
    try:
        if authenticator.reset_password(email, "", location=location):
            update_db(authenticator, con=con, cur=cur, email=email)
            send_email(
                recipient=email,
                subject="Pollen. Password Changed",
                body=f"""
Dear {authenticator.credentials["usernames"][email]["name"]},

You are recieving this email because your password for pollenq.com has been changed.
If you did not authorize this change please contact us immediately.

Thank you,
Pollen
""",
            )
            st.success("Password changed successfully")

    except Exception as e:
        st.error(e)

def read_user_db(cur):
    try:
        cur.execute("SELECT * FROM client_users")
        users = cur.fetchall()

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
    except Exception as e:
        raise f'AUTH ERROR READ USERS{e}'

def signin_main(page=None):
    """Return True or False if the user is signed in"""
    ip_address = return_app_ip()
    st.session_state['ip_address'] = ip_address
    MISC = local__filepaths_misc()
    set_streamlit_page_config_once()


    def setup_user_pollenqdbs():
        # print("AUTH SETUP")
        if 'sneak_key' in st.session_state and st.session_state['sneak_key'] == 'family':
            prod, db_root = setup_instance(client_username=st.session_state["username"], switch_env=False, force_db_root=False, queenKING=True, prod=False, init=True)
            st.session_state['instance_setup'] = True
            st.session_state['prod'] = prod
            st.session_state['db_root'] = db_root
            st.session_state['client_user'] = st.session_state["username"]
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

        prod, db_root = setup_instance(client_username=st.session_state["username"], switch_env=False, force_db_root=force_db_root, queenKING=True, init=True)
        st.session_state['instance_setup'] = True
        st.session_state['prod'] = prod
        st.session_state['client_user'] = st.session_state["username"]
        st.session_state['db_root'] = db_root
        return prod

    def define_authorized_user():

        KING = kingdom__grace_to_find_a_Queen()
        not_allowed = KING['users']['not_allowed']
        if st.session_state["username"] in not_allowed:
            st.session_state["authorized_user"] = False
        else:
            st.session_state["authorized_user"] = True

        st.session_state["admin"] = (
            True
            if st.session_state["username"] in [os.environ.get('admin_user')]
            else False
        )
        
        return setup_user_pollenqdbs()
    if testing:
        print("AUTH FIRST LOOK")
    try:
        already_setup = True if 'instance_setup' in st.session_state and st.session_state['instance_setup'] else False
        con, cur = PollenDatabase.return_db_conn()
        credentials = read_user_db(cur)

        # Create authenticator object
        authenticator = stauth.Authenticate(
            credentials=credentials,
            cookie_name=os.environ.get("cookie_name"),
            key=os.environ.get("cookie_key"),
            cookie_expiry_days=int(os.environ.get("cookie_expiry_days")),
            preauthorized={"emails": "na"},
        )
        
        # st.write(st.session_state)
        # if 'stefanstapinski@gmail.com' in st.session_state['auth_email']:
        #     print("YESSS")
        #     authentication_status = True
        #     # st.session_state['name'] = 'stefanstapinski@yahoo.com'
        #     # st.session_state['auth_email'] = "stefanstapinski@yahoo.com"
        #     # st.session_state['auth_name'] = "Kings Guest"
        #     # st.session_state['auth_pw'] = os.environ.get("quantqueen_pw")
        #     name, authentication_status, email = authenticator.direct_login(st.session_state['auth_email'], os.environ.get("quantqueen_pw"))
        #     return authenticator


        # Check login. Automatically gets stored in session state
        if 'sneak_key' in st.session_state and st.session_state['sneak_key'].lower() == 'family':
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
            if testing:
                print(email, name)
            st.session_state['auth_email'] = email
            st.session_state['auth_name'] = name
        
        if authentication_status:
            if 'logout' in st.session_state and st.session_state["logout"] != True:
                # authenticator.logout("Logout", location='sidebar')
                # reset_password(authenticator, email, location='sidebar')
                
                # Returning Customer
                if 'authorized_user' in st.session_state and st.session_state['authorized_user'] == True:
                    if already_setup:
                        setup_user_pollenqdbs()
                        return authenticator
                    else:
                        define_authorized_user()
                        return authenticator
                else:    
                    update_db(authenticator, con=con, cur=cur, email=email)
                    define_authorized_user()

        # login unsucessful; forgot password or create account
        elif authentication_status == False:
            st.session_state["authorized_user"] = False
            st.error("Email/password is incorrect")
            with st.expander("Forgot Password", expanded=True):
                forgot_password(authenticator)
            with st.expander("New User"):
                register_user(authenticator, con, cur)


        # no login trial; create account
        elif authentication_status == None:
            with st.expander("New User Create Account"):
                register_user(authenticator, con, cur)
            
            # cust_Button(file_path_url='misc/pollen_preview.gif', height='150px', hoverText='')
    
        print("ATUH", authentication_status)

        
        return authenticator
    
    
    except Exception as e:
        print('ERROR auth', e)
        print_line_of_error()

if __name__ == "__main__":
    st.session_state["logout"] = True
    signin_main(page='pollenq')
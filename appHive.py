import os
from random import randint
import sqlite3
import streamlit as st
import streamlit_authenticator as stauth
import smtplib
import ssl
from email.message import EmailMessage
import matplotlib.pyplot as plt

from dotenv import load_dotenv

load_dotenv()

## IMPROVE GLOBAL VARIABLES

################ AUTH ###################
def register_user(cur, con, authenticator):
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
            update_db(cur, con)
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


def forgot_password(authenticator, cur, con):
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
            update_db(cur, con)
            st.success("Your new password has been sent your email!")

        elif email_forgot_pw == False:
            st.error("Email not found")
    except Exception as e:
        st.error(e)


def reset_password(email):
    try:
        if authenticator.reset_password(email, ""):
            update_db(cur, con)
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
    pollenq_gmail = os.environ.get('pollenq_gmail')
    pollenq_gmail_app_pw = os.environ.get('pollenq_gmail_app_pw')

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


def update_db(cur, con):
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


def signin_main():
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
        cookie_name= os.environ.get("cookie_name"),
        key= os.environ.get("cookie_key"),
        cookie_expiry_days= int(os.environ.get("cookie_expiry_days")),
        preauthorized={"emails": "na"},
    )

    # Check login. Automatically gets stored in session state
    name, authentication_status, email = authenticator.login("Login", "main")

    # login successful; proceed
    if authentication_status:
        update_db(cur, con)

        authenticator.logout("Logout", "main")
        detials_cols = st.columns(2)
        detials_cols[0].write(f"Welcome *{name}*")
        with detials_cols[1].expander("Reset Password"):
            reset_password(email)

        return email

    # login unsucessful; forgot password or create account
    elif authentication_status == False:
        st.error("Email/password is incorrect")
        with st.expander("Forgot Password"):
            forgot_password(authenticator, cur, con)
        with st.expander("New User"):
            register_user(cur, con, authenticator)

        return False

    # no login trial; create account
    elif authentication_status == None:
        st.warning("Please enter your email and password")
        with st.expander("New User"):
            register_user()
        
        return False

################ AUTH ###################



############### Charts ##################

def example__subPlot():
    st.header("Sub Plots")
    # st.balloons()
    fig = plt.figure(figsize = (10, 5))

    #Plot 1
    data = {'C':15, 'C++':20, 'JavaScript': 30, 'Python':35}
    Courses = list(data.keys())
    values = list(data.values())
    
    plt.xlabel("Programming Environment")
    plt.ylabel("Number of Students")

    plt.subplot(1, 2, 1)
    plt.bar(Courses, values)

    #Plot 2
    x = np.array([35, 25, 25, 15])
    mylabels = ["Python", "JavaScript", "C++", "C"]

    plt.subplot(1, 2, 2)
    plt.pie(x, labels = mylabels)

    st.pyplot(fig)


def example__df_plotchart(title, df, y, x=False, figsize=(14,7), formatme=False):
    st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
    if x == False:
        return df.plot(y=y,figsize=figsize)
    else:
        if formatme:
            df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')
            return df.plot(x='chartdate', y=y,figsize=figsize)
        else:
            return df.plot(x=x, y=y,figsize=figsize)
  
############### Charts ##################



############ utils ############

def example__callback_function__set_session_state(state, key):
    # 1. Access the widget's setting via st.session_state[key]
    # 2. Set the session state you intended to set in the widget
    st.session_state[state] = st.session_state[key]


def example__color_coding__dataframe(row):
    if row.mac_ranger == 'white':
        return ['background-color:white'] * len(row)
    elif row.mac_ranger == 'black':
        return ['background-color:black'] * len(row)
    elif row.mac_ranger == 'blue':
        return ['background-color:blue'] * len(row)
    elif row.mac_ranger == 'purple':
        return ['background-color:purple'] * len(row)
    elif row.mac_ranger == 'pink':
        return ['background-color:pink'] * len(row)
    elif row.mac_ranger == 'red':
        return ['background-color:red'] * len(row)
    elif row.mac_ranger == 'green':
        return ['background-color:green'] * len(row)
    elif row.mac_ranger == 'yellow':
        return ['background-color:yellow'] * len(row)

    
    import seaborn as sns
    cm = sns.light_palette("green", as_cmap=True)
    df.style.background_gradient(cmap=cm).set_precision(2)


############ utils ############

import os
from random import randint
import sqlite3
import streamlit as st
import streamlit_authenticator as stauth
import smtplib
import ssl
from email.message import EmailMessage
import matplotlib.pyplot as plt
import base64
import pytz
from PIL import Image

from dotenv import load_dotenv

est = pytz.timezone("US/Eastern")

from dotenv import load_dotenv

default_text_color = '#59490A'
default_font = "sans serif"
load_dotenv()

main_root = os.getcwd()

# images
jpg_root = os.path.join(main_root, 'misc')
bee_image = os.path.join(jpg_root, 'bee.jpg')
bee_power_image = os.path.join(jpg_root, 'power.jpg')
hex_image = os.path.join(jpg_root, 'hex_design.jpg')
hive_image = os.path.join(jpg_root, 'bee_hive.jpg')
queen_image = os.path.join(jpg_root, 'queen.jpg')
queen_angel_image = os.path.join(jpg_root, 'queen_angel.jpg')
page_icon = Image.open(bee_image)
flyingbee_gif_path = os.path.join(jpg_root, 'flyingbee_gif_clean.gif')
flyingbee_grey_gif_path = os.path.join(jpg_root, 'flying_bee_clean_grey.gif')
bitcoin_gif = os.path.join(jpg_root, 'bitcoin_spinning.gif')
power_gif = os.path.join(jpg_root, 'power_gif.gif')

## IMPROVE GLOBAL VARIABLES

################ AUTH ###################

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

################ AUTH ###################

def mark_down_text(align='center', color=default_text_color, fontsize='33', text='Hello There', font=default_font):
    st.markdown('<p style="text-align: {}; font-family:{}; color:{}; font-size: {}px;">{}</p>'.format(align, font, color, fontsize, text), unsafe_allow_html=True)
    return True


def page_line_seperator(height='3', border='none', color='#C5B743'):
    return st.markdown("""<hr style="height:{}px;border:{};color:#333;background-color:{};" /> """.format(height, border, color), unsafe_allow_html=True)


def write_flying_bee(width="45", height="45", frameBorder="0"):
    return st.markdown('<iframe src="https://giphy.com/embed/ksE4eFvxZM3oyaFEVo" width={} height={} frameBorder={} class="giphy-embed" allowFullScreen></iframe><p><a href="https://giphy.com/gifs/bee-traveling-flying-into-next-week-like-ksE4eFvxZM3oyaFEVo"></a></p>'.format(width, height, frameBorder), unsafe_allow_html=True)


def hexagon_gif(width="45", height="45", frameBorder="0"):
    return st.markdown('<iframe src="https://giphy.com/embed/Wv35RAfkREOSSjIZDS" width={} height={} frameBorder={} class="giphy-embed" allowFullScreen></iframe><p><a href="https://giphy.com/gifs/star-12-hexagon-Wv35RAfkREOSSjIZDS"></a></p>'.format(width, height, frameBorder), unsafe_allow_html=True)


def local_gif(gif_path, width='33', height='33'):
    with open(gif_path, "rb") as file_:
        contents = file_.read()
        data_url = base64.b64encode(contents).decode("utf-8")
        st.markdown(f'<img src="data:image/gif;base64,{data_url}" width={width} height={height} alt="bee">', unsafe_allow_html=True)


def flying_bee_gif(width='33', height='33'):
    with open(os.path.join(jpg_root, 'flyingbee_gif_clean.gif'), "rb") as file_:
        contents = file_.read()
        data_url = base64.b64encode(contents).decode("utf-8")
        st.markdown(f'<img src="data:image/gif;base64,{data_url}" width={width} height={height} alt="bee">', unsafe_allow_html=True)


def pollen__story(df):
    with st.expander('pollen story', expanded=False):
        df_write = df.astype(str)
        st.dataframe(df_write)
        pass

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



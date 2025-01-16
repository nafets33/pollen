import argparse
import base64
import os
import time
import smtplib
import ssl
from datetime import datetime, date
from email.message import EmailMessage
import alpaca_trade_api as tradeapi
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytz
import streamlit as st
from alpaca_trade_api.rest import URL
from alpaca_trade_api.rest_async import AsyncRest
from PIL import Image
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
from streamlit_extras.switch_page_button import switch_page
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import ipdb
from custom_grid import st_custom_grid
from custom_grid import GridOptionsBuilder as GOB
from custom_graph_v1 import st_custom_graph
import random
import sys
import subprocess


# componenets
import streamlit_antd_components as sac

from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stoggle import stoggle
import hydralit_components as hc
from custom_button import cust_Button
# from custom_text import custom_text, TextOptionsBuilder

from chess_piece.king import (
    PickleData,
    ReadPickleData,
    hive_master_root,
    local__filepaths_misc,
    streamlit_config_colors,
    return_timestamp_string,
    print_line_of_error,
    
)
from chess_piece.pollen_db import PollenDatabase

main_root = hive_master_root()  # os.getcwd()  # hive root
load_dotenv(os.path.join(main_root, ".env"))

pg_migration = os.getenv('pg_migration')

est = pytz.timezone("US/Eastern")
utc = pytz.timezone("UTC")


# images
jpg_root = os.path.join(main_root, "misc")
MISC = local__filepaths_misc()
# chess_pic_1 = os.path.join(jpg_root, 'chess_pic_1.jpg')
queenbee = os.path.join(jpg_root, "bee.png")
bee_image = os.path.join(jpg_root, "bee.jpg")
bee_power_image = os.path.join(jpg_root, "power.jpg")
hex_image = os.path.join(jpg_root, "hex_design.jpg")
hive_image = os.path.join(jpg_root, "bee_hive.jpg")
queen_image = os.path.join(jpg_root, "queen.jpg")
queen_angel_image = os.path.join(jpg_root, "queen_angel.jpg")
flyingbee_gif_path = os.path.join(jpg_root, "flyingbee_gif_clean.gif")
flyingbee_grey_gif_path = os.path.join(jpg_root, "flying_bee_clean_grey.gif")
bitcoin_gif = os.path.join(jpg_root, "bitcoin_spinning.gif")
power_gif = os.path.join(jpg_root, "power_gif.gif")
uparrow_gif = os.path.join(jpg_root, "uparrows.gif")
learningwalk_bee = os.path.join(jpg_root, "learningwalks_bee_jq.png")
learningwalk_bee = Image.open(learningwalk_bee)
queen_flair_gif = os.path.join(jpg_root, "queen_flair.gif")
mainpage_bee_png = MISC[
    "mainpage_bee_png"
]  # queen_flair_gif_original = os.path.join(jpg_root, 'queen_flair.gif')

chess_piece_queen = (
    "https://cdn.pixabay.com/photo/2012/04/18/00/42/chess-36311_960_720.png"
)
runaway_bee_gif = os.path.join(jpg_root, "runaway_bee_gif.gif")

page_icon = Image.open(os.path.join(jpg_root, "power.png"))

##### STREAMLIT ###
k_colors = streamlit_config_colors()
default_text_color = k_colors["default_text_color"]  # = '#59490A'
default_font = k_colors["default_font"]  # = "sans serif"
default_yellow_color = k_colors["default_yellow_color"]  # = '#C5B743'

def set_streamlit_page_config_once():
    try:
        st.set_page_config(
            page_title="pollen",
            page_icon=page_icon,
            layout="wide",
            initial_sidebar_state='collapsed',
            #  menu_items={
            #      'Get Help': 'https://www.extremelycoolapp.com/help',
            #      'Report a bug': "https://www.extremelycoolapp.com/bug",
            #      'About': "# This is a header. This is an *extremely* cool app!"
            #  }
        )            
    except st.errors.StreamlitAPIException as e:
        if "can only be called once per app" in e.__str__():
            # ignore this error
            return
        raise e


def create_AppRequest_package(request_name, archive_bucket=None, client_order_id=None):
    now = datetime.now(est)
    return {
    'client_order_id': client_order_id,
    'app_requests_id': f'{request_name}{"_app-request_id_"}{return_timestamp_string()}{now.microsecond}', 
    'request_name': request_name,
    'archive_bucket': archive_bucket,
    'request_timestamp': now,
    }

def return_runningbee_gif__save(title="Saved", width=33, gif=runaway_bee_gif):
    local_gif(gif_path=gif)
    st.success(title)


def return_page_tabs(func_list=['orders', 'queens_mind', 'chess_board', 'waves', 'workerbees', 'charts', 'the_flash']):
    func_list = [i for i in func_list if st.session_state[i]]
    if len(func_list) == 0:
        st.info("I would Suggest Checking our Your ChessBoard This Morning")
        tabs = False
    else:
        tabs = st.tabs(func_list)
    
    return tabs, func_list


################ AUTH ###################


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


def sac_menu_buttons(main='Queen'):
    if main=='Queen':
        sac_menu_buttons = sac.buttons([
            sac.ButtonsItem(label='pollen', icon='robot'),
            sac.ButtonsItem(label='Board', icon='box'),
            sac.ButtonsItem(label='Orders', icon='backpack4-fill'),
            # sac.ButtonsItem(label='PlayGround', icon='fire'),
            # sac.ButtonsItem(label='Ozz', icon='wechat', href=f'{st.session_state["streamlit_ip"]}/ozz'),
            sac.ButtonsItem(label='Trading Models', disabled=False),
            # sac.ButtonsItem(label='Waves', icon='share-fill'),
            sac.ButtonsItem(label='Engine', icon='gem'),
            sac.ButtonsItem(label='Account', icon='share-fill'),
        ], format_func='title', align='end', type='text')
    elif main == 'Account':
        sac_menu_buttons = sac.buttons([
            sac.ButtonsItem(label='account', icon='key'),

            sac.ButtonsItem(label='Queen', icon='house'),
            # sac.ButtonsItem(label='Log Out', icon='key'),
        ], format_func='title', align='end', type='text')

    return sac_menu_buttons

################ AUTH ###################

def trigger_py_script(script_path):

    # script_path = os.path.join(hive_master_root(), 'pq_fastapi_server.py')
    try:
        # Use sys.executable to get the path to the Python interpreter
        python_executable = sys.executable
        subprocess.run([python_executable, script_path, '-i'])
    except FileNotFoundError:
        print(f"Error: Python interpreter not found. Make sure Python is installed.")
    except Exception as e:
        print(f"Error: {e}")

def trigger_airflow_dag(dag, client_username, prod, airflow_password=False, airflow_username=False, airflow_host=False):
    # http://34.162.91.146:8080/api/v1/dags ## dict visual of dags
    airflow_host = airflow_host if airflow_host else os.environ.get("airflow_host")
    airflow_password = airflow_password if airflow_password else os.environ.get("airflow_password")
    airflow_username = airflow_username if airflow_username else os.environ.get("airflow_username")
    # queens_chess_piece = queens_chess_piece if queens_chess_piece else None
    
    url = f'http://{airflow_host}/api/v1/dags/{dag}/dagRuns'
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    
    if dag == 'run_queenbee':
        data = {
            "dag_run_id": f'{dag}__{datetime.now(utc)}',
            "logical_date": f'{datetime.now(utc)}',
            "conf": {"client_user": client_username, "prod":prod}
        }
    elif dag =='run_workerbees':
        data = {
            "dag_run_id": f'{dag}__{datetime.now(utc)}',
            "logical_date": f'{datetime.now(utc)}',
        }
    elif dag =='run_workerbees_crypto':
        data = {
            "dag_run_id": f'{dag}__{datetime.now(utc)}',
            "logical_date": f'{datetime.now(utc)}',
        }

    result = requests.post(
        url,
        json=data,
        headers=headers,
        auth=HTTPBasicAuth(airflow_username, airflow_password)
    )

    return result


def queen_orders_view(
    QUEEN, queen_order_state, cols_to_view=False, return_all_cols=False, return_str=True
):
    if cols_to_view:
        col_view = col_view
    else:
        col_view = [
            "honey",
            "money",
            "symbol",
            "ticker_time_frame",
            "trigname",
            "datetime",
            "honey_time_in_profit",
            "filled_qty",
            "qty_available",
            "filled_avg_price",
            "limit_price",
            "cost_basis",
            "wave_amo",
            # "status_q",
            "client_order_id",
            "origin_wave",
            "wave_at_creation",
            "power_up",
            "sell_reason",
            "exit_order_link",
            "queen_order_state",
            "order_rules",
            "order_trig_sell_stop",
            "side",
        ]
    if len(QUEEN["queen_orders"]) > 0:
        df = QUEEN["queen_orders"]
        df = df[df["queen_order_state"].isin(queen_order_state)].copy()

        if len(df) > 0:
            # if 'running' in queen_order_state:
            #     df = df[col_view]
            # if 'profit_loss' in df.columns:
            #     df["profit_loss"] = df['profit_loss'].map("{:.2f}".format)
            # if "honey" in df.columns:
            #     df["honey"] = df['honey'].map("{:.2%}".format)
            # if "cost_basis" in df.columns:
            #     df["cost_basis"] = df['cost_basis'].map("{:.2f}".format)

            col_view = [i for i in col_view if i in df.columns]
            df_return = df[col_view].copy()
        else:
            df_return = df

        if return_all_cols and len(df_return) > 0:
            all_cols = col_view + [i for i in df.columns.tolist() if i not in col_view]
            df_return = df[all_cols].copy()

        if return_str:
            df_return = df_return.astype(str)

        return {"df": df_return}
    else:
        return {"df": pd.DataFrame()}



def update_queencontrol_theme(QUEEN_KING, theme_list):
    theme_desc = {
        "nuetral": " follows basic model wave patterns",
        "strong_risk": " defaults to high power trades",
        "star__storywave": " follows symbols each day changes and adjusts order rules based on latest data",
    }
    with st.form("Update Control"):
        # cols = st.columns((1,3))
        # with cols[0]:
        theme_option = st.selectbox(
            label="set theme", options=theme_list, index=theme_list.index("nuetral")
        )
        save_button = st.form_submit_button("Save Theme Setting")
        # with cols[0]:
        # with cols[1]:
        #     st.info("Set your Risk Theme")
        #     # st.warning(f'Theme: {theme_option}')
        #     ep = st.empty()
        # with cols[1]:
        st.info(f"Theme: {theme_option}{theme_desc[theme_option]}")

        if save_button:
            QUEEN_KING["theme"] = theme_option
            QUEEN_KING["last_app_update"] = datetime.now()
            PickleData(pickle_file=QUEEN_KING["source"], data_to_store=QUEEN_KING)
            st.success("Theme Saved")


def admin_queens_active(PB_KING_Pickle, KING):
    pass # handle pg_migration
    # if st.session_state['admin']:
    #     with st.expander("admin QUEENS_ACTIVE"):
    #         df = return_all_client_users__db()
    #         # df = pd.DataFrame(KING['users'].get('client_users_db'))
    #         allowed_list = KING['users']['client_user__allowed_queen_list']
    #         df_map = pd.DataFrame(allowed_list)
    #         df_map['queen_authorized'] = 'active'
    #         df_map = df_map.rename(columns={0: 'email'})
            
    #         df = pd.merge(df, df_map, how='outer', on='email').fillna('')
    #         grid = standard_AGgrid(data=df, use_checkbox=False, update_mode_value="MANUAL", grid_type='king_users')
    #         grid_df = grid['data']

    #         allowed_list_new = grid_df[grid_df['queen_authorized'] == 'active']
    #         allowed_list_new = allowed_list_new['email'].tolist()
    #         new_emails = [i for i in allowed_list_new if i not in allowed_list]

    #         if st.button("Save"):
    #             KING['users']['client_user__allowed_queen_list'] = allowed_list_new
    #             PickleData(PB_KING_Pickle, KING, write_temp=False)
    #             st.success("Auth Queen Users Updated")
    #             print(new_emails)
    #             for email in new_emails:
    #                 print(email)
    #                 send_email(email, subject="Trading Bot is Now Active", 
    #                 body=f""" Hey! Your Trading Bot is Now Active, She will Manage your Portoflio Based on your Settings!.
    #                 Steps:
    #                 1. Login to pollenq.com and enter your API credentials from alpaca brokerage >>> https://app.alpaca.markets/brokerage/dashboard/overview
    #                 2. Customize Trading Bot Setting to Trade Specific to your Needs
    #                 3. Or Join an Existing Fund Trading Strategies

    #                 Happy Trading
    #                 pollenq
    #                 """
                    
    #                 )


def mark_down_text(
    align="center",
    color=default_text_color,
    fontsize="33",
    text="Hello There",
    font=default_font,
    hyperlink=False,
    sidebar=False
):
    if hyperlink:
        st.markdown(
            """<a style='display: block; text-align: {};' href="{}">{}</a>
            """.format(
                align, hyperlink, text
            ),
            unsafe_allow_html=True,
        )
    else:
        if sidebar:
            st.sidebar.markdown(
                '<p style="text-align: {}; font-family:{}; color:{}; font-size: {}px;">{}</p>'.format(align, font, color, fontsize, text),unsafe_allow_html=True,)
        else:
            st.markdown(
            '<p style="text-align: {}; font-family:{}; color:{}; font-size: {}px;">{}</p>'.format(align, font, color, fontsize, text),unsafe_allow_html=True,)
    return True


def progress_bar(value, sleeptime=0.000003, text=False, pct=False):
    status_text = st.empty()
    if pct:
        value = int(round((value * 100), 0))
    p_bar = st.progress(value)
    if text:
        status_text.text(text)

    return True


def stop_queenbee(QUEEN_KING, sidebar=False, pg_migration=False, table_name=None):
    if sidebar:
        checkbox_val = st.sidebar.button("Stop Queen", use_container_width=True)
    else:
        checkbox_val = st.button("Stop Queen", use_container_width=True)
    
    if checkbox_val:
        stop_queen = create_AppRequest_package(request_name='queen_sleep')

        QUEEN_KING['queen_sleep'].append(stop_queen)
        if pg_migration:
            PollenDatabase.upsert_data(table_name=table_name, key=QUEEN_KING.get('key'), value=QUEEN_KING)
        else:
            PickleData(QUEEN_KING.get('source'), QUEEN_KING)
        st.success("Queen Sleeps")
    
    return True



def account_header_grid(client_user, refresh_sec, ip_address, seconds_to_market_close):
    try:
        # gb = GridOptionsBuilder.create()
        gb = GOB.create()
        gb.configure_default_column(column_width=120, resizable=True,wrapText=False, wrapHeaderText=True, autoHeaderHeight=True, autoHeight=True, suppress_menu=False, filterable=False,sortable=True)            
        # gb.configure_index('symbol')
        gb.configure_theme('ag-theme-material')

        cols=['Long',
        'Short',
        'Heart Beat',
        'Avg Beat',
        'Todays Money',
        'Todays Honey',
        'Portfolio Value',
        'Buying Power',
        'Cash',
        'daytrade count']  

        animate_numbers = {'cellRenderer': 'agAnimateShowChangeCellRenderer','enableCellChangeFlash': True,}

        def config_cols(cols):
            backgroundColor = k_colors.get('default_background_color')
            default_text_color = k_colors.get('default_text_color')
            return  {
        'Long': {**{'width': 120, 'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '15px'}}, **animate_numbers},                  
        'Short': {'width': 120, 'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '15px'}},
        'Heart Beat': {**{'width': 100, 'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '15px'}}, **animate_numbers},
        'Avg Beat': {'width': 80, 'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '16px'}},
        'Money': {**{'width': 120, 'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '16px'}, "type": ["customNumberFormat", "numericColumn", "customCurrencyFormat"], 'custom_currency_symbol':"$"}, **animate_numbers},
        'Todays Honey': {'width': 120,'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '16px'}},
        'Portfolio Value': {'width': 120,'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '15px'}},
        'Buying Power': {'width': 120,'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '15px'}},
        'Cash': {**{'width': 120,'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '15px'}}, **animate_numbers},
        'daytrade count': {'width': 80,'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '12px'}},
        'Broker Delta': {'width': 80,'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '12px'}},
            }
              
        config_cols_ = config_cols(cols)
        for col, config_values in config_cols_.items():
            config = config_values
            gb.configure_column(col, config)

        go = gb.build()

        st_custom_grid(
            client_user=client_user,
            username=client_user, #KING['users_allowed_queen_emailname__db'].get(client_user), 
            api=f"{ip_address}/api/data/account_header",
            api_update= None, #f"{ip_address}/api/data/update_queenking_chessboard",
            refresh_sec=refresh_sec, 
            refresh_cutoff_sec=seconds_to_market_close, 
            prod=st.session_state['prod'],
            grid_options=go,
            key=f'account_header',
            # kwargs from here
            prompt_message = None, #"symbol",
            prompt_field = None, #"symbol", # "current_macd_tier", # for signle value
            api_key=os.environ.get("fastAPI_key"),
            buttons=[],
            grid_height='123px',
            toggle_views=[],
            ) 

    except Exception as e:
        print_line_of_error(e)


def queen_messages_grid__apphive(KING, log_file, f_api, grid_key='queen_logfile', varss={'seconds_to_market_close': 4, 'refresh_sec': 4}):
    gb = GOB.create()
    gb.configure_grid_options(pagination=False, enableRangeSelection=True, copyHeadersToClipboard=True, sideBar=False)
    gb.configure_default_column(column_width=100, resizable=True, wrapText=True, wrapHeaderText=True, autoHeaderHeight=True, autoHeight=True, suppress_menu=False, filterable=True, sortable=True)             
    gb.configure_theme('ag-theme-material')

    #Configure index field
    gb.configure_index('idx')
    gb.configure_column('idx', {"sortable":True, 'initialWidth':89, 'sort':'desc'})
    gb.configure_column('message', {'width':1250, "wrapText": True, "autoHeight": True, "sortable":True, 'cellStyle': {'fontSize': '15px'}})
    go = gb.build()

    st_custom_grid(
        username=st.session_state["username"], 
        api=f_api,
        api_update=None,
        refresh_sec=varss.get('refresh_sec'), 
        refresh_cutoff_sec=varss.get('seconds_to_market_close'), 
        prod=st.session_state['prod'],
        grid_options=go,
        key=grid_key,
        toggle_views=[],

        # kwargs from here
        api_key=os.environ.get("fastAPI_key"),
        buttons = [],

        grid_height='350px',
        log_file=log_file

    ) 

    return True

    return True


def queen_messages_logfile_grid(KING, log_file, grid_key='queen_logfile', f_api="http://127.0.0.1:8000/api/data/queen_messages_logfile", varss={'seconds_to_market_close': None, 'refresh_sec': None}, toggle_views=[]):
    gb = GOB.create()
    gb.configure_grid_options(pagination=False, enableRangeSelection=True, copyHeadersToClipboard=False, sideBar=False)
    gb.configure_default_column(column_width=100, resizable=True, wrapText=True, wrapHeaderText=True, autoHeaderHeight=True, autoHeight=True, suppress_menu=False, filterable=True, sortable=True)             
    # gb.configure_theme('ag-theme-material')

    #Configure index field
    gb.configure_index('idx')
    gb.configure_column('idx', {"sortable":True, 'initialWidth':89, 'sort':'desc'})
    gb.configure_column('message', {'width':1250, "wrapText": True, "autoHeight": True, "sortable":True,
                                    'editable':True, 
                                    'cellEditorPopup': True,
                                    'cellStyle': {'fontSize': '15px'}
                                    }
                                    )
    go = gb.build()

    st_custom_grid(
        username=st.session_state["username"], 
        api=f_api,
        api_update=None,
        refresh_sec=varss.get('refresh_sec'), 
        refresh_cutoff_sec=varss.get('seconds_to_market_close'), 
        prod=st.session_state['prod'],
        grid_options=go,
        key=f'{grid_key}',
        button_name='insight',
        buttons=[],
        api_url=None,
        # kwargs from here
        api_key=os.environ.get("fastAPI_key"),
        prompt_message ="message",
        prompt_field = "idx", # "current_macd_tier",
        log_file=log_file,
        toggle_views=toggle_views,
        grid_height='350px',

    ) 

    return True


def log_grid(KING):
    ip_address = st.session_state['ip_address']
    log_files = os.path.join(st.session_state['db_root'], 'logs')
    log_file_options = os.listdir(log_files)
    log_file_options = [i for i in log_file_options if i.endswith(".log")]
    log_file = st.sidebar.selectbox("log Files", options=log_file_options, index=log_file_options.index('log_queen.log'))
    log_file = os.path.join(log_files, log_file)
    api=f'{ip_address}/api/data/queen_messages_logfile'
    with st.expander("Logs"):
        queen_messages_logfile_grid(KING, log_file, grid_key='queen_logfile', f_api=api, varss={'seconds_to_market_close': None, 'refresh_sec': None}, toggle_views=[])
    
    return True

def sneak_peak_form():
    # if st.session_state['SneakQueen']:
    # if cust_Button("misc/bee.png", hoverText='SneakPeak', key='SneakQueen', default=False, height=f'53px'): # "https://cdn.onlinewebfonts.com/svg/img_562964.png"
    with st.form("Sneak Peak Access"):
        st.session_state["sneak_peak"] = True
        sneak_name = st.text_input("Your Name", key='sneak_name')
        sneak_pw = st.text_input("Sneak Key", key='sneak_key')
        if st.form_submit_button("Watch a Live Bot"):
            # if len(sneak_name) == 0:
            #     st.error("Enter Your Name To Get In")
            #     st.stop()
            # if sneak_pw.lower() != os.environ.get("quantqueen_pw"):
            #     st.error("Incorrect Password")
            #     st.stop()
            st.session_state['sneak_pw'] = os.environ.get("quantqueen_pw")
            switch_page("LiveBot")
            
            return True
    
    return False


def display_for_unAuth_client_user(pct_queens_taken=89):
    # newuser = st.button("New User")
    # signin_button = st.button("SignIn")

    
    cols = st.columns((6, 7, 2))
    # with cols[0]:
    #     st.subheader("Create an Account To Get a QueenTraderBot")
    # with cols[1]:
    #     progress_bar(
    #         value=pct_queens_taken, text=f"{100-pct_queens_taken} Trading Bots Available"
    #     )
    # with cols[2]:
    sneak_peak_form()

                    

    page_line_seperator("25")
    # sneak_peak = st.button("Watch a QueenBot Trade Live")
    # if sneak_peak:
        # switch_page("LiveBot")
    # st.error(
    #     "ONLY a limited number of Queens Available!! Please contact pollenq.queen@gmail.com for any questions"
    # )

    page_line_seperator("1")


def page_tab_permission_denied(admin, st_stop=True):
    if admin == False:
        st.warning("permission denied you need a Queen to access")
        if st_stop:
            st.info("Page Stopped")
            st.stop()


def page_line_seperator(height="3", border="none", color="#C5B743"):
    return st.markdown(
        """<hr style="height:{}px;border:{};color:#333;background-color:{};" /> """.format(
            height, border, color
        ),
        unsafe_allow_html=True,
    )


def write_flying_bee(width="45", height="45", frameBorder="0"):
    return st.markdown(
        '<iframe src="https://giphy.com/embed/ksE4eFvxZM3oyaFEVo" width={} height={} frameBorder={} class="giphy-embed" allowFullScreen></iframe><p><a href="https://giphy.com/gifs/bee-traveling-flying-into-next-week-like-ksE4eFvxZM3oyaFEVo"></a></p>'.format(
            width, height, frameBorder
        ),
        unsafe_allow_html=True,
    )


def hexagon_gif(width="45", height="45", frameBorder="0"):
    return st.sidebar.markdown(
        '<iframe src="https://giphy.com/embed/Wv35RAfkREOSSjIZDS" width={} height={} frameBorder={} class="giphy-embed" allowFullScreen></iframe><p><a href="https://giphy.com/gifs/star-12-hexagon-Wv35RAfkREOSSjIZDS"></a></p>'.format(
            width, height, frameBorder
        ),
        unsafe_allow_html=True,
    )


def url_gif(
    gif_path="https://giphy.com/embed/Wv35RAfkREOSSjIZDS",
    width="33",
    height="33",
    frameBorder="0",
    sidebar=False,
):
    if sidebar:
        st.sidebar.markdown(
            f'<iframe src={gif_path} width={width} height={height} frameBorder={frameBorder} class="giphy-embed" allowFullScreen></iframe><p><a href={gif_path}></a></p>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<iframe src={gif_path} width={width} height={height} frameBorder={frameBorder} class="giphy-embed" allowFullScreen></iframe><p><a href={gif_path}></a></p>',
            unsafe_allow_html=True,
        )

    return True


def return_image_upon_save(title="Saved", width=33, gif=power_gif):
    local_gif(gif_path=gif)
    st.success(title)

def local_gif(gif_path, width="33", height="33", sidebar=False, url=False):
    if url:
        data_url = data_url
    else:
        with open(gif_path, "rb") as file_:
            contents = file_.read()
            data_url = base64.b64encode(contents).decode("utf-8")
        if sidebar:
            st.sidebar.markdown(
                f'<img src="data:image/gif;base64,{data_url}" width={width} height={height} alt="bee">',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<img src="data:image/gif;base64,{data_url}" width={width} height={height} alt="bee">',
                unsafe_allow_html=True,
            )

    return True

    def markdown_logo(LOGO_IMAGE):
        st.markdown(
            """
            <style>
            .container {
                display: flex;
            }
            .logo-text {
                font-weight:700 !important;
                font-size:50px !important;
                color: #f9a01b !important;
                padding-top: 75px !important;
            }
            .logo-img {
                float:right;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="container">
                <img class="logo-img" src="data:image/png;base64,{base64.b64encode(open(LOGO_IMAGE, "rb").read()).decode()}">
                <p class="logo-text">Logo Much ?</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def flying_bee_gif(width="33", height="33", sidebar=False):
    with open(os.path.join(jpg_root, "flyingbee_gif_clean.gif"), "rb") as file_:
        contents = file_.read()
        data_url = base64.b64encode(contents).decode("utf-8")
        if sidebar:
            st.sidebar.markdown(
                f'<img src="data:image/gif;base64,{data_url}" width={width} height={height} alt="bee">',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<img src="data:image/gif;base64,{data_url}" width={width} height={height} alt="bee">',
                unsafe_allow_html=True,
            )

def pollen__story(df):
    with st.expander("pollen story", expanded=False):
        df_write = df.astype(str)
        st.dataframe(df_write)
        pass


def grid_height(len_of_rows):
    if len_of_rows > 10:
        grid_height = 333
    elif len_of_rows == 1:
        grid_height = 89
    else:
        grid_height = round(len_of_rows * 40, 0)

    return grid_height


def queens_orders__aggrid_v2(
    data,
    active_order_state_list,
    reload_data=False,
    fit_columns_on_grid_load=False,
    height=200,
    update_mode_value=GridUpdateMode.SELECTION_CHANGED,
    paginationOn=False,
    allow_unsafe_jscode=True,
    buttons=True):

    data["money"] = pd.to_numeric(data["money"], errors='coerce')
    data["honey"] = pd.to_numeric(data["honey"], errors='coerce')
    data["honey"] = data["honey"] * 100

    data["color"] = np.where(data["honey"] > 0, "green", "white")
    gb = GridOptionsBuilder.from_dataframe(data, min_column_width=30)

    if paginationOn:
        gb.configure_pagination(paginationAutoPageSize=True)  # Add pagination

    gb.configure_side_bar()  # Add a sidebar

    # gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection

    honey_colors = JsCode(
        """
    function(params) {
        if (params.value > 0) {
            return {
                'color': '#168702',
            }
        }
        else if (params.value < 0) {
            return {
                'color': '#F03811',
            }
        }
    };
    """
    )


    # Config Columns (list selection, buttons, and tagged columns ), does the immutable grid get rebuilt by row, cell, or entire grid is a re-render
    gb.configure_column("queen_order_state",
        header_name="State",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={"values": active_order_state_list},
        pinned='right',
        initialWidth=89,
    )
    gb.configure_column("datetime",
        pinned='right',
        header_name="Date",
        type=["dateColumnFilter", "customDateTimeFormat"],
        custom_format_string="MM/dd/yy HH:mm",
        pivot=True,
        initialWidth=133,
        # maxWidth=133,
        autoSize=True,
    )
    gb.configure_column("symbol",
        # pinned="left",
        pivot=True,
        resizable=True,
        initialWidth=89,
        autoSize=True,
    )
    gb.configure_column("trigname",
        # pinned="left",
        header_name="TrigBee",
        pivot=True,
        wrapText=True,
        resizable=True,
        initialWidth=100,
        maxWidth=120,
        autoSize=True,
    )
    gb.configure_column("ticker_time_frame",
        pinned="left",
        header_name="Star",
        pivot=True,
        resizable=True,
        initialWidth=138,
        autoSize=True,
    )
    gb.configure_column("honey", # immutable
        header_name="Honey%",
        pinned="left",
        cellStyle=honey_colors,
        type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"],
        custom_currency_symbol="%",
        resizable=True,
        initialWidth=89,
        maxWidth=100,
        autoSize=True,
    )
    gb.configure_column("money", # immutable
        header_name="Money$",
        pinned="left",
        cellStyle=honey_colors,
        type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"],
        custom_currency_symbol="$",
        resizable=True,
        initialWidth=89,
        maxWidth=100,
        autoSize=True,
    )
    gb.configure_column("honey_time_in_profit",
        header_name="Time.In.Honey",
        resizable=True,
        initialWidth=89,
        maxWidth=120,
        autoSize=True,
    )
    gb.configure_column("filled_qty",
        wrapText=True,
        resizable=True,
        initialWidth=95,
        maxWidth=100,
        autoSize=True,
    )
    gb.configure_column("qty_available",
        header_name="available_qty",
        autoHeight=True,
        wrapText=True,
        resizable=True,
        initialWidth=105,
        maxWidth=130,
        autoSize=True,
    )
    gb.configure_column("filled_avg_price",
        type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"],
        custom_currency_symbol="$",
        header_name="filled_avg_price",
        autoHeight=True,
        wrapText=True,
        resizable=True,
        initialWidth=120,
        maxWidth=130,
        autoSize=True,
    )
    gb.configure_column("limit_price",
        type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"],
        custom_currency_symbol="$",
        resizable=True,
        initialWidth=95,
        maxWidth=100,
        autoSize=True,
    )
    gb.configure_column("cost_basis",
        type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"],
        custom_currency_symbol="$",
        autoHeight=True,
        wrapText=True,
        resizable=True,
        initialWidth=110,
        maxWidth=120,
        autoSize=True,
    )
    gb.configure_column("wave_amo",
        type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"],
        custom_currency_symbol="$",
        autoHeight=True,
        wrapText=True,
        resizable=True,
        initialWidth=110,
        maxWidth=120,
        autoSize=True,
    )
    # gb.configure_column("order_rules",
    #     header_name="OrderRules",
    #     wrapText=True,
    #     resizable=True,
    #     autoSize=True,
    # )

    # ## WHY IS IT NO WORKING???
    # k_sep_formatter = JsCode("""
    # function(params) {
    #     return (params.value == null) ? params.value : params.value.toLocaleString('en-US',{style: "currency", currency: "USD"});
    # }
    # """)

    # int_cols = ['money', 'filled_avg_price', 'cost_basis', 'wave_amo', 'honey']
    # gb.configure_columns(int_cols, valueFormatter=k_sep_formatter)
    # for int_col in int_cols:
    #     gb.configure_column(int_col, type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="$")
    # color code columns based on yourValue
    # BtnCellRenderer = JsCode(
    #     """
    #         function addBtn(params) { return '<button style="background-color:yellow;z-index: 1;
    #         margin: 5px;
    #         left: 0;
    #         top: 0;
    #         bottom:0;
    #         right:0;
    #         width: 100%;
    #         height: 100%;">OrderRules</button>'; }
    #     """
    # )
    # an example based on https://www.ag-grid.com/javascript-data-grid/component-cell-renderer/#simple-cell-renderer-example
    BtnCellRenderer = JsCode(
        """
    class BtnCellRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
            <span>
                <button id='click-button'
                    class='btn-simple'
                    style='color: ${this.params.color}; background-color: ${this.params.background_color}'>OrderRules</button>
            </span>
        `;

            this.eButton = this.eGui.querySelector('#click-button');

            this.btnClickedHandler = this.btnClickedHandler.bind(this);
            this.eButton.addEventListener('click', this.btnClickedHandler);

        }

        getGui() {
            return this.eGui;
        }

        refresh() {
            return true;
        }

        destroy() {
            if (this.eButton) {
                this.eGui.removeEventListener('click', this.btnClickedHandler);
            }
        }

        btnClickedHandler(event) {
            if (confirm(this.params.data.order_rules) == true) {
                if(this.params.getValue() == 'clicked') {
                    this.refreshTable('');
                } else {
                    this.refreshTable('clicked');
                }
                    console.log(this.params);
                    console.log(this.params.getValue());
                }
            }

        refreshTable(value) {
            this.params.setValue(value);
        }
    };
    """
    )

    BtnCellRendererSell = JsCode(
        """
    class BtnCellRendererSell {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
            <span>
                <button id='click-button_sell'
                    class='btn-simple'
                    style='color: ${this.params.color}; background-color: ${this.params.background_color}'>Sell</button>
            </span>
        `;

            this.eButton = this.eGui.querySelector('#click-button_sell');

            this.btnClickedHandler = this.btnClickedHandler.bind(this);
            this.eButton.addEventListener('click', this.btnClickedHandler);

        }

        getGui() {
            return this.eGui;
        }

        refresh() {
            return true;
        }

        destroy() {
            if (this.eButton) {
                this.eGui.removeEventListener('click', this.btnClickedHandler);
            }
        }

        btnClickedHandler(event) {
            if (confirm('Are you sure you want to Sell?') == true) {
                if(this.params.getValue() == 'clicked') {
                    this.refreshTable('');
                } else {
                    this.refreshTable('clicked');
                }
                    console.log(this.params);
                    console.log(this.params.getValue());
                }
            }

        refreshTable(value) {
            this.params.setValue(value);
        }
    };
    """
    )

    BtnCellRendererState = JsCode(
        """
    class BtnCellRendererState {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
            <span>
                <button id='click-button_state'
                    class='btn-simple'
                    style='color: ${this.params.color}; background-color: ${this.params.background_color}'>Change</button>
            </span>
        `;

            this.eButton = this.eGui.querySelector('#click-button_state');

            this.btnClickedHandler = this.btnClickedHandler.bind(this);
            this.eButton.addEventListener('click', this.btnClickedHandler);

        }

        getGui() {
            return this.eGui;
        }

        refresh() {
            return true;
        }

        destroy() {
            if (this.eButton) {
                this.eGui.removeEventListener('click', this.btnClickedHandler);
            }
        }

        btnClickedHandler(event) {
            if (confirm('Are you sure you want to Change State?') == true) {
                if(this.params.getValue() == 'clicked') {
                    this.refreshTable('');
                } else {
                    this.refreshTable('clicked');
                }
                    console.log(this.params);
                    console.log(this.params.getValue());
                }
            }

        refreshTable(value) {
            this.params.setValue(value);
        }
    };
    """
    )

    click_button_function = """function selectAllAmerican(e) {
                e.node.setSelected(true);}
        """

    gb.configure_column("orderrules",
        headerTooltip="OrderRules",
        editable=False,
        filter=False,
        onCellClicked=JsCode(click_button_function),
        cellRenderer=BtnCellRenderer,
        autoHeight=True,
        wrapText=False,
        lockPosition="right",
        pinned="right",
        sorteable=True,
        suppressMenu=True,
        maxWidth=100,
    )   
    if buttons:
        gb.configure_column("orderstate",
            headerTooltip="Change Order State",
            editable=False,
            filter=False,
            onCellClicked=JsCode(click_button_function),
            cellRenderer=BtnCellRendererState,
            autoHeight=True,
            wrapText=False,
            lockPosition="right",
            pinned="right",
            sorteable=True,
            suppressMenu=True,
            maxWidth=100,
        )
        gb.configure_column("sell",
            headerTooltip="SellAll",
            editable=False,
            filter=False,
            onCellClicked=JsCode(click_button_function),
            cellRenderer=BtnCellRendererSell,
            autoHeight=True,
            wrapText=False,
            lockPosition="right",
            pinned="right",
            sorteable=True,
            suppressMenu=True,
            maxWidth=100,
        )

    gridOptions = gb.build()

    gridOptions["wrapHeaderText"] = "true"
    gridOptions["autoHeaderHeight"] = "true"
    gridOptions["rememberGroupStateWhenNewData"] = "true"
    gridOptions["enableCellTextSelection"] = "true"
    gridOptions["resizable"] = False
    gridOptions["getRowStyle"] = JsCode(
        """
    function(params) {
        if (params.data["color"] == 'green') {
            return {
                'backgroundColor': '#C9A500'
            }
        } else if (params.data["color"] == 'white') {
            return {
                'backgroundColor': '#ffe680'
            }
        }
    };
    """
    )

    grid_response = AgGrid(
        data,
        gridOptions=gridOptions,
        data_return_mode="AS_INPUT",
        update_mode=update_mode_value,
        fit_columns_on_grid_load=fit_columns_on_grid_load,
        # theme="streamlit", #Add theme color to the table
        enable_enterprise_modules=True,
        height=height,
        reload_data=reload_data,
        allow_unsafe_jscode=allow_unsafe_jscode,
    )

    return grid_response




def standard_AGgrid(
    data,
    reload_data=False,
    configure_side_bar=False,
    fit_columns_on_grid_load=False,
    height=500,
    update_mode_value="NO_UPDATE",
    paginationOn=False,
    use_checkbox=False,
    hide_cols=[],
    grid_type=False
):
    # ['NO_UPDATE', # 'MANUAL',# 'VALUE_CHANGED',    # 'SELECTION_CHANGED',# 'FILTERING_CHANGED',# 'SORTING_CHANGED',  # 'COLUMN_RESIZED',   # 'COLUMN_MOVED',     # 'COLUMN_PINNED',    # 'COLUMN_VISIBLE',   # 'MODEL_CHANGED',# 'COLUMN_CHANGED', # 'GRID_CHANGED']
    gb = GridOptionsBuilder.from_dataframe(data, min_column_width=30)
    gb.configure_default_column(column_width=85, resizable=True, autoSize=True, textWrap=True, wrapHeaderText=True, autoHeaderHeight=True, autoHeight=True, suppress_menu=False, filterable=True, sortable=True)
    gb.configure_grid_options(enableRangeSelection=True, copyHeadersToClipboard=False)
    if paginationOn:
        gb.configure_pagination(paginationAutoPageSize=True)  # Add pagination
    if configure_side_bar:
        gb.configure_side_bar()  # Add a sidebar

    if use_checkbox:
        gb.configure_selection('multiple', use_checkbox=use_checkbox, groupSelectsChildren="Group checkbox select children") 
    if grid_type == 'king_users':
        gb.configure_column("queen_authorized",
            editable=True,
            cellEditor="agSelectCellEditor",
            cellEditorParams={"values": ['active', 'not_active']},
            lockPosition="left",
        )

    if hide_cols:
        for col in hide_cols:
            gb.configure_column(col, hide=True)
    gridOptions = gb.build()
    gridOptions["rememberGroupStateWhenNewData"] = "true"
    gridOptions["resizable"] = "true"
    gridOptions["wrapHeaderText"] = "true"

    grid_response = AgGrid(
        data,
        gridOptions=gridOptions,
        data_return_mode="AS_INPUT",
        update_mode=update_mode_value,
        fit_columns_on_grid_load=fit_columns_on_grid_load,
        enable_enterprise_modules=True,
        height=height,
        reload_data=reload_data,
        allow_unsafe_jscode=True,
    )

    return grid_response



def download_df_as_CSV(df, button_name="download csv", file_name="name.csv"):
    def convert_df_to_csv(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode("utf-8")

    st.download_button(
        label=button_name,
        data=convert_df_to_csv(df),
        file_name=file_name,
        mime="text/csv",
    )

    return True

# def custom_fastapi_text(KING, client_user, default_background_color, default_text_color, default_font, refresh_sec=8, refresh_cutoff_sec=8, text_size=24, prod=False, api="http://localhost:8000/api/data/account_info", key='header1'):
#     # Total Account info
#     to_builder = TextOptionsBuilder.create()
#     to_builder.configure_background_color(default_background_color)
#     to_builder.configure_text_color(default_text_color)
#     to_builder.configure_font_style(default_font)
#     to = to_builder.build()
#     custom_text(api=api, 
#                 text_size=text_size, 
#                 refresh_sec=refresh_sec,
#                 refresh_cutoff_sec=refresh_cutoff_sec,
#                 text_option=to, 
#                 api_key=os.environ.get("fastAPI_key"), 
#                 prod=prod, 
#                 username=KING['users_allowed_queen_emailname__db'].get(client_user),
#                 client_user=client_user,
#                 key=key,)            

#     return True


def queen_order_flow(QUEEN, active_order_state_list, order_buttons=False):

    now_time = datetime.now(est)
    cols = st.columns((1,3, 1, 1, 1, 1, 1))
    with cols[0]:
        refresh_b = st.button("Refresh", key="r1")
        edit_orders= st.checkbox("edit_orders", key='edit_orders')
    with cols[2]:
        today_orders = st.checkbox("Today", False)
        page_line_seperator(.2)
        if today_orders:
            st.image(mainpage_bee_png, width=33)
    with cols[3]:
        completed_orders = st.checkbox("Completed")
        page_line_seperator(.2)
        if completed_orders:
            st.image(mainpage_bee_png, width=33)
    with cols[4]:
        all_orders = st.checkbox("All", False)
        page_line_seperator(.2)
        if all_orders:
            st.image(mainpage_bee_png, width=33)
    with cols[5]:
        best_orders = st.checkbox("Best Bees")
        page_line_seperator(.2)
        if best_orders:
            st.image(mainpage_bee_png, width=33)
    with cols[6]:
        show_errors = st.checkbox("Lost Bees")
        page_line_seperator(.2)
        if show_errors:
            st.image(mainpage_bee_png, width=33)

    order_states = set(QUEEN["queen_orders"]["queen_order_state"].tolist())

    if all_orders:
        order_states = order_states
    elif completed_orders:
        order_states = ["completed", "completed_alpaca"]
    elif show_errors:
        order_states = ["error"]
    else:
        order_states = ["submitted", "running", "running_close"]

    with cols[1]:
        queen_order_states = st.multiselect(
            "queen order states",
            options=list(active_order_state_list),
            default=order_states,
        )
    cols = st.columns((1, 1, 10, 5))

    df = queen_orders_view(
        QUEEN=QUEEN, queen_order_state=queen_order_states, return_str=False
    )["df"]
    if len(df) == 0:
        st.info("No Orders to View")
        return False

    if today_orders:
        df = df[df["datetime"] > now_time.replace(hour=1, minute=1, second=1)].copy()

    g_height = grid_height(len_of_rows=len(df))
    set_grid_height = st.sidebar.number_input(
        label=f"Set Orders Grid Height", value=g_height
    )
    # with cols[1]:
    with cols[0]:
        mark_down_text(text=f'% {round(sum(df["honey"]) * 100, 2)}', fontsize="18")
    with cols[1]:
        mark_down_text(text=f'$ {round(sum(df["money"]), 2)}', fontsize="18")
    cols = st.columns((1, 1, 10))

    ordertables__agrid = queens_orders__aggrid_v2(
        data=df.astype(str),
        active_order_state_list=active_order_state_list,
        reload_data=False,
        height=set_grid_height,
        buttons=order_buttons
    )
    
    download_df_as_CSV(df=ordertables__agrid["data"], file_name="orders.csv")

    return ordertables__agrid


# def page_session_state__cleanUp(page):
#     if page == 'QueensConscience':
#         st.session_state['option_sel'] = False
#         st.session_state['sneak_peak'] = False
#         st.session_state['last_page'] = page
    
#     return True



def init_client_user_secrets(
    prod_keys_confirmed=False,
    sandbox_keys_confirmed=False,
    APCA_API_KEY_ID_PAPER="init",
    APCA_API_SECRET_KEY_PAPER="init",
    APCA_API_KEY_ID="init",
    APCA_API_SECRET_KEY="init",
    datetimestamp_est=datetime.now(est),
):
    return {
        "prod_keys_confirmed": prod_keys_confirmed,
        "sandbox_keys_confirmed": sandbox_keys_confirmed,
        # 'client_user': client_user,
        "APCA_API_KEY_ID_PAPER": APCA_API_KEY_ID_PAPER,
        "APCA_API_SECRET_KEY_PAPER": APCA_API_SECRET_KEY_PAPER,
        "APCA_API_KEY_ID": APCA_API_KEY_ID,
        "APCA_API_SECRET_KEY": APCA_API_SECRET_KEY,
        "datetimestamp_est": datetimestamp_est,
    }


def test_api_keys(user_secrets, prod=False):
    APCA_API_KEY_ID_PAPER = user_secrets["APCA_API_KEY_ID_PAPER"]
    APCA_API_SECRET_KEY_PAPER = user_secrets["APCA_API_SECRET_KEY_PAPER"]
    APCA_API_KEY_ID = user_secrets["APCA_API_KEY_ID"]
    APCA_API_SECRET_KEY = user_secrets["APCA_API_SECRET_KEY"]

    if prod:
        try:
            base_url = "https://api.alpaca.markets"
            rest = AsyncRest(key_id=APCA_API_KEY_ID, secret_key=APCA_API_SECRET_KEY)

            api = tradeapi.REST(
                key_id=APCA_API_KEY_ID,
                secret_key=APCA_API_SECRET_KEY,
                base_url=URL(base_url),
                api_version="v2",
            )
            api.get_snapshot("SPY")
            api_true = True
        except Exception as e:
            api_true = False
    else:
        try:
            base_url = "https://paper-api.alpaca.markets"
            rest = AsyncRest(
                key_id=APCA_API_KEY_ID_PAPER, secret_key=APCA_API_SECRET_KEY_PAPER
            )

            api = tradeapi.REST(
                key_id=APCA_API_KEY_ID_PAPER,
                secret_key=APCA_API_SECRET_KEY_PAPER,
                base_url=URL(base_url),
                api_version="v2",
            )
            api.get_snapshot("SPY")
            api_true = True
        except Exception as e:
            api_true = False

    return api_true


def pollenq_button_source():
    return{
        'chess_board': False,
        'waves_queen_qk_source_toggle': [
        {'id': "waves_revrec", 'icon': "fas fa-chess-pawn", 'label':"RevRec Refresh"},
        {'id': "waves_revrec_queen", 'icon':"fas fa-chess-queen",'label':"Queen RevRec"},
        {'id': "waves_revrec_king", 'icon': "fas fa-chess-king", 'label':"King RevRec"},
        ],
        'option_data_orders': [
        # {'id': 'main_queenmind', 'icon': "fas fa-chess-queen", 'label':""},
        {'id': "orders", 'icon':"fas fa-chess-king",'label':"on"},
        {'id': "", 'icon':"fas fa-chess-pawn",'label':"off"},
        ],
        'charts_option_data': [
        {'id': "", 'icon':"fas fa-chess-pawn",'label':"off"},
        {'id': "charts_id", 'icon': "fa fa-signal", 'label':"on"},
        ],

        'board_option_data': [
        {'id': "chess_board", 'icon': "fas fa-chess-board", 'label':"on"},
        {'id': "", 'icon':"fas fa-chess-pawn",'label':"off"},
        {'id': "admin_workerbees", 'icon':"fas fa-chess-queen",'label':"admin"},
        ],
        
        'option_data_qm': [
        {'id': 'main_queenmind', 'icon': "fas fa-chess-queen", 'label':"on"},
        {'id': "admin_workerbees", 'icon':"fas fa-chess-king",'label':"admin"},
        ],
        'workerbees_option_data': [
        {'id': "", 'icon': "fas fa-chess-pawn", 'label':"off"},
        {'id': "workerbees", 'icon': "fa fa-star", 'label':"on"},
        ],

        'option_heart': [{'id': "heartbeat", 'icon':"fas fa-heart",'label':"heartbeat"},],
        'option_chart': [{'id': "show_charts", 'icon':"fa fa-bar-chart",'label':"on"}, {'id': "no_charts", 'icon':"fa fa-toggle-off",'label':"off"}, ],
        'pawn_option_data': [
        {'id': "chess_board", 'icon': "fas fa-chess-pawn", 'label':"on"},
        ],
        'castle_option_data': [
        {'id': "rook", 'icon': "fas fa-chess-rook", 'label':"castle"},
        ],
        'bishop_option_data': [
        {'id': "bishop", 'icon': "fas fa-chess-bishop", 'label':"bishop"},
        ],
        'knight_option_data': [
        {'id': "knight", 'icon': "fas fa-chess-knight", 'label':"knight"},
        ],
        'chess_option_data': [
        {'id': "chess_search", 'icon': "fas fa-chess", 'label':"search"},
        ],
        'charts_day_option_data': [
        {'id': "charts_dayonly_no", 'icon': "", 'label':"no"},
        {'id': "charts_dayonly_yes", 'icon': "", 'label':"yes"},
        ],
        'coin_option_data': [
        {'id': "coins", 'icon': "fas fa-chess-bishop", 'label':"coins"},
        ],

    }

def queen__account_keys(QUEEN_KING, authorized_user, show_form=False):
    if authorized_user == False:
        return False
    # view_account_button = st.sidebar.button("Update API Keys", key='sidebar_key')
    cols = st.columns((4, 1, 4))

    prod = st.session_state["prod"]
    table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
    user_env_instance = "prod" if st.session_state["prod"] else "sandbox"
    keys_confirmed = QUEEN_KING["users_secrets"][f"{user_env_instance}_keys_confirmed"]
    view_account_keys = False

    if keys_confirmed == False:
        with cols[0]:
            st.error(
                f"Enter Your API Keys To Activate {user_env_instance} QueenTraderBot"
            )
        with cols[1]:
            # view_account_button = st.button("Update API Keys", key='main_key')
            view_account_keys = True
            # with cols[2]:
            local_gif(gif_path=runaway_bee_gif, height=33, width=33)

    if view_account_keys or show_form:
        with st.form("account keys"):
            # local_gif(gif_path=runaway_bee_gif, height=33, width=33)
            st.session_state["account_keys"] = True
            if prod:
                st.write("# Production LIVE")
                APCA_API_KEY_ID = st.text_input(
                    label=f"APCA_API_KEY_ID",
                    value=QUEEN_KING["users_secrets"]["APCA_API_KEY_ID"],
                    key=f"APCA_API_KEY_ID",
                )
                APCA_API_SECRET_KEY = st.text_input(
                    label=f"APCA_API_SECRET_KEY",
                    value=QUEEN_KING["users_secrets"]["APCA_API_SECRET_KEY"],
                    key=f"APCA_API_SECRET_KEY",
                )
                user_secrets = init_client_user_secrets(
                    prod_keys_confirmed=False,
                    sandbox_keys_confirmed=False,
                    APCA_API_KEY_ID_PAPER=None,
                    APCA_API_SECRET_KEY_PAPER=None,
                    APCA_API_KEY_ID=APCA_API_KEY_ID,
                    APCA_API_SECRET_KEY=APCA_API_SECRET_KEY,
                )

            else:
                st.write("# SandBox Paper")
                APCA_API_KEY_ID_PAPER = st.text_input(
                    label=f"APCA_API_KEY_ID_PAPER",
                    value=QUEEN_KING["users_secrets"]["APCA_API_KEY_ID_PAPER"],
                    key=f"APCA_API_KEY_ID_PAPER",
                )
                APCA_API_SECRET_KEY_PAPER = st.text_input(
                    label=f"APCA_API_SECRET_KEY_PAPER",
                    value=QUEEN_KING["users_secrets"]["APCA_API_SECRET_KEY_PAPER"],
                    key=f"APCA_API_SECRET_KEY_PAPER",
                )
                user_secrets = init_client_user_secrets(
                    prod_keys_confirmed=False,
                    sandbox_keys_confirmed=False,
                    APCA_API_KEY_ID_PAPER=APCA_API_KEY_ID_PAPER,
                    APCA_API_SECRET_KEY_PAPER=APCA_API_SECRET_KEY_PAPER,
                    APCA_API_KEY_ID=None,
                    APCA_API_SECRET_KEY=None,
                )
            
            st.warning("NEVER EVER Share your API KEYS WITH ANYONE!")

            if st.form_submit_button("Save API Keys"):
                print("SAVE KEYS")
                # test keys
                if test_api_keys(user_secrets=user_secrets, prod=prod):
                    print("SAVE KEYS")
                    st.success(f"{user_env_instance} Keys Added Refreshing Page")
                    user_secrets[f"{user_env_instance}_keys_confirmed"] = True
                    QUEEN_KING["users_secrets"] = user_secrets
                    if pg_migration:
                        
                        PollenDatabase.upsert_data(table_name=QUEEN_KING.get('table_name'), key=QUEEN_KING.get('key'), value=QUEEN_KING)
                    else:
                        PickleData(QUEEN_KING.get('source'), QUEEN_KING, console=True)
                    # switch_page('pollen')
                else:
                    st.error(f"{user_env_instance} Keys Failed")
                    user_secrets[f"{user_env_instance}_keys_confirmed"] = False


    return True




############### Charts ##################

def create_main_macd_chart(df, width=850, height=450):
    try:
        title = df.iloc[-1]['name']

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])

        df['chartdate_'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')
        df['cross'] = np.where(df['macd_cross'].str.contains('cross'), df['macd'], 0)
        
        fig.add_ohlc(x=df['chartdate_'], close=df['close'], open=df['open'], low=df['low'], high=df['high'], name='price')
        fig.add_scatter(x=df['chartdate_'], y=df['vwap'], mode="lines", row=1, col=1, name='vwap')
        fig.add_scatter(x=df['chartdate_'], y=df['macd'], mode="lines", row=2, col=1, name='mac')
        fig.add_scatter(x=df['chartdate_'], y=df['signal'], mode="lines", row=2, col=1, name='signal')
        fig.add_bar(x=df['chartdate_'], y=df['hist'], row=2, col=1, name='hist')
        
        fig.add_scatter(x=df['chartdate_'], y=df['cross'], mode='lines', row=2, col=1, name='cross',) # line_color='#00CC96')
        # fig.add_scatter(x=df['chartdate'], y=df['cross'], mode='markers', row=1, col=1, name='cross',) # line_color='#00CC96')
        fig.update_layout(title_text=title, width=width, height=height)
        fig.update_xaxes(showgrid=False, rangeslider_visible=False)
        fig.update_yaxes(showgrid=False)
        # fig.update_layout(sliders=False)
        return fig
    except Exception as e:
        print_line_of_error(e)


def create_guage_chart(title, value=.01):

    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 25}},
        delta = {'reference':.4 , 'increasing': {'color': "RebeccaPurple"}},
        gauge = {
            'axis': {'range': [1, -1], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': '#ffe680'},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [-1, -.5], 'color': 'red'},
                {'range': [1, .6], 'color': 'royalblue'}],
            'threshold': {
                'line': {'color': "red", 'width': 3},
                'thickness': 0.60,
                'value': 1}}))

    # fig.update_layout(paper_bgcolor = "lavender", font = {'color': "darkblue", 'family': "Arial"})
    fig.update_layout(height=289, width=350)

    return fig


def create_wave_chart(df):
    title = f'buy+sell cross __waves {df.iloc[-1]["name"]}'
    # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01)
    # df.set_index('timestamp_est')
    # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
    df = df.copy()
    df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')

    fig.add_bar(x=df['chartdate'], y=df['buy_cross-0__wave'],  row=1, col=1, name='buycross wave')
    fig.add_bar(x=df['chartdate'], y=df['sell_cross-0__wave'],  row=1, col=1, name='sellcross wave')
    fig.update_layout(height=600, width=900, title_text=title)
    return fig

def create_wave_chart_single(df, wave_col):
    title = df.iloc[-1]['name']
    # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01)
    # df.set_index('timestamp_est')
    # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
    df = df.copy()
    df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')

    fig.add_bar(x=df['chartdate'], y=df[wave_col],  row=1, col=1, name=wave_col)
    fig.update_layout(height=600, width=900, title_text=title)
    return fig


def create_slope_chart(df):
    title = df.iloc[-1]['name']
    # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01)
    # df.set_index('timestamp_est')
    # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
    df = df.copy()
    df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')
    slope_cols = [i for i in df.columns if 'slope' in i]
    for col in slope_cols:
        df[col] = pd.to_numeric(df[col])
        df[col] = np.where(abs(df[col])>5, 0, df[col])
    fig.add_scatter(x=df['chartdate'], y=df['hist_slope-3'], mode="lines", row=1, col=1, name='hist_slope-3')
    fig.add_scatter(x=df['chartdate'], y=df['hist_slope-6'], mode="lines", row=1, col=1, name='hist_slope-6')
    # fig.add_scatter(x=df['chartdate'], y=df['hist_slope-23'], mode="lines", row=1, col=1, name='hist_slope-23')
    fig.add_scatter(x=df['chartdate'], y=df['macd_slope-3'], mode="lines", row=2, col=1, name='macd_slope-3')
    fig.add_scatter(x=df['chartdate'], y=df['macd_slope-6'], mode="lines", row=2, col=1, name='macd_slope-6')
    # fig.add_scatter(x=df['chartdate'], y=df['macd_slope-23'], mode="lines", row=2, col=1, name='macd_slope-23')
    fig.update_layout(height=600, width=900, title_text=title)
    return fig


def create_wave_chart_all(df, wave_col):
    try:
        title = df.iloc[-1]['name']
        # st.markdown('<div style="text-align: center;">{}</div>'.format(title), unsafe_allow_html=True)
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01)
        # df.set_index('timestamp_est')
        # df['chartdate'] = f'{df["chartdate"].day}{df["chartdate"].hour}{df["chartdate"].minute}'
        df = df.copy()
        # df['chartdate'] = df['chartdate'].apply(lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}')
        # df[f'{wave_col}{"_number"}'] = df[f'{wave_col}{"_number"}'].astype(str)
        # dft = df[df[f'{wave_col}{"_number"}'] == '1'].copy()
        fig.add_bar(x=df[f'{wave_col}{"_number"}'], y=df[wave_col].values,  row=1, col=1, name=wave_col)
        fig.update_layout(height=600, width=900, title_text=title)
        return fig
    except Exception as e:
        print(e)


def example__subPlot():
    st.header("Sub Plots")
    # st.balloons()
    fig = plt.figure(figsize=(10, 5))

    # Plot 1
    data = {"C": 15, "C++": 20, "JavaScript": 30, "Python": 35}
    Courses = list(data.keys())
    values = list(data.values())

    plt.xlabel("Programming Environment")
    plt.ylabel("Number of Students")

    plt.subplot(1, 2, 1)
    plt.bar(Courses, values)

    # Plot 2
    x = np.array([35, 25, 25, 15])
    mylabels = ["Python", "JavaScript", "C++", "C"]

    plt.subplot(1, 2, 2)
    plt.pie(x, labels=mylabels)

    st.pyplot(fig)


def example__df_plotchart(title, df, y, x=False, figsize=(14, 7), formatme=False):
    st.markdown(
        '<div style="text-align: center;">{}</div>'.format(title),
        unsafe_allow_html=True,
    )
    if x == False:
        return df.plot(y=y, figsize=figsize)
    else:
        if formatme:
            df["chartdate"] = df["chartdate"].apply(
                lambda x: f'{x.month}{"-"}{x.day}{"_"}{x.hour}{":"}{x.minute}'
            )
            return df.plot(x="chartdate", y=y, figsize=figsize)
        else:
            return df.plot(x=x, y=y, figsize=figsize)


############### Charts ##################


############ utils ############
def createParser_App():
    parser = argparse.ArgumentParser()
    parser.add_argument("-qcp", default="app")
    parser.add_argument("-admin", default="false")
    # parser.add_argument ('-user', default='pollen')
    return parser


def example__callback_function__set_session_state(state, key):
    # 1. Access the widget's setting via st.session_state[key]
    # 2. Set the session state you intended to set in the widget
    st.session_state[state] = st.session_state[key]





############ utils ############



def show_waves(STORY_bee, ticker_option='SPY', frame_option='1Minute_1Day'):
    ttframe = f'{ticker_option}{"_"}{frame_option}'
    knowledge = STORY_bee[ttframe]

    # mark_down_text(text=ttframe)
    st.write("waves story -- investigate BACKEND functions")
    df = knowledge['waves']['story']
    df = df.astype(str)
    st.dataframe(df)

    st.write("buy cross waves")
    m_sort = knowledge['waves']['buy_cross-0']
    df_m_sort = pd.DataFrame(m_sort).T
    if st.button("download buy"):
        dd = download_df_as_CSV(df_m_sort, 'trigbee_cross-0.csv')
    df_m_sort = df_m_sort.astype(str)
    st.dataframe(data=df_m_sort)

    st.write("sell cross waves")
    m_sort = knowledge['waves']['sell_cross-0']
    df_m_sort = pd.DataFrame(m_sort).T
    df_m_sort = df_m_sort.astype(str)
    st.dataframe(data=df_m_sort)

    return True


def nested_grid():
    url = "https://www.ag-grid.com/example-assets/master-detail-data.json"
    df = pd.read_json(url)
    df["callRecords"] = df["callRecords"].apply(lambda x: pd.json_normalize(x))

    gridOptions = {
        # enable Master / Detail
        "masterDetail": True,
        "rowSelection": "single",
        # the first Column is configured to use agGroupCellRenderer
        "columnDefs": [
            {
                "field": "name",
                "cellRenderer": "agGroupCellRenderer",
                "checkboxSelection": True,
            },
            {"field": "account"},
            {"field": "calls"},
            {"field": "minutes", "valueFormatter": "x.toLocaleString() + 'm'"},
        ],
        "defaultColDef": {
            "flex": 1,
        },
        # provide Detail Cell Renderer Params
        "detailCellRendererParams": {
            # provide the Grid Options to use on the Detail Grid
            "detailGridOptions": {
                "rowSelection": "multiple",
                "suppressRowClickSelection": True,
                "enableRangeSelection": True,
                "pagination": True,
                "paginationAutoPageSize": True,
                "columnDefs": [
                    {"field": "callId", "checkboxSelection": True},
                    {"field": "direction"},
                    {"field": "number", "minWidth": 150},
                    {"field": "duration", "valueFormatter": "x.toLocaleString() + 's'"},
                    {"field": "switchCode", "minWidth": 150},
                ],
                "defaultColDef": {
                    "sortable": True,
                    "flex": 1,
                },
            },
            # get the rows for each Detail Grid
            "getDetailRowData": JsCode(
                """function (params) {
                    console.log(params);
                    params.successCallback(params.data.callRecords);
        }"""
            ).js_code,
        },
    }

    r = AgGrid(
        df,
        gridOptions=gridOptions,
        height=300,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
    )


def click_button_grid():
    now = int(datetime.now().timestamp())
    start_ts = now - 3 * 30 * 24 * 60 * 60

    @st.cache(allow_output_mutation=True)
    def make_data():
        df = pd.DataFrame(
            {
                "timestamp": np.random.randint(start_ts, now, 20),
                "side": [np.random.choice(["buy", "sell"]) for i in range(20)],
                "base": [np.random.choice(["JPY", "GBP", "CAD"]) for i in range(20)],
                "quote": [np.random.choice(["EUR", "USD"]) for i in range(20)],
                "amount": list(
                    map(
                        lambda a: round(a, 2),
                        np.random.rand(20) * np.random.randint(1, 1000, 20),
                    )
                ),
                "price": list(
                    map(
                        lambda p: round(p, 5),
                        np.random.rand(20) * np.random.randint(1, 10, 20),
                    )
                ),
                "clicked": [""] * 20,
            }
        )
        df["cost"] = round(df.amount * df.price, 2)
        df.insert(
            0,
            "datetime",
            df.timestamp.apply(lambda ts: datetime.fromtimestamp(ts)),
        )

        return df.sort_values("timestamp").drop("timestamp", axis=1)

    # an example based on https://www.ag-grid.com/javascript-data-grid/component-cell-renderer/#simple-cell-renderer-example
    BtnCellRenderer = JsCode(
        """
    class BtnCellRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
            <span>
                <button id='click-button'
                    class='btn-simple'
                    style='color: ${this.params.color}; background-color: ${this.params.background_color}'>Click!</button>
            </span>
        `;

            this.eButton = this.eGui.querySelector('#click-button');

            this.btnClickedHandler = this.btnClickedHandler.bind(this);
            this.eButton.addEventListener('click', this.btnClickedHandler);

        }

        getGui() {
            return this.eGui;
        }

        refresh() {
            return true;
        }

        destroy() {
            if (this.eButton) {
                this.eGui.removeEventListener('click', this.btnClickedHandler);
            }
        }

        btnClickedHandler(event) {
            if (confirm('Are you sure you want to CLICK?') == true) {
                if(this.params.getValue() == 'clicked') {
                    this.refreshTable('');
                } else {
                    this.refreshTable('clicked');
                }
                    console.log(this.params);
                    console.log(this.params.getValue());
                }
            }

        refreshTable(value) {
            this.params.setValue(value);
        }
    };
    """
    )

    df = make_data()
    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_default_column(editable=True)
    grid_options = gb.build()

    grid_options["columnDefs"].append(
        {
            "field": "clicked",
            "header": "Clicked",
            "cellRenderer": BtnCellRenderer,
            "cellRendererParams": {
                "color": "red",
                "background_color": "black",
            },
        }
    )

    st.title("cellRenderer Class Example")

    response = AgGrid(
        df,
        # theme="streamlit",
        key="table1",
        gridOptions=grid_options,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
        reload_data=False,
        try_to_convert_back_to_original_types=False,
    )

    st.write(response["data"])
    try:
        st.write(response["data"][response["data"].clicked == "clicked"])
    except:
        st.write("Nothing was clicked")


def create_ag_grid_column(
    headerName="Column Header",
    # field="dataField",
    # colId="columnId",
    type=None,
    textWrap=None,
    width=100,
    initialWidth=None,  # Add initialWidth property
    minWidth=None,
    maxWidth=None,
    sortable=True,
    filter=True,
    filterParams=None,
    resizable=True,
    pinned=None,
    lockPosition=False,
    suppressSizeToFit=False,
    cellRenderer=None,
    cellStyle=None,
    headerCheckboxSelection=False,
    checkboxSelection=False,
    headerClass=None,
    cellClass=None,
    valueGetter=None,
    valueFormatter=None,
    cellEditor=None,
    cellEditorParams=None,
    floatingFilter=False,
    floatingFilterComponent=None,
    floatingFilterComponentParams=None,
    enableRowGroup=False,
    rowGroupIndex=None,
    enablePivot=False,
    pivotIndex=None,
    aggFunc=None,
    enableValue=False,
    enableChangeDetection=False,
    enableCellChangeFlash=False,
    cellEditorPopup=False,
    cellEditorPopupParent=None,
    custom_format_string=None,
    editable=None,
    cellClassRules=None,
):
    # Create a dictionary with the provided field values
    column = {
        "headerName": headerName,
        "type": type,
        # "field": field,
        # "colId": colId,
        "width": width,
        "initialWidth": initialWidth,  # Include initialWidth property
        "minWidth": minWidth,
        "maxWidth": maxWidth,
        "sortable": sortable,
        "filter": filter,
        "filterParams": filterParams,
        "resizable": resizable,
        "pinned": pinned,
        "lockPosition": lockPosition,
        "suppressSizeToFit": suppressSizeToFit,
        "cellRenderer": cellRenderer,
        "cellStyle": cellStyle,
        "headerCheckboxSelection": headerCheckboxSelection,
        "checkboxSelection": checkboxSelection,
        "headerClass": headerClass,
        "cellClass": cellClass,
        "valueGetter": valueGetter,
        "valueFormatter": valueFormatter,
        "cellEditor": cellEditor,
        "cellEditorParams": cellEditorParams,
        "floatingFilter": floatingFilter,
        "floatingFilterComponent": floatingFilterComponent,
        "floatingFilterComponentParams": floatingFilterComponentParams,
        "enableRowGroup": enableRowGroup,
        "rowGroupIndex": rowGroupIndex,
        "enablePivot": enablePivot,
        "pivotIndex": pivotIndex,
        "aggFunc": aggFunc,
        "enableValue": enableValue,
        "enableChangeDetection": enableChangeDetection,
        "enableCellChangeFlash": enableCellChangeFlash,
        "cellEditorPopup": cellEditorPopup,
        "cellEditorPopupParent": cellEditorPopupParent,
        "custom_format_string": custom_format_string,
        "editable": editable,
        "cellClassRules": cellClassRules,
        "textWrap": textWrap,
    }
    
    # Remove fields with None values
    column = {key: value for key, value in column.items() if value is not None}

    return column

#
def setup_page(QUEEN_KING, theme_list):
    try:
        cols = st.columns((3,3))
        with cols[0]:
            st.title("Automate Your Portfolio With a AI.BeeBot")
        with cols[1]:
            cust_Button(file_path_url='misc/chess_board_king.gif', height='150px', hoverText='')
            # return_custom_button_nav(file_path_url='misc/chess_board_king.gif', height='150', hoverText='Queens Conscience', key='qc2')

        hive_setup, settings_queen, BrokerAPIKeys, YourPublicCharacter, help_me = st.tabs(["Setup Steps:gear:", "Risk Parameters:comet:", "BrokerAPIKeys:old_key:", "Choose A Queen:crown:", "Help:dizzy:"])

        with hive_setup:
            # st.subheader("Steps to get your QueenTraderBot")
            cols = st.columns((1,1,1))
                            
            # cols = st.columns((5,3,3,2,2,2))
            with cols[0]:
                stoggle("1. Select your Broker",
                "Alpaca is only current supported broker, Create your FREE account at https://app.alpaca.markets/brokerage/new-account"
                )
            with cols[1]:
                stoggle("2. Add your Broker API keys",
                """
                This allows the Queen to place Trades for your portfolio. 
                This will change the way you trade forever...everyone needs an AI
                """
                )
            with cols[2]:
                stoggle("3. Select A Queen",
                """
                Each Queen Offers different trading trading strategies with different levels of customization  
                """
                )
            # with cols[3]:
            #     stoggle("4. Command",
            #     """
            #     Select a Queen.TradingModel 
            #     Trade alongside, make changes, talk with you Queen, Change strategy and Implement! 
            #     Sit Back and watch your Queen Make You Money $$$
            #     """
            #     )

            cols = st.columns((1,1,1))

            with cols[0]:
                page_line_seperator('.5')
                st.image(mainpage_bee_png, width=100)
            with cols[1]:
                page_line_seperator('.5')
                st.image(mainpage_bee_png, width=100)
            with cols[2]:
                page_line_seperator('.5')
                st.image(mainpage_bee_png, width=100)
        
        with BrokerAPIKeys:
            queen__account_keys(PB_App_Pickle=st.session_state['PB_App_Pickle'], QUEEN_KING=QUEEN_KING, authorized_user=st.session_state['authorized_user'], show_form=True)
            pass
        
        with settings_queen:
            st.subheader("QueenTraderBot Settings")
            with st.expander("QueenTraderBot Settings", True):
                mark_down_text(align='left', color=default_text_color, fontsize='23', text='Ensure to Complete Step 1 and an Create Alpaca Account', font=default_font, hyperlink="https://app.alpaca.markets/brokerage/new-account")
                
                # queen_controls__tabs = [""]
                
                cols = st.columns((3,4,1))

                # with st.expander("Risk Levels"):
                with cols[0]:
                    # with st.form("Set How You Wish your Queen to Trade"):
                    st.subheader("Set Your Risk Level")
                    st.text("How Old are you?")
                    if 'QueenTraders_Bithday' in QUEEN_KING.keys():
                        birthday = st.date_input("Enter your birthday: YYYY/MM/DD")
                    else:
                        birthday = st.date_input("Enter your birthday: YYYY/MM/DD", date(year=1989, month=4, day=11))
                    
                    yrs_old = datetime.now().year - birthday.year
                    if QUEEN_KING['age'] == 0:
                        QUEEN_KING['age'] = yrs_old
                    with cols[1]:
                        QUEEN_KING['risk_level'] = st.slider("Risk Level", min_value=1, max_value=10, value=int(QUEEN_KING['risk_level']), help="Shoot for the Moon or Steady as she goes")            
                    with cols[1]:
                        QUEEN_KING['age'] = st.slider("Age..How you Feel to Risk", min_value=1, max_value=100, value=int(QUEEN_KING['age']))     
                    QUEEN_KING['QueenTraders_Bithday'] = birthday
                    
                    
                    # if st.form_submit_button('Save Risk Settings'):
                    if st.button('Save Risk Settings'):
                        PickleData(pickle_file=st.session_state['PB_App_Pickle'], data_to_store=QUEEN_KING)
                        return_runningbee_gif__save(title='Risk Saved')
                            
            # with cols[1]:
            with st.expander("Select a Theme, a Personality"):
                update_queencontrol_theme(QUEEN_KING, theme_list)

        with YourPublicCharacter:      
            cols = st.columns((1,1,1))
            with cols[0]:
                set_button = True if QUEEN_KING['queen_tier'] == 'queen_1' else False
                cBq = cust_Button(file_path_url="misc/pawn.png", height=f'100px', hoverText="Tier1 QUEEN", key="queen_1", default=set_button)
                if cBq:
                    QUEEN_KING['queen_tier'] = 'queen_1'

        with help_me:
            st.write("No Soup for You")
            local_gif(gif_path=flyingbee_grey_gif_path)
    except Exception as e:
        print('setup', e, print_line_of_error())



def cust_graph_trinity(username, api, x_axis, y_axis, theme_options, key="0_graph", refresh_button=False, refresh_sec=8, return_type=None, prod=False, symbols=["SPY"], graph_height=150, trinity_weight='w_15'):
    st_custom_graph(
        api=api,
        x_axis={
            'field': x_axis
        },

        y_axis=y_axis,
        theme_options=theme_options,
        refresh_button=refresh_button,
        
        #kwrags
        username=username,
        prod=prod,
        symbols=symbols,
        refresh_sec=refresh_sec,
        api_key=os.environ.get("fastAPI_key"),
        return_type=return_type,
        graph_height=graph_height,
        trinity_weight=trinity_weight,
        key=key,
        # y_max=420
        )
    return True

def symbols_unique_color(unique_names, characterpool='0123456789ABCDEF'):
    symbol_dicts = []
    # Get unique names from the 'name' column
    # Generate a list of unique colors for each unique name
    unique_colors = ['#' + ''.join([random.choice(characterpool) for j in range(6)]) for _ in range(len(unique_names))]
    
    for i, name in enumerate(unique_names):
        # Customize the 'name' and 'color' values as needed
        if 'vwap' in name and 'QQQ' in name:
            color = "#8BA6F3"
        elif 'vwap' in name and 'SPY' in name:
            color = "#96FEA5"
        elif 'vwap' not in name and 'QQQ' in name:
            color = "#285EF9"
        elif 'vwap' not in name and 'SPY' in name:
            color = "#2DAD40"
        else:
            color = unique_colors[i]
        name = f'{name}'
        symbol_dict = {
            "field": name,
            "name": name,
            "color": color
        }
        symbol_dicts.append(symbol_dict)
    
    return symbol_dicts

def return_user_symbol_colors(QUEEN_KING, symbols=['SPY']):
    # check if symbol is assigned a color and then use that color else use unique
    # qcp_tickers = QUEEN_KING['chess_board'][qcp].get('tickers')

    symbol_dicts = symbols_unique_color(symbols)

    return symbol_dicts


def custom_graph_ttf_qcp(symbols, prod, KING, client_user, QUEEN_KING, refresh_sec, ip_address, graph_height=300, ttf='1Minute_1Day', key='ttf_macd_graph'):
# with cols[1]:
    # refresh_sec = 8 if seconds_to_market_close > 0 and mkhrs == 'open' else None
    k_colors = streamlit_config_colors()
    try:
        # refresh_sec = 8 if seconds_to_market_close > 0 and mkhrs == 'open' else None
        theme_options={
            'backgroundColor': k_colors.get('default_background_color'),
            'main_title': '',   # '' for none
            'x_axis_title': '',
            'grid_color': k_colors.get('default_text_color'),
            "showInLegend": True,
            "showInLegendPerLine": True,
        }
        st_custom_graph(
            api=f'{ip_address}/api/data/ticker_time_frame',
            x_axis={
                'field': 'timestamp_est'
            },

            y_axis=return_user_symbol_colors(QUEEN_KING=QUEEN_KING, symbols=symbols),
            theme_options=theme_options,
            refresh_button=True,
            
            #kwrags
            username=client_user,
            prod=prod,
            symbols=symbols,
            refresh_sec=refresh_sec,
            api_key=os.environ.get("fastAPI_key"),
            graph_height=graph_height,
            key=key,
            ttf=ttf,
            # y_max=420
            )
    except Exception as e:
        print_line_of_error("ERROR cust graph trinity")


def move_columns_to_front(dataframe, column_list, raise_error=False):

    # Ensure that all columns in column_list exist in the DataFrame
    invalid_columns = [col for col in column_list if col not in dataframe.columns]
    if invalid_columns:
        if raise_error:
            raise ValueError(f"Columns not found in DataFrame: {', '.join(invalid_columns)}")
        else:
            st.write(f" cols not found in dataframe {', '.join(invalid_columns)}")

    # Reorder columns
    new_columns_order = column_list + [col for col in dataframe.columns if col not in column_list]
    return dataframe[new_columns_order]



## del me



def menu_bar_selection(prod_name_oppiste, prod_name, prod, menu,hide_streamlit_markers=True):
    k_colors = streamlit_config_colors()
    default_text_color = k_colors['default_text_color'] # = '#59490A'
    default_font = k_colors['default_font'] # = "sans serif"
    default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'
    


    if menu == 'main':
        
        menu_data = [
            {'id':'queen','icon':"fa fa-fire",'label':"Queen"},
            {'id':'TradingModels','icon':"fa fa-fire",'label':"Trading Models"},
            # {'id':'PlayGround', 'icon': "fa fa-bug", 'label':"PlayGround"},
            {'id':'Account', 'icon': "fa fa-bug", 'label':"Account"},
            {'id':'waves', 'icon': "fas fa-chess-board", 'label':"RevRec"},
            {'icon': "fa fa-fighter-jet",'label':"HiveEngine", 
             'submenu':[{'id':'pollen_engine', 'label':"QUEEN", 'icon': "fa fa-heart"},{'label':"KING", 'icon': "fa fa-meh"}]},

        ]
    elif menu == 'unAuth':
        menu_data = [
            {'id':'unauth','icon':"fa fa-fire",'label':"Welcome to pollenq"},

            # {'id':'Copy','icon':"🐙",'label':"Copy"},
            # {'icon': "fa-solid fa-radar",'label':"Dropdown1", 'submenu':[{'id':' subid11','icon': "fa fa-paperclip", 'label':"Sub-item 1"},{'id':'subid12','icon': "💀", 'label':"Sub-item 2"},{'id':'subid13','icon': "fa fa-database", 'label':"Sub-item 3"}]},
            # {'icon': "far fa-chart-bar", 'label':"Chart"},#no tooltip message
            # {'id':' Crazy return value 💀','icon': "💀", 'label':"Calendar"},
            # {'icon': "fas fa-tachometer-alt", 'label':"Dashboard",'ttip':"I'm the Dashboard tooltip!"}, #can add a tooltip message
            # {'icon': "far fa-copy", 'label':"Right End"},
            # {'icon': "fa-solid fa-radar",'label':"Dropdown2", 'submenu':[{'label':"Sub-item 1", 'icon': "fa fa-meh"},{'label':"Sub-item 2"},{'icon':'🙉','label':"Sub-item 3",}]},
        ]
        prod_name = ""

    if prod:

        menu_id = hc.nav_bar(
            menu_definition=menu_data,
            home_name=f'pollen {prod_name}',
            login_name='Account',
            hide_streamlit_markers=hide_streamlit_markers, #will show the st hamburger as well as the navbar now!
            sticky_nav=True, #at the top or not
            sticky_mode='pinned', #jumpy or not-jumpy, but sticky or pinned
        )
    else:
        over_theme = {'option_active':'#B7C8D6'} # {'txc_inactive': '#FB070A'} #'txc_active':'#59490A','option_active':'#FB6464'} #'menu_background':'black',
        # over_font = {'font-class':'h2','font-size':'100%'}
        # over_theme = {'txc_inactive': "#0D93FB"}
        menu_id = hc.nav_bar(
            menu_definition=menu_data,
            override_theme=over_theme,
            # font_styling=over_font,
            home_name=f'pollen {prod_name}',
            login_name='Account',
            hide_streamlit_markers=hide_streamlit_markers, #will show the st hamburger as well as the navbar now!
            sticky_nav=True, #at the top or not
            sticky_mode='pinned', #jumpy or not-jumpy, but sticky or pinned
        )

    st.session_state['menu_id']= menu_id

    return menu_id



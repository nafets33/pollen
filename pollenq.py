import pandas as pd
import logging
import os
import pandas as pd
import datetime
import pytz
import ipdb
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from itertools import islice
from PIL import Image
from dotenv import load_dotenv
import os
# from random import randint
import streamlit as st
from polleq_app_auth import signin_main
import time
from streamlit_extras.switch_page_button import switch_page
import argparse
from streamlit_extras.stoggle import stoggle
from app_hive import queen__account_keys, live_sandbox__setup_switch, local_gif, mark_down_text, update_queencontrol_theme, progress_bar, page_line_seperator, return_runningbee_gif__save
from king import hive_master_root, streamlit_config_colors, local__filepaths_misc, ReadPickleData, PickleData, client_dbs_root
from queen_hive import add_key_to_app, init_pollen_dbs,  KINGME, pollen_themes

pd.options.mode.chained_assignment = None
# https://blog.streamlit.io/a-new-streamlit-theme-for-altair-and-plotly/
# https://discuss.streamlit.io/t/how-to-animate-a-line-chart/164/6 ## animiate the Bees Images : )
# https://blog.streamlit.io/introducing-theming/  # change theme colors
# https://extras.streamlit.app
# https://www.freeformatter.com/cron-expression-generator-quartz.html
# http://34.162.236.105:8080/home # dags
# https://docs.google.com/spreadsheets/d/1ddqj-EkO1MluAjDg-U-DyCzJvtFjRN-9SfEYXkB8eNo/edit#gid=0 # track hours
# https://unicode.org/emoji/charts/full-emoji-list.html#1fae0

# scriptname = os.path.basename(__file__)
# queens_chess_piece = os.path.basename(__file__)
def pollenq(admin_pq):


    est = pytz.timezone("US/Eastern")

    main_root = hive_master_root() # os.getcwd()  # hive root

    # images
    MISC = local__filepaths_misc()
    bee_image = MISC['bee_image']
    castle_png = MISC['castle_png']
    bishop_png = MISC['bishop_png']
    queen_png = MISC['queen_png']
    mainpage_bee_png = MISC['mainpage_bee_png']
    floating_queen_gif = MISC['floating_queen_gif']
    chess_board__gif = MISC['chess_board__gif']
    knight_png = MISC['knight_png']
    bishop_unscreen = MISC['bishop_unscreen']
    flyingbee_grey_gif_path = MISC['flyingbee_grey_gif_path']
    alpaca_portfolio_keys_png = MISC['alpaca_portfolio_keys_png']
    
    page_icon = Image.open(bee_image)

    st.set_page_config(
        page_title="pollenq",
        page_icon=page_icon,
        layout="wide",
        initial_sidebar_state='expanded',
        #  menu_items={
        #      'Get Help': 'https://www.extremelycoolapp.com/help',
        #      'Report a bug': "https://www.extremelycoolapp.com/bug",
        #      'About': "# This is a header. This is an *extremely* cool app!"
        #  }
    )

    ##### STREAMLIT ###
    k_colors = streamlit_config_colors()
    default_text_color = k_colors['default_text_color'] # = '#59490A'
    default_font = k_colors['default_font'] # = "sans serif"
    default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'


    with st.spinner("Hello Welcome To pollenq"):
        signin_main()

        
        # st.write(st.session_state['authorized_user'])
        # st.write(st.session_state)
        if st.session_state['authentication_status'] != None:
            if st.session_state['authorized_user'] == False:
                st.info("Your Need to have your account authorized before receiving a QueenTraderBot, Please contact pollenq.queen@gmail.com or click the button below to send a Request")
                client_user_wants_a_queen = st.button("Yes I want a Queen!")
                if client_user_wants_a_queen:
                    st.session_state['init_queen_request'] = True

        if st.session_state['authentication_status']:
            # if 'username' not in st.session_state:
            #     signin_auth = signin_main()
            
            # st.sidebar.write(f'Welcome {st.session_state["name"]}')
            # st.sidebar.write(f'{st.session_state["username"]}')
            # return_to_last_page()

            client_user = st.session_state['username']
            authorized_user = st.session_state['authorized_user']            
            client_user = st.session_state['username'].split("@")[0]

            prod, admin, prod_name = live_sandbox__setup_switch(client_user=client_user)
            
            if admin: ### Need to Store admin password encrypted
                st.write('admin:', admin)
                d = list(os.listdir(client_dbs_root()))
                d = [i.split("db__")[1] for i in d]
                admin_client_user = st.sidebar.selectbox('admin client_users', options=d, index=d.index(client_user))
                if st.sidebar.button('admin change user'):
                    st.session_state['admin__client_user'] = admin_client_user
                    switch_page("pollenq")

            if prod and authorized_user == True:
                st.warning("The Stage is Live And the Queen will begin trading for you....Good Luck...honestly the best Queens i bet will be the storywave_ai")
            else:
                st.info("Welcome to your Sandbox...Play around...create new Queenbots! Learn and Deploy Strategy!")
            
            if admin_pq:
                admin = True
                st.session_state['admin'] = True

            # if db__name exists use db__name else use db
            db_root = st.session_state['db_root']

            init_pollen = init_pollen_dbs(db_root=db_root, prod=st.session_state['production'], queens_chess_piece='queen')
            PB_QUEEN_Pickle = init_pollen['PB_QUEEN_Pickle']
            PB_App_Pickle = init_pollen['PB_App_Pickle']
            PB_Orders_Pickle = init_pollen['PB_Orders_Pickle']

            QUEEN_KING = ReadPickleData(pickle_file=PB_App_Pickle)    
            # def run_main_page():
            KING = KINGME()
            pollen_theme = pollen_themes(KING=KING)
            # QUEEN Databases
            QUEEN_KING = ReadPickleData(pickle_file=PB_App_Pickle)
            QUEEN_KING['source'] = PB_App_Pickle
            QUEEN = ReadPickleData(PB_QUEEN_Pickle)
            ORDERS = ReadPickleData(PB_Orders_Pickle)

            APP_req = add_key_to_app(QUEEN_KING)
            QUEEN_KING = APP_req['QUEEN_KING']
            if APP_req['update']:
                PickleData(PB_App_Pickle, QUEEN_KING)

           
            pollen_theme = pollen_themes(KING=KING)
            theme_list = list(pollen_theme.keys())
            # Return True

            if 'init_queen_request' in st.session_state:
                QUEEN_KING['init_queen_request'] = {'timestamp_est': datetime.datetime.now(est)}
                PickleData(PB_App_Pickle, QUEEN_KING)
                st.success("Hive Master Notified and You should receive contact soon")

            tabs = ["Setup Steps", "Risk Parameters", "To The Hive", "Help"]
            st.session_state['active_tab'] = tabs[0] if 'active_tab' not in st.session_state else st.session_state['active_tab']

            hive_setup, settings_queen, BrokerAPIKeys, YourPublicCharacter, help_me = st.tabs(["Setup Steps:gear:", "Risk Parameters:comet:", "BrokerAPIKeys:old_key:", "YourCharacter:octopus:", "Help:dizzy:"])
            if st.button("QueensConscience:honeybee:"):
                switch_page("QueensConscience")
            with hive_setup:
                st.title("Create Yourself The QueenTrader")
                # st.subheader("Steps to get your QueenTraderBot")
                cols = st.columns((3,3,3,1,1,1,1))
                
                # with cols[0]:
                #     st.text("Customize QueenTraderBot Settings!\nTrade based on how you feel&think" )
                # with cols[1]:
                #     st.image(mainpage_bee_png, width=89)
                # with cols[2]:
                #     st.text("Set an investment theme and watch your QueenTraderBot\nhandle everyone of your trades, trade along side her")


                
                # cols = st.columns((5,3,3,2,2,2))
                with cols[0]:
                    stoggle("1. Select your Broker",
                    "Alpaca is only current supported broker (Alpaca is a free no-fee trading broker, they are FDIC 250k insured) create a FREE account at https://app.alpaca.markets/brokerage/new-account"
                    )
                with cols[1]:
                    stoggle("2. Enter in your API Keys ",
                    """
                    (this allows the QueenTraderBot to place trades) Its going to change the way you trade forever...everyone needs an AI :bot:
                    """
                    )
                with cols[2]:
                    stoggle("3. Set your Risk Parameters",
                    """
                    Go Start Building your QueenTradingBot! There is too much to dicuss now...we'll talk later
                    """
                    )

                cols = st.columns((3,3,3,1,1,1,1))

                with cols[0]:
                    page_line_seperator('.5')
                    st.image(mainpage_bee_png, width=100)
                with cols[1]:
                    page_line_seperator('.5')
                    st.image(mainpage_bee_png, width=100)
                with cols[2]:
                    page_line_seperator('.5')
                    st.image(mainpage_bee_png, width=100)
                # with cols[2]:
                #     st.image(queen_png, width=250)
                    # local_gif(floating_queen_gif, '89', '89')

                # with cols[3]:
                #     # local_gif(gif_path=queen_flair_gif, height=254, width=450)
                #     st.image(bishop_png, width=223)
                    # local_gif(bishop_unscreen, '133', '133')
                with cols[4]:
                    st.image(castle_png, width=133)

                # with cols[5]:
                #     st.image(mainpage_bee_png, width=133)
                #     # page_line_seperator('.5')

                # with cols[1]:
                #     st.image(mainpage_bee_png, width=133)
            
            with BrokerAPIKeys:
                queen__account_keys(PB_App_Pickle=PB_App_Pickle, QUEEN_KING=QUEEN_KING, authorized_user=authorized_user, show_form=True)
                # st.error("Account Needs to be Authoirzed First, Add Keys in QueensConscience")
                pass
            
            page_line_seperator('1')
            
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
                    # st.write(QUEEN_KING.keys())
                        st.text("How Old are you?")
                        if 'QueenTraders_Bithday' in QUEEN_KING.keys():
                            birthday = st.date_input("Enter your birthday: YYYY/MM/DD")
                        else:
                            birthday = st.date_input("Enter your birthday: YYYY/MM/DD", datetime.date(year=1989, month=4, day=11))
                        
                        yrs_old = datetime.datetime.now().year - birthday.year
                        if QUEEN_KING['age'] == 0:
                            QUEEN_KING['age'] = yrs_old
                        with cols[1]:
                            QUEEN_KING['risk_level'] = st.slider("Risk Level", min_value=1, max_value=10, value=int(QUEEN_KING['risk_level']), help="Shoot for the Moon or Steady as she goes")            
                        with cols[1]:
                            QUEEN_KING['age'] = st.slider("Age..How you Feel to Risk", min_value=1, max_value=100, value=int(QUEEN_KING['age']))     
                        QUEEN_KING['QueenTraders_Bithday'] = birthday
                        
                        
                        # if st.form_submit_button('Save Risk Settings'):
                        if st.button('Save Risk Settings'):
                            PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                            return_runningbee_gif__save(title='Risk Saved')
                                
                # with cols[1]:
                with st.expander("Select a Theme, a Personality"):
                    update_queencontrol_theme(QUEEN_KING, theme_list)

            
            


            with help_me:
                st.write("No Soup for You")
                local_gif(gif_path=flyingbee_grey_gif_path)

        
        else:
            st.session_state['authorized_user'] = False
            st.session_state['admin'] = False
            st.session_state['prod'] = False
            pct_queens_taken = 54

            def display_for_unAuth_client_user():
                # newuser = st.button("New User")
                # signin_button = st.button("SignIn")
                
                cols = st.columns((5,2))
                with cols[0]:
                    progress_bar(value=pct_queens_taken, text=f'{100-pct_queens_taken} Queens Remaining')
                with cols[0]:
                    sneak_peak = st.button("Take a sneak peak and watch a Queen Trade in Real Time")
                    if sneak_peak:
                        st.session_state['sneak_peak'] = True
                        switch_page("QueensConscience")
                    else:
                        st.session_state['sneak_peak'] = False
                with cols[1]:
                    st.image(mainpage_bee_png, width=54)
                # with cols[1]:
                #     local_gif(floating_queen_gif, '100', '123')
                page_line_seperator('1')
                
                st.error("ONLY a limited number of Queens Available!! Please contact pollenq.queen@gmail.com for any questions")

                page_line_seperator('1')

                # local_gif(chess_board__gif, 650, 400)
            
            # display_for_unAuth_client_user()
if __name__ == '__main__':
    def createParser():
        parser = argparse.ArgumentParser()
        parser.add_argument ('-admin', default=False)
        return parser
    parser = createParser()
    namespace = parser.parse_args()
    admin_pq = namespace.admin
    pollenq(admin_pq)
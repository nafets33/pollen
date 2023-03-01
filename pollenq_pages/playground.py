import streamlit as st
from streamlit_extras.stoggle import stoggle
from PIL import Image
import subprocess
from polleq_app_auth import signin_main
from chess_piece.queen_hive import print_line_of_error
from chess_piece.app_hive import show_waves, create_AppRequest_package, queens_orders__aggrid_v2, click_button_grid, nested_grid, page_line_seperator, standard_AGgrid, queen_orders_view
from chess_piece.king import master_swarm_KING, PickleData, hive_master_root, local__filepaths_misc, ReadPickleData, return_QUEENs__symbols_data
from custom_button import cust_Button
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta
import hydralit_components as hc
from ozz.ozz_bee import send_ozz_call
import pytz
import ipdb
import pandas as pd
import numpy as np
from chat_bot import ozz_bot
import os



# https://extras.streamlit.app/Annotated%20text

def PlayGround():
    try:
        # images
        MISC = local__filepaths_misc()
        learningwalk_bee = MISC['learningwalk_bee']
        mainpage_bee_png = MISC['mainpage_bee_png']

        est = pytz.timezone("US/Eastern")
        utc = pytz.timezone('UTC')
        st.write(st.color_picker("colors"))
        
        cols = st.columns(3)
        with cols[0]:
            st.write("# Welcome to Playground! 👋")
        with cols[1]:
            st.image(MISC.get('mainpage_bee_png'))
        with cols[2]:
            cB = cust_Button(file_path_url="misc/learningwalks_bee_jq.png", height='50px', key='b1', hoverText="HelloMate")
            if cB:
                st.write("Thank you Akash")
    
        with st.expander("Ozz"):
            cols = st.columns(2)
            with cols[0]:
                query = st.text_input('ozz learning walks call')
                if st.button("ozz"):
                    send_ozz_call(query=query)
            with cols[1]:
                OZZ = ozz_bot(api_key=os.environ.get("ozz_api_key"), username=st.session_state['username'])
                st.write(OZZ)
        
        with st.expander('feedback menu options examples'):
            option_data = [
            {'icon': "bi bi-hand-thumbs-up", 'label':"Agree"},
            {'icon':"fa fa-question-circle",'label':"Unsure"},
            {'icon': "bi bi-hand-thumbs-down", 'label':"Disagree"},
            ]

            # override the theme, else it will use the Streamlit applied theme
            over_theme = {'txc_inactive': 'white','menu_background':'purple','txc_active':'yellow','option_active':'blue'}
            font_fmt = {'font-class':'h2','font-size':'150%'}

            # display a horizontal version of the option bar
            op = hc.option_bar(option_definition=option_data,title='Feedback Response',key='PrimaryOption') #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)
            st.write(op)

            # display a version version of the option bar
            op2 = hc.option_bar(option_definition=option_data,title='Feedback Response',key='PrimaryOption2', horizontal_orientation=False) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=False)
            st.write(op2)


            selected2 = option_menu(None, ["Home", "Upload", "Tasks", 'Settings'], 
                icons=['house', 'cloud-upload', "list-task", 'gear'], 
                menu_icon="cast", default_index=0, orientation="horizontal")
            st.write(selected2)

        view_ss_state = st.sidebar.button("View Session State")
        if view_ss_state:
            st.write(st.session_state)


        def queen_order_flow(QUEEN, active_order_state_list):
            # st.write(QUEEN['source'])
            # if st.session_state['admin'] == False:
            #     return False
            # page_line_seperator()
            # with cols[1]:
            #     orders_table = st.checkbox("show completed orders")
            # import ipdb
            # ipdb.set_trace()
            with st.expander("Portfolio Orders", expanded=True):
                now_time = datetime.now(est)
                cols = st.columns((1,3, 1, 1, 1, 1, 1))
                with cols[0]:
                    refresh_b = st.button("Refresh", key="r1")
                    edit_orders_button = st.checkbox("edit_orders_button", key='edit_orders_button')
                with cols[2]:
                    today_orders = st.checkbox("Today", False)
                    # page_line_seperator(.2)
                    if today_orders:
                        st.image(mainpage_bee_png, width=33)
                with cols[3]:
                    completed_orders = st.checkbox("Completed")
                    # page_line_seperator(.2)
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

                # g_height = grid_height(len_of_rows=len(df))

                if len(df) <= 3:
                    g_height = 250
                else:
                    g_height = 434

                set_grid_height = st.sidebar.number_input(
                    label=f"Set Orders Grid Height", value=g_height
                )
                # with cols[1]:
                # with cols[0]:
                #     mark_down_text(text=f'% {round(sum(df["honey"]) * 100, 2)}', fontsize="18")
                # with cols[1]:
                #     mark_down_text(text=f'$ {round(sum(df["$honey"]), 2)}', fontsize="18")
                # cols = st.columns((1, 1, 10))

                ordertables__agrid = queens_orders__aggrid_v2(
                    data=df.astype(str),
                    active_order_state_list=active_order_state_list,
                    reload_data=False,
                    height=set_grid_height,
                )

                # with cols[0]:
                # download_df_as_CSV(df=ordertables__agrid["data"], file_name="orders.csv")
            
            return ordertables__agrid

        @st.cache(allow_output_mutation=True)
        def return_QUEEN():
            print("test cache")
            return ReadPickleData(st.session_state['PB_QUEEN_Pickle'])


        # QUEEN = ReadPickleData(st.session_state['PB_QUEEN_Pickle'])
        if 'edit_orders_button' in st.session_state and st.session_state['edit_orders_button'] == True:
            QUEEN = return_QUEEN()
        else:
            QUEEN = ReadPickleData(st.session_state['PB_QUEEN_Pickle'])
        
        PB_App_Pickle = st.session_state['PB_App_Pickle']
        QUEEN_KING = ReadPickleData(pickle_file=PB_App_Pickle)
        ticker_db = return_QUEENs__symbols_data(QUEEN=QUEEN)
        POLLENSTORY = ticker_db['pollenstory']
        STORY_bee = ticker_db['STORY_bee']
        tickers_avail = [set(i.split("_")[0] for i in STORY_bee.keys())][0]
        PB_KING_Pickle = master_swarm_KING(prod=st.session_state['production'])
        KING = ReadPickleData(pickle_file=PB_KING_Pickle)

        
        active_order_state_list = ['running', 'running_close', 'submitted', 'error', 'pending', 'completed', 'completed_alpaca', 'running_open', 'archived_bee']
        # queen_order_flow(QUEEN=QUEEN, active_order_state_list=active_order_state_list)
        ordertables__agrid = queen_order_flow(QUEEN=QUEEN, active_order_state_list=active_order_state_list)
        # ipdb.set_trace()
        if st.session_state['authorized_user']:
            if ordertables__agrid.selected_rows:
                # st.write(queen_order[0]['client_order_id'])
                queen_order = ordertables__agrid.selected_rows[0]
                client_order_id = queen_order.get('client_order_id')

                try: # OrderState
                    df = ordertables__agrid["data"][ordertables__agrid["data"].orderstate == "clicked"]
                    if len(df) > 0:
                        current_requests = [i for i in QUEEN_KING['update_queen_order'] if client_order_id in i.keys()]
                        if len(current_requests) > 0:
                            st.write("You Already Requested Queen To Change Order State, Refresh Orders to View latest Status")
                        else:
                            st.write("App Req Created")
                            order_update_package = create_AppRequest_package(request_name='update_queen_order', client_order_id=client_order_id)
                            order_update_package['queen_order_updates'] = {client_order_id: {'queen_order_state': queen_order.get('queen_order_state')}}
                            # QUEEN_KING['update_queen_order'].append(order_update_package)
                            # PickleData(PB_App_Pickle, QUEEN_KING)
                            # st.success("Changing QueenOrderState Please wait for Queen to process, Refresh Table")
                except:
                    st.write("OrderState nothing was clicked")
                
                # validate to continue with selection
                try: ## SELL
                    df = ordertables__agrid["data"][ordertables__agrid["data"].sell == "clicked"]
                    if len(df) > 0:
                        current_requests = [i for i in QUEEN_KING['sell_orders'] if client_order_id in i.keys()]
                        if len(current_requests) > 0:
                            st.write("You Already Requested Queen To Sell order, Refresh Orders to View latest Status")
                        else:
                            st.write("Sell App Req Created")
                            sell_package = create_AppRequest_package(request_name='sell_orders', client_order_id=client_order_id)
                            sell_package['sellable_qty'] = queen_order.get('available_qty')
                            sell_package['side'] = 'sell'
                            sell_package['type'] = 'market'
                            # QUEEN_KING['sell_orders'].append(sell_package)
                            # PickleData(PB_App_Pickle, QUEEN_KING)
                            # st.success("Selling Order Sent to Queen Please wait for Queen to process, Refresh Table")
                    else:
                        st.write("Nothing Sell clicked")

                except:
                    st.write("Nothing was Sold")
                try: ## KOR
                    df = ordertables__agrid["data"][ordertables__agrid["data"].orderrules == "clicked"]
                    if len(df) > 0:
                        st.write("KOR: ", client_order_id)
                        # kings_order_rules__forum(order_rules)
                    else:
                        st.write("Nothing KOR clicked")
                except:
                    st.write("Nothing was KOR")
        # page_tab_permission_denied(st.session_state['admin'])
        with st.expander("button on grid"):
            click_button_grid()

        with st.expander("nested grid"):
            nested_grid()


        with st.expander("pollenstory"):
            ttf = st.selectbox('ttf', list(STORY_bee.keys())) # index=['no'].index('no'))

            grid = standard_AGgrid(data=POLLENSTORY[ttf], configure_side_bar=True)



        with st.expander("wave stories"):
            ticker_option = st.selectbox("ticker", options=tickers_avail)
            frame_option = st.selectbox("frame", options=KING['star_times'])
            show_waves(STORY_bee=STORY_bee, ticker_option=ticker_option, frame_option=frame_option)


        def get_screen_processes():
            # Run the "screen -ls" command to get a list of screen processes
            output = subprocess.run(["screen", "-ls"], stdout=subprocess.PIPE).stdout.decode(
                "utf-8"
            )

            # Split the output into lines
            lines = output.strip().split("\n")

            # The first line is a header, so skip it
            lines = lines[1:]

            # Initialize an empty dictionary
            screen_processes = {}

            # Iterate over the lines and extract the process name and PID
            for line in lines:
                parts = line.split()
                name = parts[0]
                pid = parts[1]
                screen_processes[name] = pid

            return screen_processes
    
    
    except Exception as e:
        print("playground error: ", e,  print_line_of_error())
if __name__ == '__main__':
    PlayGround()
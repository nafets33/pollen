import streamlit as st
from streamlit_extras.stoggle import stoggle
from PIL import Image
import subprocess
from polleq_app_auth import signin_main
from chess_piece.app_hive import local_gif, click_button_grid, nested_grid, page_tab_permission_denied, standard_AGgrid
from chess_piece.king import copy_directory, hive_master_root, local__filepaths_misc, ReadPickleData, return_QUEENs__symbols_data
from custom_button import cust_Button
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta
import hydralit_components as hc

# https://extras.streamlit.app/Annotated%20text


def PlayGround():
    st.set_page_config(
        page_title="PlayGround",
        # page_icon=page_icon,
        layout="wide",
        # initial_sidebar_state=sidebar_hide,
        #  menu_items={
        #      'Get Help': 'https://www.extremelycoolapp.com/help',
        #      'Report a bug': "https://www.extremelycoolapp.com/bug",
        #      'About': "# This is a header. This is an *extremely* cool app!"
        #  }
    )



    # def menu_bar_selection():
    #     menu_data = [
    #         {'icon': "far fa-copy", 'label':"Left End"},
    #         {'id':'Copy','icon':"🐙",'label':"Copy"},
    #         {'icon': "fa-solid fa-radar",'label':"Dropdown1", 'submenu':[{'id':' subid11','icon': "fa fa-paperclip", 'label':"Sub-item 1"},{'id':'subid12','icon': "💀", 'label':"Sub-item 2"},{'id':'subid13','icon': "fa fa-database", 'label':"Sub-item 3"}]},
    #         {'icon': "far fa-chart-bar", 'label':"Chart"},#no tooltip message
    #         {'id':' Crazy return value 💀','icon': "💀", 'label':"Calendar"},
    #         {'icon': "fas fa-tachometer-alt", 'label':"Dashboard",'ttip':"I'm the Dashboard tooltip!"}, #can add a tooltip message
    #         {'icon': "far fa-copy", 'label':"Right End"},
    #         {'icon': "fa-solid fa-radar",'label':"Dropdown2", 'submenu':[{'label':"Sub-item 1", 'icon': "fa fa-meh"},{'label':"Sub-item 2"},{'icon':'🙉','label':"Sub-item 3",}]},
    #     ]

    #     over_theme = {'txc_inactive': '#FFFFFF'}
    #     menu_id = hc.nav_bar(
    #         menu_definition=menu_data,
    #         # override_theme=over_theme,
    #         home_name='pollenq',
    #         login_name='Logout',
    #         hide_streamlit_markers=False, #will show the st hamburger as well as the navbar now!
    #         sticky_nav=True, #at the top or not
    #         sticky_mode='pinned', #jumpy or not-jumpy, but sticky or pinned
    #     )

    #     # if st.button('click me'):
    #     #     st.info('You clicked at: {}'.format(datetime.now()))

    #     return menu_id

    # menu_id = menu_bar_selection()

    # st.write(menu_id)


    # define what option labels and icons to display
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

    # display a version version of the option bar
    op2 = hc.option_bar(option_definition=option_data,title='Feedback Response',key='PrimaryOption2', horizontal_orientation=False) #,override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=False)


    st.write("# Welcome to Playground! 👋")


    selected2 = option_menu(None, ["Home", "Upload", "Tasks", 'Settings'], 
        icons=['house', 'cloud-upload', "list-task", 'gear'], 
        menu_icon="cast", default_index=0, orientation="horizontal")

    st.write(selected2)

    signin_main(page="PlayGround")

    main_root = hive_master_root() # os.getcwd()  # hive root

    # images
    MISC = local__filepaths_misc()
    jpg_root = MISC['jpg_root']
    bee_image = MISC['bee_image']
    castle_png = MISC['castle_png']
    bishop_png = MISC['bishop_png']
    queen_png = MISC['queen_png']
    knight_png = MISC['knight_png']
    mainpage_bee_png = MISC['mainpage_bee_png']
    floating_queen_gif = MISC['floating_queen_gif']
    chess_board__gif = MISC['chess_board__gif']
    bee_power_image = MISC['bee_power_image']
    hex_image = MISC['hex_image']
    hive_image = MISC['hive_image']
    queen_image = MISC['queen_image']
    queen_angel_image = MISC['queen_angel_image']
    flyingbee_gif_path = MISC['flyingbee_gif_path']
    flyingbee_grey_gif_path = MISC['flyingbee_grey_gif_path']
    bitcoin_gif = MISC['bitcoin_gif']
    power_gif = MISC['power_gif']
    uparrow_gif = MISC['uparrow_gif']
    learningwalk_bee = MISC['learningwalk_bee']
    queen_flair_gif = MISC['queen_flair_gif']
    chess_piece_queen = MISC['chess_piece_queen']
    runaway_bee_gif = MISC['runaway_bee_gif']
    # hexagon_loop = MISC['hexagon_loop']
    # purple_heartbeat_gif = MISC['purple_heartbeat_gif'] MISC.get('puprple')

    moving_ticker_gif = MISC['moving_ticker_gif']
    # heart_bee_gif = MISC['heart_bee_gif']


    st.image(mainpage_bee_png)
    # learningwalk_bee = C:\Users\sstapinski\pollen\pollen\custom_button\frontend\build\misc\learningwalks_bee_jq.png
    learningwalk_bee = "misc/learningwalks_bee_jq.png"


    cB = cust_Button(file_path_url="misc/flyingbee_gif_clean.gif", height='50px', hoverText='restart', key=None)
    if cB:
        st.write("Thank you Akash")
        cB = False


    view_ss_state = st.sidebar.button("View Session State")
    if view_ss_state:
        st.write(st.session_state)
        # st.sidebar.collapse()


    # page_tab_permission_denied(st.session_state['admin'])
    with st.expander("button on grid"):
        click_button_grid()

    with st.expander("nested grid"):
        nested_grid()

    QUEEN = ReadPickleData(st.session_state['PB_QUEEN_Pickle'])
    ticker_db = return_QUEENs__symbols_data(QUEEN=QUEEN)
    POLLENSTORY = ticker_db['pollenstory']
    STORY_bee = ticker_db['STORY_bee']

    with st.expander("pollenstory"):
    ttf = st.selectbox('ttf', list(STORY_bee.keys())) # index=['no'].index('no'))

    grid = standard_AGgrid(data=POLLENSTORY[ttf], configure_side_bar=True)


    cB = cust_Button(file_path_url=learningwalk_bee, height='50px', key='b1')
    if cB:
        st.write("Thank you Akash")







    # show trading model

    # admin_user_swap = st.number_input("fast", min_value=1, max_value=10000, value=0)
    # if st.button("swap"): 
    #     if admin_user_swap == 89:
    #         d = list(os.listdir(client_dbs_root()))
    #         d = [i.split("db__")[1] for i in d]
    #         admin_client_user = st.sidebar.selectbox('admin client_users', options=d, index=d.index(db_client_user_name))
    #         if st.sidebar.button('admin change user'):
    #             st.session_state['admin__client_user'] = admin_client_user
    #             switch_page("pollenq")

    # stoggle(
    #     "Click me!",
    #     """🥷 Surprise! Here's some additional content""",
    # )


    # html = """
    #   <style>
    #     /* Disable overlay (fullscreen mode) buttons */
    #     .overlayBtn {
    #       display: none;
    #     }

    #     /* Remove horizontal scroll */
    #     .element-container {
    #       width: auto !important;
    #     }

    #     .fullScreenFrame > div {
    #       width: auto !important;
    #     }

    #     /* 2nd thumbnail */
    #     .element-container:nth-child(4) {
    #       top: -266px;
    #       left: 350px;
    #     }

    #     /* 1st button */
    #     .element-container:nth-child(3) {
    #       left: 10px;
    #       top: -60px;
    #     }

    #     /* 2nd button */
    #     .element-container:nth-child(5) {
    #       left: 360px;
    #       top: -326px;
    #     }
    #   </style>
    # """
    # st.markdown(html, unsafe_allow_html=True)

    # st.image("https://www.w3schools.com/howto/img_forest.jpg", width=300)
    # st.button("Show", key=1)

    # # img=st.image("https://www.w3schools.com/howto/img_forest.jpg", width=300)
    # st.button("Show:key:", key=2)

    # st.button('name', st.image(learningwalk_bee, width=33))


    # st.image("https://cdn.pixabay.com/photo/2012/04/18/00/42/chess-36311_960_720.png", width=33)

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
if __name__ == '__main__':
    PlayGround()
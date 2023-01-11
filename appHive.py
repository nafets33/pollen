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
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import argparse
import datetime
import pandas as pd
import numpy as np
# from QueenHive import PickleData, queen_orders_view
import pickle
from King import hive_master_root, streamlit_config_colors

from dotenv import load_dotenv

est = pytz.timezone("US/Eastern")


main_root = hive_master_root() # os.getcwd()  # hive root

# images
jpg_root = os.path.join(main_root, 'misc')
# chess_pic_1 = os.path.join(jpg_root, 'chess_pic_1.jpg')
bee_image = os.path.join(jpg_root, 'bee.jpg')
bee_power_image = os.path.join(jpg_root, 'power.jpg')
hex_image = os.path.join(jpg_root, 'hex_design.jpg')
hive_image = os.path.join(jpg_root, 'bee_hive.jpg')
queen_image = os.path.join(jpg_root, 'queen.jpg')
queen_angel_image = os.path.join(jpg_root, 'queen_angel.jpg')
flyingbee_gif_path = os.path.join(jpg_root, 'flyingbee_gif_clean.gif')
flyingbee_grey_gif_path = os.path.join(jpg_root, 'flying_bee_clean_grey.gif')
bitcoin_gif = os.path.join(jpg_root, 'bitcoin_spinning.gif')
power_gif = os.path.join(jpg_root, 'power_gif.gif')
uparrow_gif = os.path.join(jpg_root, 'uparrows.gif')
learningwalk_bee = os.path.join(jpg_root, 'learningwalks_bee_jq.png')
learningwalk_bee = Image.open(learningwalk_bee)
queen_flair_gif = os.path.join(jpg_root, 'queen_flair.gif')
# queen_flair_gif_original = os.path.join(jpg_root, 'queen_flair.gif')
chess_piece_queen = "https://cdn.pixabay.com/photo/2012/04/18/00/42/chess-36311_960_720.png"
runaway_bee_gif = os.path.join(jpg_root, 'runaway_bee_gif.gif')

page_icon = Image.open(bee_image)

##### STREAMLIT ###
k_colors = streamlit_config_colors()
default_text_color = k_colors['default_text_color'] # = '#59490A'
default_font = k_colors['default_font'] # = "sans serif"
default_yellow_color = k_colors['default_yellow_color'] # = '#C5B743'

## IMPROVE GLOBAL VARIABLES

def return_runningbee_gif__save(title="Saved", width=33, gif=runaway_bee_gif):
    local_gif(gif_path=gif)
    st.success(title)

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

def queen_orders_view(QUEEN, queen_order_state, cols_to_view=False, return_all_cols=False, return_str=True):
    if cols_to_view:
        col_view = col_view
    else:
        col_view = ['honey', '$honey', 'symbol', 'ticker_time_frame', 'trigname',  'datetime', 'honey_time_in_profit', 'filled_qty', 'qty_available', 'filled_avg_price', 'limit_price', 'cost_basis', 'wave_amo', 'status_q', 'client_order_id', 'origin_wave', 'wave_at_creation', 'power_up', 'sell_reason', 'exit_order_link', 'queen_order_state', 'order_rules', 'order_trig_sell_stop',  'side']
    if len(QUEEN['queen_orders']) > 0:
        df = QUEEN['queen_orders']
        df = df[df['queen_order_state'].isin(queen_order_state)].copy()

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
        
        return {'df': df_return}
    else:
        return {'df': pd.DataFrame()}

def PickleData(pickle_file, data_to_store):

    p_timestamp = {'pq_last_modified': datetime.datetime.now(est)}
    root, name = os.path.split(pickle_file)
    pickle_file_temp = os.path.join(root, ("temp" + name))
    with open(pickle_file_temp, 'wb+') as dbfile:
        db = data_to_store
        db['pq_last_modified'] = p_timestamp
        pickle.dump(db, dbfile)
    
    with open(pickle_file, 'wb+') as dbfile:
        db = data_to_store
        db['pq_last_modified'] = p_timestamp
        pickle.dump(db, dbfile)
     
    return True

def update_queencontrol_theme(QUEEN_KING, theme_list):
    theme_desc = {'nuetral': ' follows basic model wave patterns',
                'strong_risk': ' defaults to high power trades',
                'star__storywave': ' follows symbols each day changes and adjusts order rules based on latest data'}
    with st.form("Update Control"):
        # cols = st.columns((1,3))
        # with cols[0]:
        theme_option = st.selectbox(label='set theme', options=theme_list, index=theme_list.index('nuetral'))
        save_button = st.form_submit_button("Save Theme Setting")
        # with cols[0]:
        # with cols[1]:
        #     st.info("Set your Risk Theme")
        #     # st.warning(f'Theme: {theme_option}')
        #     ep = st.empty()
        # with cols[1]:
        st.info(f'Theme: {theme_option}{theme_desc[theme_option]}')

        if save_button:
            QUEEN_KING['theme'] = theme_option
            QUEEN_KING['last_app_update'] = datetime.datetime.now()
            PickleData(pickle_file=QUEEN_KING['source'], data_to_store=QUEEN_KING)
            st.success("Theme Saved")

def mark_down_text(align='center', color=default_text_color, fontsize='33', text='Hello There', font=default_font, hyperlink=False):
    if hyperlink:
        st.markdown(
            """<a style='display: block; text-align: {};' href="{}">{}</a>
            """.format(align, hyperlink, text),
            unsafe_allow_html=True,
        )    
    else:
        st.markdown('<p style="text-align: {}; font-family:{}; color:{}; font-size: {}px;">{}</p>'.format(align, font, color, fontsize, text), unsafe_allow_html=True)
    return True

def progress_bar(value, sleeptime=.000003, text=False, pct=False):
    
    status_text = st.empty()
    if pct:
        value = int(round((value * 100),0))
    p_bar  = st.progress(value)
    if text:
        status_text.text(text)

    return True

def page_tab_permission_denied(admin, st_stop=True):
    if admin == False:
        st.warning("permission denied you need a Queen to access")
        if st_stop:
            st.info("Page Stopped")
            st.stop()

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


def grid_height(len_of_rows):
    if len_of_rows > 10:
        grid_height = 333
    else:
        grid_height = round(len_of_rows * 33, 0)
    
    return grid_height


def build_AGgrid_df__queenorders(data, active_order_state_list, reload_data=False, fit_columns_on_grid_load=False, height=200, update_mode_value='VALUE_CHANGED', paginationOn=False,  allow_unsafe_jscode=True):
    # Color Code Honey
    data['$honey'] = data['$honey'].apply(lambda x: round(float(x), 2)).fillna(data['honey'])
    data['honey'] = data['honey'].apply(lambda x: round((float(x) * 100), 2)).fillna(data['honey'])
    data['color'] = np.where(data['honey'] > 0, 'green', 'white')
    gb = GridOptionsBuilder.from_dataframe(data, min_column_width=30)
    
    if paginationOn:
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
    
    gb.configure_side_bar() #Add a sidebar

    # gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection

    honey_colors = JsCode("""
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
    """)
                # 'backgroundColor': '#177311'
                # 'backgroundColor': '#F03811',

    honey_colors_dollar = JsCode("""
    function(params) {
        if (params.value > 0) {
            return {
                'color': '#027500',
            }
        }
        else if (params.value < 0) {
            return {
                'color': '#c70c0c',
            }
        }
    };
    """)

    # Config Columns
    gb.configure_column('queen_order_state', header_name='State', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': active_order_state_list })
    gb.configure_column("datetime", header_name='Date', type=["dateColumnFilter","customDateTimeFormat"], custom_format_string='MM/dd/yy', pivot=True, initialWidth=75, maxWidth=110, autoSize=True)
    gb.configure_column("symbol", pinned='left', pivot=True, resizable=True, initialWidth=89, autoSize=True)
    gb.configure_column("trigname", pinned='left', header_name='TrigBee', pivot=True, wrapText=True, resizable=True, initialWidth=100, maxWidth=120, autoSize=True)
    gb.configure_column("ticker_time_frame", pinned='left', header_name='Star', pivot=True, resizable=True, initialWidth=138, autoSize=True)
    gb.configure_column("honey", header_name='Honey%', pinned='left', cellStyle=honey_colors, type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="%", resizable=True, initialWidth=89, maxWidth=100, autoSize=True)
    gb.configure_column("$honey", header_name='Money$', pinned='left', cellStyle=honey_colors, type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="$", resizable=True, initialWidth=89, maxWidth=100, autoSize=True)
    gb.configure_column("honey_time_in_profit", header_name='Time.In.Honey', resizable=True, initialWidth=89, maxWidth=120, autoSize=True)
    gb.configure_column("filled_qty", wrapText=True, resizable=True, initialWidth=95, maxWidth=100, autoSize=True)
    gb.configure_column("qty_available", header_name='available_qty', autoHeight=True, wrapText=True, resizable=True, initialWidth=105, maxWidth=130, autoSize=True)
    gb.configure_column("filled_avg_price", type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="$", header_name='filled_avg_price', autoHeight=True, wrapText=True, resizable=True, initialWidth=120, maxWidth=130, autoSize=True)
    gb.configure_column("limit_price", type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="$", resizable=True, initialWidth=95, maxWidth=100, autoSize=True)
    gb.configure_column("cost_basis",   type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="$", autoHeight=True, wrapText=True, resizable=True, initialWidth=110, maxWidth=120, autoSize=True)
    gb.configure_column("wave_amo",   type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="$", autoHeight=True, wrapText=True, resizable=True, initialWidth=110, maxWidth=120, autoSize=True)
    gb.configure_column("order_rules", header_name='OrderRules', wrapText=True, resizable=True, autoSize=True)

    # ## WHY IS IT NO WORKING??? 
    # k_sep_formatter = JsCode("""
    # function(params) {
    #     return (params.value == null) ? params.value : params.value.toLocaleString('en-US',{style: "currency", currency: "USD"}); 
    # }
    # """)

    # int_cols = ['$honey', 'filled_avg_price', 'cost_basis', 'wave_amo', 'honey']
    # gb.configure_columns(int_cols, valueFormatter=k_sep_formatter)
    # for int_col in int_cols:
    #     gb.configure_column(int_col, type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="$")
# color code columns based on yourValue

    BtnCellRenderer = JsCode('''
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
    ''')



    gridOptions = gb.build()
    
    gridOptions['wrapHeaderText'] = 'true'
    gridOptions['autoHeaderHeight'] = 'true'
    gridOptions['rememberGroupStateWhenNewData'] = 'true'
    gridOptions['enableCellTextSelection'] = 'true'
    gridOptions['resizable'] = 'true'

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

    gridOptions['columnDefs'].append({
        "field": "clicked",
        "header": "Clicked",
        "cellRenderer": BtnCellRenderer,
        "cellRendererParams": {
            "color": "red",
            "background_color": "black",
        },
    })

# columnDefs = [
#     {colId: 'column1', newPosition: 2},
#     {colId: 'column2', newPosition: 0},
#     {colId: 'column3', newPosition: 1},
# ]
# grid_response.setColumnDefs([{'Clicked': 'column1'}, {'Money': 'column2'}])

# # Next, use the setColumnOrder method to rearrange the columns in the grid
# grid.setColumnOrder(columnDefs)
    # gridOptions.moveColumn('Clicked', 5)
    # ipdb.set_trace()
    grid_response = AgGrid(
        data,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT', 
        update_mode=update_mode_value, 
        fit_columns_on_grid_load=fit_columns_on_grid_load,
        # theme="streamlit", #Add theme color to the table
        enable_enterprise_modules=True,
        height=height, 
        reload_data=reload_data,
        allow_unsafe_jscode=allow_unsafe_jscode
    )
    # grid_response = grid_response.set_filter("symbol", "contains", "SPY")
    
    
    return grid_response

def save_the_QUEEN_KING(PB_App_Pickle, QUEEN_KING):
    PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)

def queen_order_flow(ORDERS, active_order_state_list):
    # st.write(QUEEN['source'])
    # if st.session_state['admin'] == False:
    #     return False
    # page_line_seperator()
    # with cols[1]:
    #     orders_table = st.checkbox("show completed orders")
    
    with st.expander('Portfolio Orders', expanded=True):
        now_time = datetime.datetime.now(est)
        cols = st.columns((1,1,1,1,1))
        with cols[0]:
            refresh_b = st.button("Refresh Orders", key='r1')
        with cols[1]:
            today_orders = st.checkbox("Today Orders", False)
        with cols[2]:
            completed_orders = st.checkbox("Completed orders")
        with cols[3]:
            all_orders = st.checkbox("All Orders", False)
        with cols[4]:
            show_errors = st.checkbox("Lost Bees")

        
        order_states = set(ORDERS['queen_orders']['queen_order_state'].tolist())
        
        if all_orders:
            order_states = order_states
        elif completed_orders:
            order_states = ['completed', 'completed_alpaca']
        elif show_errors:
            order_states = ['error']
        else:
            order_states = ['submitted', 'running', 'running_close']
        
        cols = st.columns((3,1))
        with cols[0]:
            queen_order_states = st.multiselect('queen order states', options=list(active_order_state_list), default=order_states)
        
        df = queen_orders_view(QUEEN=ORDERS, queen_order_state=queen_order_states, return_str=False)['df']
        if len(df) == 0:
            st.info("No Orders to View")
            return False

        if today_orders:
            df = df[df['datetime'] > now_time.replace(hour=1, minute=1, second=1)].copy()
        
        with cols[1]:
            g_height = grid_height(len_of_rows=len(df))
            set_grid_height = st.number_input(label=f'Set Orders Grid Height', value=g_height)
                    
        ordertables__agrid = build_AGgrid_df__queenorders(data=df.astype(str), active_order_state_list=active_order_state_list, reload_data=False, height=set_grid_height)
    


            
    return True


def live_sandbox__setup_switch():
    prod = True if 'production' in st.session_state and st.session_state['production'] == True else False
    prod_name = "LIVE" if 'production' in st.session_state and st.session_state['production'] == True else 'Sandbox'
    admin = True if st.session_state['username'] == 'stefanstapinski@gmail.com' else False
    st.session_state['admin'] = True if admin else False
    
    prod_option = st.sidebar.selectbox('LIVE/Sandbox', ['LIVE', 'Sandbox'], index=['LIVE', 'Sandbox'].index(prod_name))#, on_change=save_change())
    st.session_state['production'] = True if prod_option == 'LIVE' else False
    prod = st.session_state['production']

    return prod, admin, prod_name

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
def createParser_App():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-qcp', default="app")
    parser.add_argument ('-admin', default='false')
    # parser.add_argument ('-user', default='pollen')
    return parser

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
        update_mode=GridUpdateMode.SELECTION_CHANGED
    )


def click_button_grid():
    now = int(datetime.datetime.now().timestamp())
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
                "clicked": [""]*20,
            }
        )
        df["cost"] = round(df.amount * df.price, 2)
        df.insert(
            0,
            "datetime",
            df.timestamp.apply(lambda ts: datetime.datetime.fromtimestamp(ts)),
        )

        return df.sort_values("timestamp").drop("timestamp", axis=1)


    # an example based on https://www.ag-grid.com/javascript-data-grid/component-cell-renderer/#simple-cell-renderer-example
    BtnCellRenderer = JsCode('''
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
    ''')

    df = make_data()
    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_default_column(editable=True)
    grid_options = gb.build()

    grid_options['columnDefs'].append({
        "field": "clicked",
        "header": "Clicked",
        "cellRenderer": BtnCellRenderer,
        "cellRendererParams": {
            "color": "red",
            "background_color": "black",
        },
    })

    st.title("cellRenderer Class Example")

    response = AgGrid(df,
                    # theme="streamlit",
                    key='table1',
                    gridOptions=grid_options,
                    allow_unsafe_jscode=True,
                    fit_columns_on_grid_load=True,
                    reload_data=False,
                    try_to_convert_back_to_original_types=False
                    )

    st.write(response['data'])
    try:
        st.write(response['data'][response['data'].clicked == 'clicked'])
    except:
        st.write('Nothing was clicked')

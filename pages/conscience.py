import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from itertools import islice
from PIL import Image
from dotenv import load_dotenv
import streamlit as st
import os

from chess_piece.app_hive import sac_tabs, symbols_unique_color, log_grid, create_ag_grid_column, wave_grid, mark_down_text, mark_down_text, page_line_seperator, local_gif, flying_bee_gif
from chess_piece.king import hive_master_root, streamlit_config_colors, print_line_of_error, return_QUEENs__symbols_data, return_QUEEN_KING_symbols
from chess_piece.queen_hive import fetch_portfolio_history, kingdom__grace_to_find_a_Queen, star_names, return_queenking_board_symbols, sell_button_dict_items, hive_dates, return_market_hours, init_logging, bishop_ticker_info, init_queenbee, star_refresh_star_times
from chess_piece.pollen_db import PollenDatabase
from chess_utils.conscience_utils import buy_button_dict_items, add_symbol_dict_items
from pq_auth import signin_main
from pages.PortfolioManager import ozz
from custom_grid import st_custom_grid, GridOptionsBuilder, JsCode

from custom_graph_v1 import st_custom_graph

import ipdb


pd.options.mode.chained_assignment = None

scriptname = os.path.basename(__file__)
queens_chess_piece = os.path.basename(__file__)

page = 'QueensConscience'


main_root = hive_master_root() # os.getcwd()  # hive root
load_dotenv(os.path.join(main_root, ".env"))
est = pytz.timezone("US/Eastern")
utc = pytz.timezone('UTC')
pg_migration = os.environ.get('pg_migration')


def generate_cell_style(flash_state_variable='Day_state'):
    return JsCode(f"""
        function(p) {{
            // Ensure {flash_state_variable} exists and is a string
            if (p.data.{flash_state_variable} && typeof p.data.{flash_state_variable} === 'string') {{
                // Split {flash_state_variable} by '$'
                var parts = p.data.{flash_state_variable}.split('$');
                
                if (parts.length === 2) {{
                    var action_part = parts[0].toLowerCase(); // Convert to lowercase for consistent matching
                    var value = parseInt(parts[1], 10); // Convert second part to an integer

                    // Further split action by "-"
                    var action_split = action_part.split('-');
                    var action = action_split[0]; // Main action (buy/sell)
                    var length = action_split.length > 1 ? parseInt(action_split[1], 10) : 0; // Extract length as integer
                    
                    // Determine background color based on length and action
                    var color = '';
                    if (!isNaN(length) && length >= 0) {{
                        if (action.includes('buy')) {{
                            if (length <= 2) {{
                                color = '#e0f8e4'; // Light green for > 40
                            }} else if (length <= 8) {{
                                color = '#c8f3d1'; // Light green
                            }} else if (length <= 12) {{
                                color = '#aef0bc'; // Light-medium green
                            }} else if (length <= 16) {{
                                color = '#94ecaa'; // Medium green
                            }} else if (length <= 20) {{
                                color = '#7ae897'; // Medium-dark green
                            }} else if (length <= 24) {{
                                color = '#60e484'; // Dark green
                            }} else if (length <= 28) {{
                                color = '#46e071'; // Darker green
                            }} else if (length <= 32) {{
                                color = '#2cdc5e'; // Darkest green
                            }} else if (length <= 40) {{
                                color = '#12d84b'; // Softer darkest green
                            }} else if (length > 40) {{
                                color = '#00d438'; // Darkest green
                            }}
                        }} else if (action.includes('sell')) {{
                            if (length <= 2) {{
                                color = '#f8e0e0'; // Light red for > 40
                            }} else if (length <= 8) {{
                                color = '#f3c8c8'; // Light red
                            }} else if (length <= 12) {{
                                color = '#f0aeae'; // Light-medium red
                            }} else if (length <= 16) {{
                                color = '#ec9494'; // Medium red
                            }} else if (length <= 20) {{
                                color = '#e87a7a'; // Medium-dark red
                            }} else if (length <= 24) {{
                                color = '#e46060'; // Dark red
                            }} else if (length <= 28) {{
                                color = '#e04646'; // Darker red
                            }} else if (length <= 32) {{
                                color = '#dc2c2c'; // Darkest red
                            }} else if (length <= 40) {{
                                color = '#d81212'; // Softer darkest red
                            }} else if (length > 40) {{
                                color = '#d40000'; // Darkest red
                            }}
                        }}
                    }}

                    // Return style
                    return {{
                        backgroundColor: color,
                        color: value < 0 ? '#f00' : '#000', // Red text if value < 0, otherwise black
                        padding: '2px',
                        boxSizing: 'border-box',
                        border: '8px solid white',
                        fontSize: '16px', 
                        fontWeight: 'bold', 

                    }};
                }}
            }}

            // Default: no style for unhandled cases
            return null;
        }}
    """)

def generate_cell_style_range(max_number=40):
    """
    Generates a JS cell style function that colors the cell based on the 'length' value,
    breaking up the range [0, max_number] equally for color assignment.
    Uses the 'Day_state' field by default.
    """
    # Color codes for buy and sell actions, in order from lowest to highest
    buy_colors = [
        '#e0f8e4',  # Light green
        '#c8f3d1',
        '#aef0bc',
        '#94ecaa',
        '#7ae897',
        '#60e484',
        '#46e071',
        '#2cdc5e',
        '#12d84b',
        '#00d438',  # Darkest green
    ]
    sell_colors = [
        '#f8e0e0',  # Light red
        '#f3c8c8',
        '#f0aeae',
        '#ec9494',
        '#e87a7a',
        '#e46060',
        '#e04646',
        '#dc2c2c',
        '#d81212',
        '#d40000',  # Darkest red
    ]
    # Number of color steps
    n_steps = len(buy_colors)
    # JS arrays for color codes
    buy_colors_js = str(buy_colors).replace("'", '"')
    sell_colors_js = str(sell_colors).replace("'", '"')
    return JsCode(f"""
        function(p) {{
            var max_number = {max_number};
            var n_steps = {n_steps};
            var buy_colors = {buy_colors_js};
            var sell_colors = {sell_colors_js};
            var color = '';
            var value = null;
            var length = 0;
            var is_string = typeof p.value === 'string' && p.value.includes('$');
            var is_number = typeof p.value === 'number' && !isNaN(p.value);

            if (is_string) {{
                var parts = p.value.split('$');
                if (parts.length === 2) {{
                    var action_part = parts[0].toLowerCase();
                    value = parseInt(parts[1], 10);
                    var action_split = action_part.split('-');
                    var action = action_split[0];
                    length = action_split.length > 1 ? parseInt(action_split[1], 10) : 0;
                }}
            }} else if (is_number) {{
                value = p.value;
                length = value;
            }}

            if (value !== null && !isNaN(length)) {{
                var idx;
                if (length >= 0) {{
                    // Positive: green
                    var clamped = Math.min(length, max_number);
                    idx = Math.floor((clamped / max_number) * (n_steps - 1));
                    color = buy_colors[idx];
                }} else {{
                    // Negative: red
                    var clamped = Math.min(Math.abs(length), max_number);
                    idx = Math.floor((clamped / max_number) * (n_steps - 1));
                    color = sell_colors[idx];
                }}

                // If string with action, override color logic
                if (is_string) {{
                    if (action && action.includes('buy')) {{
                        var clamped = Math.min(Math.abs(length), max_number);
                        idx = Math.floor((clamped / max_number) * (n_steps - 1));
                        color = buy_colors[idx];
                    }} else if (action && action.includes('sell')) {{
                        var clamped = Math.min(Math.abs(length), max_number);
                        idx = Math.floor((clamped / max_number) * (n_steps - 1));
                        color = sell_colors[idx];
                    }}
                }}

                return {{
                    backgroundColor: color,
                    color: color, //value < 0 ? '#f00' : '#000',
                    padding: '0px',
                    border: '8px solid white',  // Change thickness here (e.g., '0px' to remove, '1px' for thin)
                    fontSize: '16px',
                    fontWeight: 'bold',
                }};
            }}
            return null;
        }}
    """)

def generate_shaded_cell_style(flash_state_variable='trinity_w_L'):
    return JsCode(f"""
        function(p) {{
            var value = p.data.{flash_state_variable};
            
            // Ensure the value is a number
            if (value !== null && !isNaN(value)) {{
                var color = ''; // Default color
                
                if (value > 0) {{
                    if (value <= 25) {{
                        color = '#e6f9e9'; // Very light green
                    }} else if (value <= 50) {{
                        color = '#bff0c7'; // Light green
                    }} else if (value <= 75) {{
                        color = '#80df97'; // Medium green
                    }} else if (value <= 90) {{
                        color = '#4cb96d'; // Dark green
                    }} else if (value <= 100) {{
                        color = '#2e8948'; // Darker green
                    }}
                }} else if (value < 0) {{
                    if (value >= -25) {{
                        color = '#fdecec'; // Very light red
                    }} else if (value >= -50) {{
                        color = '#f8c6c6'; // Light red
                    }} else if (value >= -75) {{
                        color = '#f09494'; // Medium red
                    }} else if (value >= -90) {{
                        color = '#e06363'; // Dark red
                    }} else if (value >= -100) {{
                        color = '#c23d3d'; // Darker red
                    }}
                }}
                
                // Return the style
                return {{
                    backgroundColor: color,
                    color: '#000', // Black text for better contrast
                    padding: '5px',
                    boxSizing: 'border-box',
                    textAlign: 'center',
                    border: '3px solid white' // White border
                }};
            }}

            // Default: no style for unhandled cases
            return null;
        }}
    """)      


button_suggestedallocation_style = JsCode("""
function(p) {
    if (p.data.allocation_long_deploy > 0) {
        return {
            //backgroundColor: '#bff0c7', // Light green for positive allocation_long_deploy
            padding: '3px',
            boxSizing: 'border-box',
            border: '8px solid' + '#bff0c7', // White border
            color: 'red'
        };
    } else if (p.data.allocation_long_deploy < 0) {
        return {
            //backgroundColor: '#f8c6c6', // Light red for negative allocation_long_deploy
            padding: '3px',
            boxSizing: 'border-box',
            border: '8px solid' + '#f8c6c6', // White border
            color: 'red'
        };
    } else {
        return {
            border: '3px solid white' // Default white border for other cases
        };
    }
}
""")

honey_colors = JsCode("""
function(p) {
    if (p.value > 0) {
        return {
            color: '#0a9d25', // Medium green for positive money
            padding: '0px',
            boxSizing: 'border-box',
            textAlign: 'center',
            fontSize: '16px', 
            //fontWeight: 'bold', 
        };
    } else if (p.value < 0) {
        return {
            color: '#ed370f', // Medium red for negative money
            padding: '0px',
            boxSizing: 'border-box',
            textAlign: 'center',
            fontSize: '16px', 
            //fontWeight: 'bold', 
        };
    } else {
        return {
            textAlign: 'center' // Center the values for zero
        };
    }
}
""")

value_format = JsCode("""function(params) { return params.value ? '$' + Math.round(params.value) : ''; }""")

value_format_number = JsCode("""function(params) { 
    if (params.value === undefined || params.value === null || isNaN(params.value)) return '';
    return params.value.toLocaleString();
}""")

value_format_pct = JsCode("function(params) { return params.value ? params.value.toFixed(2) + '%' : ''; }")

value_format_pct_2 = JsCode("function(params) { return params.value ? (params.value * 100).toFixed(2) + '%' : ''; }")


button_style_sell = JsCode("""
function(p) {
    var value = p.data.money;
    // Try to split by '$' if value is a string
    if (typeof value === 'string' && value.includes('$')) {
        var parts = value.split('$');
        if (parts.length === 2) {
            value = parseFloat(parts[1]);
        }
    }
    if (value > 0) {
        return {
            //backgroundColor: '#bff0c7', // Light green for positive allocation_long_deploy
            padding: '3px',
            boxSizing: 'border-box',
            border: '8px solid #bff0c7' // White border
        };
    } else if (value < 0) {
        return {
            //backgroundColor: '#f8c6c6', // Light red for negative allocation_long_deploy
            padding: '3px',
            boxSizing: 'border-box',
            border: '8px solid #f8c6c6' // White border
        };
    } else {
        return null; // No style for other cases (e.g., money === 0)
    }
}
""")

button_style_symbol = JsCode("""
function(p) {
    return {
        boxSizing: 'border-box',
        padding: '5px',
        border: '10px solid #f2f7ff', // Light grey border
        // backgroundColor: '#f5f5f5'   // Light grey background
    };
}
""")

button_style_BUY_autopilot = JsCode("""
function(color_autobuy) {
    if (color_autobuy.data.buy_autopilot === "ON") {
        //console.log('buy_autopilot value:', color_autobuy.data.buy_autopilot);
        return {
            //backgroundColor: '#bff0c7',
            // color: 'red',
            padding: '3px',
            boxSizing: 'border-box',
            border: '8px solid' + '#bff0c7',
            // width: '100%',
        };
    } else if (color_autobuy.data.buy_autopilot === "OFF") {
        return {
            //backgroundColor: '#f8c6c6', // Light red text
            padding: '3px',
            boxSizing: 'border-box',
            border: '8px solid' + '#f8c6c6',
            // color: 'yellow',
        };
    } else {
        return {};
    }
}
""")

button_style_SELL_autopilot = JsCode("""
function(color_autobuy) {
    if (color_autobuy.data.sell_autopilot === "ON") {
        //console.log('sell_autopilot value:', color_autobuy.data.sell_autopilot);
        return {
            //backgroundColor: '#bff0c7',
            // color: 'red',
            padding: '3px',
            boxSizing: 'border-box',
            border: '8px solid' + '#bff0c7',
            // width: '100%',
        };
    } else if (color_autobuy.data.sell_autopilot === "OFF") {
        return {
            //backgroundColor: '#f8c6c6', // Light red text
            padding: '3px',
            boxSizing: 'border-box',
            border: '8px solid' + '#f8c6c6',
            // color: 'yellow',
        };
    } else {
        return {};
    }
}
""")


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def trigger_queen_vars(dag, client_username, last_trig_date=datetime.now(est)):
    return {'dag': dag, 'last_trig_date': last_trig_date, 'client_user': client_username}

def chunk_write_dictitems_in_row(chunk_list, max_n=10, write_type='checkbox', title="Active Models", groupby_qcp=False, info_type='buy'):

    try:
        # chunk_list = chunk_list
        num_rr = len(chunk_list) + 1 # + 1 is for chunking so slice ends at last 
        chunk_num = max_n if num_rr > max_n else num_rr
        
        # if num_rr > chunk_num:
        chunks = list(chunk(range(num_rr), chunk_num))
        for i in chunks:
            if i[0] == 0:
                slice1 = i[0]
                slice2 = i[-1] # [0 : 49]
            else:
                slice1 = i[0] - 1
                slice2 = i[-1] # [49 : 87]
            chunk_n = chunk_list[slice1:slice2]
            cols = st.columns(len(chunk_n) + 1)
            with cols[0]:
                if write_type == 'info':
                    flying_bee_gif(width='53', height='53')
                else:
                    st.write(title)
                # bees = [write_flying_bee(width='3') for i in chunk_n]
            for idx, package in enumerate(chunk_n):
                for ticker, v in package.items():
                # ticker, value = package.items()
                    with cols[idx + 1]:
                        if write_type == 'checkbox':
                            st.checkbox(ticker, v, key=f'{ticker}')  ## add as quick save to turn off and on Model
                        if write_type == 'info':
                            if info_type == 'buy':
                                st.info(f'{ticker} {v}')
                                # local_gif(gif_path=uparrow_gif, height='23', width='23')
                            else:
                                st.error(f'{ticker} {v}')
                            # flying_bee_gif(width='43', height='40')
                        if write_type == 'pl_profits':
                            st.write(ticker, v)
    except Exception as e:
        print_line_of_error()

    return True 



button_style_broker = JsCode("""
function(ppp) {
    if (ppp.data.Broker === 'Alpaca') {
        return {
            backgroundColor: '#f5f55b', // Yellow background for Alpaca
        };
    } else if (ppp.data.Broker === 'RobinHood') {
        return {
            backgroundColor: '#9fe899', // Green background for Robinhood
        };
    } else {
        return {
            backgroundColor: 'white', // White background for other cases
        };
    }
}
""")

# @st.cache_data
# def portfolio_history():

def account_header_grid(client_user, prod, refresh_sec, ip_address, seconds_to_market_close):
    try:
        k_colors = streamlit_config_colors()
        gb = GridOptionsBuilder.create()
        gb.configure_grid_options(pagination=False, 
                                    enableRangeSelection=True, 
                                    copyHeadersToClipboard=True,
                                    sideBar=False,
                                    sortable=True
                                ) 
        gb.configure_default_column(
            column_width=120,
            resizable=True,
            wrapText=False,
            wrapHeaderText=True,
            autoHeaderHeight=True,
            autoHeight=True,
            suppress_menu=False,
            filterable=False,
            sortable=True
        )
        gb.configure_index('Broker')
        gb.configure_theme('ag-theme-material')

        cols=[
        'Broker',
        'Cash',
        'Long',
        'Short',
        'Crypto',
        'Todays Money',
        'Todays Honey',
        'Portfolio Value',
        'Buying Power',
        'daytrade count'
        'Heart Beat',
        'Avg Beat',
        ]

        animate_numbers = {'cellRenderer': 'agAnimateShowChangeCellRenderer','enableCellChangeFlash': True,}

        def config_cols(cols):
            backgroundColor = k_colors.get('default_background_color')
            default_text_color = k_colors.get('default_text_color')
            return  {
        'Broker': {'width': 130, 'cellStyle': button_style_broker},                  
        'Cash': {**{'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '15px'}}, **animate_numbers},
        'Long': {**{'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '15px'}}, **animate_numbers},                  
        'Short': {'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '15px'}},
        'Crypto': {'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '15px'}},
        'Money': {**{'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '16px'}, "type": ["customNumberFormat", "numericColumn", "customCurrencyFormat"], 'custom_currency_symbol':"$"}, **animate_numbers},
        'Todays Honey': {'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '16px'}},
        'Portfolio Value': {'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '15px'}},
        'Buying Power': {'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '15px'}},
        'daytrade count': {'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '12px'}},
        'Heart Beat': {**{'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '15px'}, 'width': 89}, **animate_numbers},
        'Avg Beat': {'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '16px'}, 'width': 89},
        # 'Broker Delta': {'width': 80,'cellStyle': {'backgroundColor': backgroundColor, 'color': default_text_color, 'fontSize': '12px'}},
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
            prod=prod,
            grid_options=go,
            key=f'{prod}account_header_grid',
            # kwargs from here
            prompt_message = None, #"symbol",
            prompt_field = None, #"symbol", # "current_macd_tier", # for signle value
            api_key=os.environ.get("fastAPI_key"),
            buttons=[],
            grid_height='110px',
            toggle_views=[],
            allow_unsafe_jscode=True,
            grid_type='account_header',
            subtotal_cols=[],
            ) 

    except Exception as e:
        print_line_of_error(e)

# @st.cache_data
def load_storybee(QUEEN_KING, pg_migration, symbols, QUEEN=None):
    if pg_migration:
        symbols = return_QUEEN_KING_symbols(QUEEN_KING)
        STORY_bee = PollenDatabase.retrieve_all_story_bee_data(symbols).get('STORY_bee')
    else:
        STORY_bee = return_QUEENs__symbols_data(QUEEN=QUEEN, QUEEN_KING=QUEEN_KING, read_storybee=True, read_pollenstory=False).get('STORY_bee') ## async'd func
    
    return STORY_bee

def queens_conscience(prod, revrec, KING, QUEEN_KING, api, sneak_peak=False, show_graph_s=True, show_graph_t=True, show_acct=True):
    run_times = {}
    s = datetime.now()
    # with st.sidebar:
    #     edit_grid = st.toggle("Edit Portfolio", True)
    if not sneak_peak:
        with st.sidebar:
            refresh_grids = st.toggle("Refresh Grids", True)
    else:
        refresh_grids = False
    symbols = return_queenking_board_symbols(QUEEN_KING)
    symbols = ['SPY'] if len(symbols) == 0 else symbols



    # STORY_bee = return_QUEENs__symbols_data(symbols=symbols, read_pollenstory=False).get('STORY_bee')

    ip_address = st.session_state['ip_address']
    client_user = st.session_state["username"]
    db_root = st.session_state['db_root']
    prod, admin, prod_name = st.session_state['prod'], st.session_state.get('admin'), st.session_state.get('prod_name')
    # st.write("PRODUCTION", prod)

    # return page last visited
    # revrec = QUEEN.get('revrec')
    # if QUEEN_KING.get('revrec') == 'init' or st.sidebar.button("refresh revrec"):
    #     revrec = refresh_chess_board__revrec(acct_info, QUEEN, QUEEN_KING, STORY_bee, active_queen_order_states) ## Setup Board
    #     QUEEN_KING['revrec'] = revrec

    ##### STREAMLIT ###

  
    def story_grid(prod, client_user, ip_address, revrec, symbols, refresh_sec=8, paginationOn=False, key='default', tab_view=None):

        
        try:
            gb = GridOptionsBuilder.create()
            gb.configure_grid_options(pagination=True, 
                                      paginationPageSize=50, 
                                      suppressPaginationPanel=True, 
                                      enableRangeSelection=True, 
                                      copyHeadersToClipboard=True,
                                      sideBar=True,
                                      sortable=True
                                    ) 
            gb.configure_default_column(column_width=100, 
                                        resizable=True, 
                                        wrapText=False, 
                                        wrapHeaderText=True, 
                                        sortable=True, 
                                        autoHeaderHeight=True, 
                                        autoHeight=True, 
                                        suppress_menu=False, 
                                        filter=True, 
                                        cellStyle={"fontSize": "14px"})            
            gb.configure_index('symbol')
            gb.configure_theme('ag-theme-material')
            if paginationOn:
                gb.configure_pagination(paginationAutoPageSize=True) #Add pagination

            pct_change_columns_config = {
                                'pct_portfolio': {'headerName':"% Portfolio", 'sortable':'true',
                                        "type": ["customNumberFormat", "numericColumn", "numberColumnFilter"],
                                        'valueFormatter': value_format_pct_2
                                        },
                                'current_ask': {'headerName': 'ask', 'sortable':'true',
                                                "type": ["customNumberFormat", "numericColumn", "numberColumnFilter"],
                                                'valueFormatter': value_format_number},
                                '5Minute_5Day_change': {'headerName':"Week Change", 'cellStyle': honey_colors, 'sortable':'true',
                                                    "type": ["customNumberFormat", "numericColumn", "numberColumnFilter"],
                                                    'valueFormatter': value_format_pct_2
                                                    },
                            '30Minute_1Month_change': {'headerName':"Month Change", 'cellStyle': honey_colors, 'sortable':'true',
                                                    "type": ["customNumberFormat", "numericColumn", "numberColumnFilter"],
                                                    'valueFormatter': value_format_pct_2
                                                    },
                            '1Hour_3Month_change': {'headerName':"Quarter Change", 'cellStyle': honey_colors, 'sortable':'true',
                                                    "type": ["customNumberFormat", "numericColumn", "numberColumnFilter"],
                                                    'valueFormatter': value_format_pct_2
                                                    } ,
                            '2Hour_6Month_change': {'headerName':"2 Quarters Change", 'cellStyle': honey_colors, 'sortable':'true',
                                                    "type": ["customNumberFormat", "numericColumn", "numberColumnFilter"],
                                                    'valueFormatter': value_format_pct_2
                                                    },
                            '1Day_1Year_change': {'headerName':"1 Year Change", 'cellStyle': honey_colors, 'sortable':'true',
                                                    "type": ["customNumberFormat", "numericColumn", "numberColumnFilter"],
                                                    'valueFormatter': value_format_pct_2
                                                    } 
            }
            def story_grid_buttons(hf=False):
                # try:
                active_orders_order_book = ['ticker_time_frame', 'side', 'wave_amo', 'filled_qty', 'qty_available', 'qty', 'money', 'honey', 'trigname', 'order_rules']
                # data  ={
                # "filterParams": {
                # "buttons": ['apply', 'reset'], 
                # }}
                buttons = []
                exclude_buy_kors = ['reverse_buy', 'sell_trigbee_trigger_timeduration']
                buttons=[
                            {'button_name': None,
                            'button_api': f'{ip_address}/api/data/update_queenking_symbol',
                            'prompt_message': 'Manage Board',
                            'prompt_field': 'add_symbol_option',
                            'col_headername': 'Symbol',
                            "col_header": "symbol",
                            # "border_color": "green",
                            'col_width':100,
                            'sortable': True,
                            'pinned': 'left',
                            'prompt_order_rules': [i for i in add_symbol_dict_items().keys()],
                            'cellStyle': button_style_symbol,
                            # 'add_symbol_row_info': ['star_buys_at_play', 'allocation_long', 'current_ask', 'ticker_total_budget', 'ticker_remaining_budget', 'ticker_remaining_borrow'],
                            # 'display_grid_column': 'active_orders',
                            # 'editableCols': ['allocation_long'],
                            },

                            {'button_name': None,
                            'button_api': f'{ip_address}/api/data/queen_buy_orders',
                            'prompt_message': 'Edit Buy',
                            'prompt_field': 'kors',
                            'col_headername': 'Advisors Allocation',
                            "col_header": "queens_suggested_buy", # allocation_long_deploy
                            "border_color": "green",
                            'col_width':100,
                            'sortable': True,
                            # 'pinned': 'left',
                            'prompt_order_rules': [i for i in buy_button_dict_items().keys() if i not in exclude_buy_kors],
                            'cellStyle': button_suggestedallocation_style,
                            'add_symbol_row_info': ['ticker_total_budget', 'star_buys_at_play', 'ticker_remaining_budget', 'allocation_long', 'current_ask',
                                                       'ticker_remaining_borrow'],
                            # 'editableCols': ['allocation_long'],
                            },

                            {'button_name': None,
                            'button_api': f'{ip_address}/api/data/queen_sell_orders',
                            'prompt_message': 'Edit Sell',
                            'prompt_field': 'sell_option',
                            'col_headername': 'Sell',
                            "col_header": "queens_suggested_sell",
                            # "border_color": "red",
                            'col_width':100,
                            'sortable': True,
                            # 'pinned': 'left',
                            'border': '2px solid red',
                            'prompt_order_rules': [i for i in sell_button_dict_items().keys()],
                            'cellStyle': button_style_sell, #generate_cell_style_range(100000), #button_style_sell, #JsCode("""function(p) {if (p.data.money > 0) {return {backgroundColor: 'green'}} else {return {}} } """),
                            'cellRendererParams': {
                                'cellStyle': generate_cell_style_range(100000),
                                  'color': 'red',  # or button_style_sell, etc.
                                # ...add any other params you want to pass to the renderer
                            },
                            'add_symbol_row_info': ['qty_available', 'current_ask', 'star_buys_at_play', 'ticker_total_budget', 'ticker_remaining_budget', 'ticker_remaining_borrow']
                            },

                            {'button_name': None,
                            'button_api': f'{ip_address}/api/data/update_buy_autopilot',
                            'prompt_message': 'Edit AutoPilot',
                            'prompt_field': 'edit_buy_autopilot_option',
                            'col_headername': 'Buy Auto Pilot',
                            "col_header": "buy_autopilot",
                            # "border_color": "green",
                            'col_width':75,
                            # 'pinned': 'left',
                            'prompt_order_rules': ['buy_autopilot'],
                            'cellStyle': button_style_BUY_autopilot,
                            },
                            {'button_name': None,
                            'button_api': f'{ip_address}/api/data/update_sell_autopilot',
                            'prompt_message': 'Edit AutoPilot',
                            'prompt_field': 'edit_sell_autopilot_option',
                            'col_headername': 'Sell Auto Pilot',
                            "col_header": "sell_autopilot",
                            # "border_color": "red",
                            'col_width':75,
                            # 'pinned': 'left',
                            'prompt_order_rules': ['sell_autopilot'],
                            'cellStyle': button_style_SELL_autopilot,
                            },
                        ]
                
                exclude_buy_kors = ['star_list', 'reverse_buy', 'sell_trigbee_trigger_timeduration']
                if not hf:
                    for star in star_names().keys():
                        starname = star
                        if star == 'Day':
                            starname = 'Day'
                            cellStyle = generate_cell_style('Day_state')
                        elif star == 'Week':
                            cellStyle = generate_cell_style('Week_state')
                        elif star == 'Month':
                            cellStyle = generate_cell_style('Month_state')
                        elif star == 'Quarter':
                            cellStyle = generate_cell_style('Quarter_state')
                        elif star == 'Quarters':
                            cellStyle = generate_cell_style('Quarters_state')
                        elif star == 'Year':
                            cellStyle = generate_cell_style('Year_state')
                        else:
                            cellStyle = {}
                        temp = {'button_name': None,
                                'button_api': f'{ip_address}/api/data/ttf_buy_orders',
                                'prompt_message': 'Edit Buy',
                                'prompt_field': f'{star}_kors',
                                'col_headername': f'{starname}',
                                "col_header": f"{star}_state",
                                "border_color": "#BEE3FE",
                                'col_width':135,
                                # 'pinned': 'right',
                                'prompt_order_rules': [i for i in buy_button_dict_items().keys() if i not in exclude_buy_kors],
                                'cellStyle': cellStyle,
                                }
                        buttons.append(temp)
                # except Exception as e:
                #     print_line_of_error(f'ERRRROR BUSTSON {e}')
                
                return buttons

            def config_cols(df_qcp):
                df_ticker_qcp_names = df_qcp['piece_name'].tolist()
                configg =  {
                # for col in cols:
                # 'symbol': {'headerName':'Symbol', 'initialWidth':89, 'pinned': 'left', 'sortable':'true',},
                'current_from_yesterday': {'headerName':'% Change', 'sortable':'true',
                                        'cellStyle': honey_colors,
                                        "type": ["customNumberFormat", "numericColumn", "numberColumnFilter"],
                                        'valueFormatter': value_format_pct
                                        }, #  "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ]},                    
                # 'ticker_buying_power': {'headerName':'BuyingPower Allocation', 'editable':True, }, #  'cellEditorPopup': True "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ]},                    
                # 'current_from_open': {'headerName':"% From Open", 'sortable':'true', 
                #                         'cellStyle': honey_colors,
                #                         "type": ["customNumberFormat", "numericColumn", "numberColumnFilter"],
                #                         'valueFormatter': value_format_pct
                #                         },                   

                'unrealized_pl': {'headerName':"Unrealized PL", 'cellStyle': honey_colors, 'sortable':'true',
                                        "type": ["customNumberFormat", "numericColumn", "numberColumnFilter"],
                                        'valueFormatter': value_format
                                        },
                'unrealized_plpc': {'headerName':"Unrealized PL %", 'cellStyle': honey_colors, 'sortable':'true',
                                        "type": ["customNumberFormat", "numericColumn", "numberColumnFilter"],
                                        'valueFormatter': value_format_pct_2
                                        },

                'piece_name': {'headerName': 'Budget Group', 
                               'filter': True,
                                "cellEditorParams": {"values": df_ticker_qcp_names},"editable":True, "cellEditor":"agSelectCellEditor",
                                                                    },
                'queen_wants_to_sell_qty': {'headerName': 'Suggested Sell Qty','sortable': True, 'initialWidth': 89},
                'total_budget': {'headerName':'Total Budget', 'sortable':'true', "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ]},                    
                'star_buys_at_play': { 'headerName': '$Long', 'sortable': True, 'initialWidth': 100, 'enableCellChangeFlash': True, 'cellRenderer': 'agAnimateShowChangeCellRenderer', 'type': ["customNumberFormat", "numericColumn", "numberColumnFilter"], 'autoWidth': True, 'initialWidth': 110} ,
                'star_sells_at_play': { 'headerName': '$Short', 'sortable': True, 'initialWidth': 100, 'enableCellChangeFlash': True, 'cellRenderer': 'agAnimateShowChangeCellRenderer', 'type': ["customNumberFormat", "numericColumn", "numberColumnFilter"], 'autoWidth': True, 'initialWidth': 110},
                'allocation_long' : {'headerName':'Minimum Allocation Long', 'sortable':'true', "type": ["customNumberFormat", "numericColumn", "numberColumnFilter", ], 'autoWidth': True, 'initialWidth': 110},              
                'trinity_w_L': {'headerName': 'Price Position','sortable': True, 'initialWidth': 89, 'enableCellChangeFlash': True, 'cellRenderer': 'agAnimateShowChangeCellRenderer', 
                                'cellStyle': generate_shaded_cell_style('trinity_w_L')},
                'trinity_w_15': {'headerName': 'Day Force','sortable': True, 'initialWidth': 89, 'enableCellChangeFlash': True, 'cellRenderer': 'agAnimateShowChangeCellRenderer',
                                'cellStyle': generate_shaded_cell_style('trinity_w_15')},
                'trinity_w_30': {'headerName': 'Mid Force','sortable': True, 'initialWidth': 89, 'enableCellChangeFlash': True, 'cellRenderer': 'agAnimateShowChangeCellRenderer',
                                'cellStyle': generate_shaded_cell_style('trinity_w_30')},
                'trinity_w_54': {'headerName': 'Future Force','sortable': True, 'initialWidth': 89, 'enableCellChangeFlash': True, 'cellRenderer': 'agAnimateShowChangeCellRenderer',
                                'cellStyle': generate_shaded_cell_style('trinity_w_54')},
                'remaining_budget': create_ag_grid_column(headerName='Remaining Budget', initialWidth=100,  type=["customNumberFormat", "numericColumn", "numberColumnFilter", ]),
                'remaining_budget_borrow': create_ag_grid_column(headerName='Remaining Budget Margin', initialWidth=100, type=["customNumberFormat", "numericColumn", "numberColumnFilter", ]),
                'qty_available': create_ag_grid_column(headerName='Qty Avail', initialWidth=89),
                'broker_qty_delta': create_ag_grid_column(headerName='Broker Qty Delta', initialWidth=89, cellStyle={'backgroundColor': k_colors.get('default_background_color'), 'color': k_colors.get('default_text_color'), 'font': '18px'}),
                'broker_qty_available': {},
                # 'shortName' : {'headerName':'Symbol Name', 'initialWidth':110,},
                # 'sector' : {'headerName':'Sector', 'initialWidth':110,},
                # 'shortRatio' : {'headerName':'Short Ratio', 'initialWidth':89, 'sortable':'true',},
                
                # 'refresh_star': {'headerName': 'ReAllocate Time', 
                #                 "cellEditorParams": {"values": list(star_refresh_star_times().keys())},
                #                                                     "editable":True,
                #                                                     "cellEditor":"agSelectCellEditor",
                #                                                     },       
                }

                return {**configg, **pct_change_columns_config}

            
            story_col_order = [
                               'queens_suggested_buy', 
                               'unrealized_pl', 
                               'unrealized_plpc', 
                               'queens_suggested_sell', 
                               'piece_name',
                               'pct_portfolio', 
                               'buy_autopilot', 
                               'sell_autopilot',
                               'current_ask', 
            ]
            # with st.expander("default build check"):
            #     st.write(go)
            # QUEENsHeart = init_queenbee(client_user=client_user, prod=prod, queen_heart=True, pg_migration=True)
            # df_broker_portfolio=pd.DataFrame(QUEENsHeart['heartbeat'].get('portfolio')).T
            # missing_tickers = [i for i in df_broker_portfolio.index if i not in revrec['df_ticker'].index]
            # if missing_tickers:
            #     print("tickers missing", missing_tickers)
            #     QUEEN_KING[chess_board]['non_active_stories'] = init_qcp_workerbees(piece_name='non_active_stories', ticker_list=missing_tickers, buying_power=0)
            toggle_view = []
            if client_user == 'stefanstapinski@gmail.com':
                main_toggles = ["Portfolio", "King", '2025_Screen']
            else:
                main_toggles = ["Portfolio", "King"]
            hf=False
            if tab_view == 'Hedge Funds':
                hf=True
                refresh_sec = None
                story_col_order = []
                main_toggles = []
                all_avail_hfunds = PollenDatabase.get_all_keys('hedgefund_holdings')
                from pages.hedgefunds import read_filer_names_coverpage
                df = read_filer_names_coverpage()
                filer_names = dict(zip(df['ACCESSION_NUMBER'], df['FILINGMANAGER_NAME']))
                filer_names_ = {v:k for k,v in filer_names.items() if k in all_avail_hfunds}
                
                ACCESSION_NUMBER = all_avail_hfunds[223]
                data = PollenDatabase.retrieve_data('hedgefund_holdings', ACCESSION_NUMBER)
                hedge_fund_names = [i for i in filer_names_.keys()][54:89]
                
                # df = df[df['ACCESSION_NUMBER'].isin(all_avail_hfunds)]
                # print(df.columns)
                # print("LEEEN", len(df))
                # [i for i in all_avail_hfunds if i in df['ACCESSION_NUMBER']]
                # ipdb.set_trace()
                # hedge_fund_names = df['FILINGMANAGER_NAME'].tolist()[:23]

                # ACCESSION_NUMBER = filer_names_[hedge_fund_names[2]]
                # for ACCESSION_NUMBER in hedge_fund_names:
                #     print(ACCESSION_NUMBER)
                #     data = PollenDatabase.retrieve_data('hedgefund_holdings', ACCESSION_NUMBER)
                #     print(data)

                toggle_view = hedge_fund_names
                for col, config in pct_change_columns_config.items():
                    gb.configure_column(col, config)

            elif tab_view == 'Portfolio':
                data  ={
                "filterParams": {
                "buttons": ['apply', 'reset'], 
                }}
                # Build toggle_view as list of "piece_name (XX%)" where XX is total portfolio_pct for that qcp
                toggle_view = []
                # if 'storygauge' in revrec and 'piece_name' in revrec['storygauge'].columns and 'pct_portfolio' in revrec['storygauge'].columns:
                #     qcp_pct = (
                #         revrec['storygauge']
                #         .groupby('piece_name')['pct_portfolio']
                #         .sum()
                #         .sort_values(ascending=False)
                #     )
                #     for qcp, pct in qcp_pct.items():
                #         toggle_view.append(f"{qcp} - {round(pct * 100, 2)}%")
                # else:
                #     toggle_view = [
                #         QUEEN_KING['chess_board'][qcp].get('piece_name')
                #         for qcp in QUEEN_KING['chess_board'].keys()
                #         if len(QUEEN_KING['chess_board'][qcp].get('tickers', [])) > 0
                #     ]
                story_col = revrec.get('storygauge').columns.tolist()
                config_cols_ = config_cols(revrec.get('df_qcp'))
                mmissing = [i for i in story_col if i not in config_cols_.keys()]
                if len(mmissing) > 0:
                    for col in mmissing:
                        col_dtype = revrec.get('storygauge')[col].dtype if col in revrec.get('storygauge').columns else None
                        if col_dtype is not None and pd.api.types.is_string_dtype(col_dtype):
                            extra = {'pivotable': True, 'enableRowGroup': True}
                        elif col_dtype is not None and pd.api.types.is_float_dtype(col_dtype):
                            extra = {'enableValue': True, 'pivotable': True}
                        else:
                            extra ={}
                        # if col == 'symbol':
                        #     extra = {**extra, **{'enablePivot': True, 'rowGroup': True, 'pivotable': True, 'enableRowGroup': True, 'initialWidth': 100,}}
                        # if col == 'ticker_buying_power':
                        #     st.write("ASK COL", col, col_dtype)
                        #     extra = {**extra, **{'aggFunc': 'sum', 'enableValue': True, 'pivotable': True, 'initialWidth': 100,}}
                        gb.configure_column(col, {**data, **{'hide': True}, **extra})
                for col, config_values in config_cols_.items():
                    col_dtype = revrec.get('storygauge')[col].dtype if col in revrec.get('storygauge').columns else None
                    if col_dtype is not None and pd.api.types.is_string_dtype(col_dtype):
                        extra = {'pivotable': True, 'enableRowGroup': True}
                    elif col_dtype is not None and pd.api.types.is_float_dtype(col_dtype):
                        extra = {'enableValue': True, 'pivotable': True}
                    else:
                        extra ={}
                    # if col == 'symbol':
                    #     extra = {**extra, **{'enablePivot': True, 'rowGroup': True, 'pivotable': True, 'enableRowGroup': True, 'initialWidth': 100,}}
                    # if col == 'ticker_buying_power':
                    #     st.write("ASK COL", col, col_dtype)
                    #     extra = {**extra, **{'aggFunc': 'sum', 'enableValue': True, 'pivotable': True, 'initialWidth': 100,}}
                    gb.configure_column(col, {**data, **config_values, **extra})


                # ticker_info_cols = bishop_ticker_info().get('ticker_info_cols')
                # for col in ticker_info_cols:
                #     if col not in story_col + list(config_cols_.keys()):
                #         # config = {"cellEditorParams":{"editable":True,"cellEditor":"agSelectCellEditor",}, 'hide': True, 'sortable': 'true', 'editable': True}
                #         gb.configure_column(col, {'hide': True, 'sortable': 'true', 'cellEditorPopup': True, 'editable': True, 'cellEditorPopupParams': {
                #   'popupWidth': '500',
                #   'popupHeight': '300'}})

            toggle_views = main_toggles + toggle_view
            g_buttons = story_grid_buttons(hf)
            go = gb.build()
            # go['pivotMode'] = True


            st_custom_grid(
                client_user=client_user,
                username=client_user, 
                api=f"{ip_address}/api/data/story",
                api_update=f"{ip_address}/api/data/update_queenking_chessboard",
                refresh_sec=refresh_sec, 
                refresh_cutoff_sec=seconds_to_market_close, 
                prod=st.session_state['prod'],
                grid_options=go,
                key=f'{prod}{tab_view}story_grid',
                return_type='story',
                # kwargs from here
                api_lastmod_key=f"REVREC",
                prompt_message = "symbol",
                prompt_field = "symbol", # "current_macd_tier", # for signle value
                api_key=os.environ.get("fastAPI_key"),
                symbols=symbols,
                buttons=g_buttons,
                grid_height='550px',
                toggle_views = toggle_views,
                allow_unsafe_jscode=True,
                columnOrder=story_col_order,
                refresh_success=True,
                total_col="symbol", # where total is located
                subtotal_cols = ["queens_suggested_buy", #"Advisors Allocation",
                                 "broker_qty_delta",
                                 "allocation_long", #"Minimum Allocation Long", 
                                 "total_budget", 
                                 "qty_available", 
                                 "money", 
                                 "Day_state", 
                                 'star_buys_at_play', 
                                 'remaining_budget', 
                                #  'allocation_long', 
                                'remaining_budget_borrow', 
                                'pct_portfolio', 
                                ],
                filter_apply=True,
                filter_button='piece_name',

            ) 

        except Exception as e:
            print_line_of_error(f"STORYGRID FAILED {e}")



    ########################################################
    ########################################################
    #############The Infinite Loop of Time #################
    ########################################################nnj
    ########################################################jnk
    ########################################################kjm,mmmm

    try:

        # if show_acct:

        #     # Show all portfolio history periods in columns
        #     periods = ['7D', '1M', '3M', '6M', '1A']
        #     perf_cols = st.columns(len(periods))
        #     for i, period in enumerate(periods):
        #         df = fetch_portfolio_history(api, period=period)
        #         if df is not None and not df.empty:
        #             portfolio_perf = round((df.iloc[-1]['equity'] - df.iloc[0]['equity']) / df.iloc[0]['equity'] * 100, 2)
        #             with perf_cols[i]:
        #                 if i != 0:
        #                     mark_down_text(f'{period} %{portfolio_perf}', fontsize='23')
        #                 else:
        #                     mark_down_text(f'Portfolio')

        # Toggle View
        tab_view = sac_tabs(["Portfolio", "AI Portfolio Manager", "Hedge Funds", "Sectors"])
        if tab_view == 'Hedge Funds':
            show_graph_s = False
            show_graph_t = False

        # # if authorized_user: log type auth and none
        log_dir = os.path.join(db_root, 'logs')
        init_logging(queens_chess_piece=queens_chess_piece, db_root=db_root, prod=st.session_state['prod'])
        
        trading_days = hive_dates(api=api)['trading_days']
        mkhrs = return_market_hours(trading_days=trading_days)
        seconds_to_market_close = (datetime.now(est).replace(hour=16, minute=0)- datetime.now(est)).total_seconds() 
        seconds_to_market_close = seconds_to_market_close if seconds_to_market_close > 0 else 0


        # with story_tab:
        refresh_sec = 8 if seconds_to_market_close > 0 and mkhrs == 'open' else 889
        refresh_sec = 365 if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else refresh_sec
        ui_refresh_sec = st.sidebar.number_input('story grid refresh sec', min_value=0)
        if ui_refresh_sec > 0:
            refresh_sec = ui_refresh_sec

        k_colors = streamlit_config_colors()
        default_text_color = k_colors['default_text_color'] # = '#59490A'
        # cols = st.columns((10,1))
        if show_acct and tab_view == 'Portfolio':
            # with cols[0]:
            print("account_header_grid refresh_sec", refresh_sec)
            account_header_grid(client_user, prod, refresh_sec, ip_address, seconds_to_market_close)
        
        if tab_view == 'AI Portfolio Manager':
            # st.switch_page("pages/PortfolioManager.py")
            print("AI Portfolio Manager")
            ozz(st.session_state['authentication_status'])
            st.stop()
            
        # cols = st.columns((8,1,1))
 
                # with st.form("Margin Guage"):
                #     for qcp in revrec['storygauge']:

            # def chunk_list(data, chunk_size=6):
            #     return [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
 
            # if show_margin:
            #     # Streamlit form
            #     with st.form("slider_form"):
            #         st.write("### Set Margin Budget")
            #         # item_list = sorted(set(revrec['storygauge']['piece_name']))
            #         for row in chunk_list(sorted(set(revrec['df_qcp']['piece_name'].tolist())), 3):
            #             cols = st.columns(len(row))
            #             for i, label in enumerate(row):
            #                 token = revrec['df_qcp'].reset_index().set_index('piece_name')
            #                 value = token.loc[label].get('margin_power', 0)
            #                 # Assign slider with unique key
            #                 cols[i].slider(label, min_value=-1.0, max_value=1.0, value=float(value), key=f"slider_{label}_margin")
            #         submitted = st.form_submit_button("Submit")                    
            #         # After form is submitted, collect values using keys
            #         if submitted:
            #             st.write("### Save")
            #             # allocation save fastapi
            # ticker_allowed = KING['alpaca_symbols_df'].index.tolist()
            # crypto_symbols__tickers_avail = ['BTCUSD', 'ETHUSD', 'BTC/USD', 'ETH/USD']
            # ticker_allowed =  ticker_allowed + crypto_symbols__tickers_avail

            # if show_budget:
            #     with st.form("slider_form budget"):
            #         st.write("### Set Budget")
            #         # item_list = sorted(set(revrec['storygauge']['piece_name']))
            #         for row in chunk_list(sorted(set(revrec['df_qcp']['piece_name'].tolist())), 3):
            #             cols = st.columns(len(row))
            #             for i, label in enumerate(row):
            #                 token = revrec['df_qcp'].reset_index().set_index('piece_name')
            #                 value = token.loc[label].get('buying_power', 0)
            #                 t_budget = f'{round(float(token.loc[label].get("total_budget", 0)))}'
            #                 tickers = token.loc[label]['tickers']
            #                 print(tickers)
            #                 cols[i].slider(f'{label}: Budget {t_budget}', min_value=-1.0, max_value=1.0, value=float(value), key=f"slider_{label}_budget")
            #                 cols[i].multiselect(label=f'symbols', options=ticker_allowed, default=tickers, help='Castle Should Hold your Highest Valued Symbols', key=f'{label}tickers', label_visibility='hidden')

            #         submitted = st.form_submit_button("Submit")                    
            #         # After form is submitted, collect values using keys
            #         if submitted:
            #             st.write("### Save")
            #             # allocation save fastapi
        refresh_sec = None if not refresh_grids else refresh_sec
        print("story_grid refresh timer", refresh_sec)
        story_grid(prod, client_user=client_user, ip_address=ip_address, revrec=revrec, symbols=symbols, refresh_sec=refresh_sec, tab_view=tab_view)
          
        if st.sidebar.toggle("Show Wave Grid"):
            if type(revrec.get('waveview')) != pd.core.frame.DataFrame:
                st.error("PENDING QUEEN")
            else:
                with st.expander("Star Grid :sparkles:", True):
                    # refresh_sec = 8 if seconds_to_market_close > 120 and mkhrs == 'open' else 0
                    # refresh_sec = 54 if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else refresh_sec
                    wave_grid(client_user, revrec, symbols, ip_address, 
                              prompt_order_rules=[i for i in buy_button_dict_items().keys()], 
                              toggle_views=[], 
                              refresh_sec=8, 
                              refresh_cutoff_sec=seconds_to_market_close, 
                              paginationOn=True, 
                              key='wave_grid')
                    # wave_grid(revrec=revrec, symbols=symbols, ip_address=ip_address, key=f'{"wb"}{symbols}{"orders"}', refresh_sec=False)

        cols = st.columns(2)
        
        def symbol_graph():
            refresh_sec = 8 if seconds_to_market_close > 120 and mkhrs == 'open' else 0
            refresh_sec = 365 if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else refresh_sec
            refresh_sec = 0 if refresh_grids == False else refresh_sec
            # print("GRAPHS")
            st_custom_graph(
                api=f'{ip_address}/api/data/symbol_graph',
                x_axis={
                    'field': "timestamp_est"
                },

                y_axis=symbols_unique_color(['SPY', 'SPY vwap', 'QQQ', 'QQQ vwap']),
                theme_options={
                            'backgroundColor': k_colors.get('default_background_color'),
                            'main_title': '',   # '' for none
                            'x_axis_title': '',
                            'grid_color': default_text_color,
                            "showInLegend": True,
                            "showInLegendPerLine": True,
                        },
                refresh_button=True,
                
                #kwrags
                username=client_user,
                prod=prod,
                symbols=['SPY', 'QQQ'],
                refresh_sec=refresh_sec,
                api_key=os.environ.get("fastAPI_key"),
                return_type=None,
                graph_height=300,
                key="Index_Graph",
                toggles=list(reversed(list(star_names().keys()))),
                # y_max=420
                )

        if show_graph_s:
            with cols[0]:
                symbol_graph()


        def trinity_graph():
            with st.sidebar:
                graph_qcps = st.multiselect('graph qcps', options=QUEEN_KING.get('chess_board'), default=['bishop', 'castle', 'knight'])
            refresh_sec = 23 if seconds_to_market_close > 0 and mkhrs == 'open' else 0
            refresh_sec = None if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else refresh_sec
            refresh_sec = None if refresh_grids == False else refresh_sec
            symbols = []
            for qcp in graph_qcps:
                symbols+= QUEEN_KING['chess_board'][qcp].get('tickers')
            
            if len(symbols) > 10:
                # print('symbols > 10 lines')
                c=1
                symbols_copy = symbols.copy()
                symbols =  []
                for s in symbols_copy:
                    if c > 9:
                        continue
                    symbols.append(s)
                    c+=1

            refresh_sec = 12 if seconds_to_market_close > 120 and mkhrs == 'open' else 0
            refresh_sec = 60 if 'sneak_peak' in st.session_state and st.session_state['sneak_peak'] else refresh_sec
            refresh_sec = refresh_grids if refresh_grids == False else refresh_sec

            st_custom_graph(
                api=f'{ip_address}/api/data/ticker_time_frame',
                x_axis={
                    'field': 'timestamp_est'
                },

                y_axis=symbols_unique_color(symbols),
                theme_options={
                        'backgroundColor': k_colors.get('default_background_color'),
                        'main_title': '',   # '' for none
                        'x_axis_title': '',
                        'grid_color': default_text_color,
                        "showInLegend": True,
                        "showInLegendPerLine": True,
                    },
                refresh_button=True,
                
                #kwrags
                username=client_user,
                prod=prod,
                symbols=symbols,
                refresh_sec=refresh_sec,
                api_key=os.environ.get("fastAPI_key"),
                return_type=None,
                graph_height=300,
                key='graph2',
                ttf='1Minute_1Day',
                toggles=list(reversed(list(star_names().keys()))),
                # y_max=420
                )

        if show_graph_t:
            with cols[1]:
                trinity_graph()




        if st.sidebar.toggle("Show Logs"):
            log_grid(KING)
        # print("END CONSCIENCE")
        ##### END ####
    except Exception as e:
        print('queensconscience', print_line_of_error(e))

if __name__ == '__main__':


    signin_main(page="pollenq")

    if 'authentication_status' not in st.session_state or st.session_state['authentication_status'] != True:
        print("SWITCHING PAGES")
        # switch_page('pollen')

    client_user = st.session_state.get('client_user') # if st.session_state.get('client_user') else switch_page('pollen')
    prod = st.session_state['prod']
    KING = kingdom__grace_to_find_a_Queen()
    if st.sidebar.toggle("Read Main Server"):
        main_server = True
    else:
        main_server = False
    qb = init_queenbee(client_user=client_user, prod=prod, queen_king=True, api=True, init=True, revrec=True, main_server=main_server)
    QUEEN_KING = qb.get('QUEEN_KING')
    # st.write({data.get('piece_name'): qcp for qcp, data in QUEEN_KING['chess_board'].items() })
    api = qb.get('api')
    revrec = qb.get('revrec') 
    queens_conscience(prod, revrec, KING, QUEEN_KING, api)

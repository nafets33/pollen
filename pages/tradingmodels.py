
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from chess_piece.app_hive import set_streamlit_page_config_once, standard_AGgrid
from dotenv import load_dotenv
import os
from chess_piece.pollen_db import PollenDatabase
import ipdb

set_streamlit_page_config_once()

if 'authentication_status' not in st.session_state or st.session_state['authentication_status'] != True:
    switch_page('pollen')

from chess_piece.king import print_line_of_error, master_swarm_KING
from chess_piece.queen_hive import init_queenbee, read_swarm_db, hive_master_root, pollen_themes, ReadPickleData, PickleData, refresh_tickers_TradingModels
from chess_piece.app_hive import page_line_seperator, create_AppRequest_package, return_image_upon_save


main_root = hive_master_root()
load_dotenv(os.path.join(main_root, ".env"))
pg_migration = os.environ.get('pg_migration')

client_user=st.session_state['client_user']
prod=st.session_state['prod']
st.write(f'Production: {prod}')

if pg_migration:
    KING = read_swarm_db(prod, 'KING')
else:
    KING = ReadPickleData(master_swarm_KING(prod=prod))


PB_App_Pickle = st.session_state.get('PB_App_Pickle') 

def update_trading_models(QUEEN_KING, KING):
    pollen_themes_selections = list(pollen_themes(KING).keys()) 
    try:
        control_option = 'symbols_stars_TradingModel'
        cols = st.columns((1,4))
        with cols[0]:
            saved_avail = list(QUEEN_KING['saved_trading_models'].keys()) + ['select']
            saved_model_ticker = st.selectbox("View Saved Model", options=saved_avail, index=saved_avail.index('select'), help="This will display Saved Model")

        # mark_down_text(color='Black', text='Ticker Model')
        if saved_model_ticker != 'select':
            title = f'{"Viewing a Saved Not active Ticker Model"}'
        else:
            title = "Trading Models"
        
        st.title(title)

        cols = st.columns(4)
        with cols[0]:
            models_avail = list(QUEEN_KING['king_controls_queen'][control_option].keys())
            ticker_option_qc = st.selectbox("Symbol", models_avail, index=models_avail.index(["SPY" if "SPY" in models_avail else models_avail[0]][0]))                
        if st.button(f"{ticker_option_qc} Reset Model"):
            QUEEN_KING = refresh_tickers_TradingModels(QUEEN_KING=QUEEN_KING, ticker=ticker_option_qc)
            if pg_migration:
                table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
                PollenDatabase.upsert_data(table_name, QUEEN_KING.get('key'), QUEEN_KING)
            else:
               PickleData(QUEEN_KING.get('source'), QUEEN_KING)
                
        ## Trading Model
        if saved_model_ticker != 'select':
            st.info("You Are Viewing Saved Model")
            trading_model = QUEEN_KING['saved_trading_models'][saved_model_ticker]
        else:
            trading_model = QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc]

        # Trading Global Model Levels
        star_avail = list(trading_model['stars_kings_order_rules'].keys())
        trigbees_avail = list(trading_model['trigbees'].keys())
        blocktime_avail = list(trading_model['time_blocks'].keys())
        
        ticker_model_level_1 = {
                'portforlio_weight_ask': {'type': 'portforlio_weight_ask'},
                'QueenBeeTrader': {'type': None}, # not allowed to change
                'status': {'type': 'status', 'list': ['active', 'not_active']},
                'buyingpower_allocation_LongTerm': {'type': 'numberslider', 'min': 0, 'max': 1},
                'buyingpower_allocation_ShortTerm': {'type': None}, # returns opposite of LongTerm
                'index_long_X': {'type': 'index_long_X', 'list': ['1X', '2X', '3X']},
                'index_inverse_X': {'type': 'index_inverse_X', 'list': ['1X', '2X', '3X']},
                'total_budget': {'type': 'total_budget'},
                'max_single_trade_amount': {'type': 'number'},
                'allow_for_margin': {'type': 'allow_for_margin'}, 
                'buy_ONLY_by_accept_from_QueenBeeTrader': {'type': 'buy_ONLY_by_accept_from_QueenBeeTrader'},
                'trading_model_name': {'type': None}, # not allowed to change
                'portfolio_name': {'type': None}, # not allowed to change
                'trigbees': {'type': 'trigbees', 'list': ['active', 'not_active']},
                'time_blocks': {'type': 'time_blocks', 'list': ['active', 'not_active']},
                # 'power_rangers': {'type': 'power_rangers', 'list': ['active', 'not_active']},
                # 'power_rangers_power': {'type': 'power_rangers_power'},
                'kings_order_rules': {'type': 'PENDING'},
                'stars_kings_order_rules': {'type': 'stars_kings_order_rules'},
                'short_position': {'type': None},
        }

        star_level_2 = {
            # 'stars': ["1Minute_1Day", "5Minute_5Day", "30Minute_1Month", "1Hour_3Month", "2Hour_6Month", "1Day_1Year"], 
            'trade_using_limits': {'name': 'trade_using_limits', 'type':'bool', 'var': None},
            'stagger_profits': {'name': 'stagger_profits', 'type':'number', 'var': None},
            'total_budget': {'name': 'total_budget', 'type':'number', 'var': None},
            'buyingpower_allocation_LongTerm': {'name': 'buyingpower_allocation_LongTerm', 'type':'number', 'var': None},
            'buyingpower_allocation_ShortTerm': {'name': 'buyingpower_allocation_ShortTerm', 'type':'number', 'var': None},
            'power_rangers': ["1Minute_1Day", "5Minute_5Day", "30Minute_1Month", "1Hour_3Month", "2Hour_6Month", "1Day_1Year"],
            'trigbees': None,
    }

        star_trigbee_mapping = {
            'status': 'checkbox',
        }
            
        kor_option_mapping = {
        'theme': 'theme',
        'take_profit': 'number',
        'sell_out': 'number',
        'status': 'checkbox',
        'trade_using_limits': 'checkbox',
        'doubledown_timeduration': 'number',
        'max_profit_waveDeviation': 'number',
        'max_profit_waveDeviation_timeduration': 'number',
        'timeduration': 'number',
        'sell_trigbee_trigger': 'checkbox',
        'stagger_profits': 'checkbox',
        'scalp_profits': 'checkbox',
        'scalp_profits_timeduration': 'number',
        'stagger_profits_tiers': 'number',
        'limitprice_decay_timeduration': 'number',
        # 'take_profit_in_vwap_deviation_range': 'take_profit_in_vwap_deviation_range',
        'skip_sell_trigbee_distance_frequency': 'skip_sell_trigbee_distance_frequency', # skip sell signal if frequency of last sell signal was X distance >> timeperiod over value, 1m: if sell was 1 story index ago
        'ignore_trigbee_at_power': 'ignore_trigbee_at_power',
        'ignore_trigbee_in_vwap_range': 'ignore_trigbee_in_vwap_range',
        'ignore_trigbee_in_macdstory_tier': 'ignore_trigbee_in_macdstory_tier',
        'ignore_trigbee_in_histstory_tier': 'ignore_trigbee_in_histstory_tier',
        'KOR_version': 'KOR_version',
        }



        cols = st.columns(3)

        with cols[0]:
            star_option_qc = st.selectbox("Star", star_avail, index=star_avail.index(["1Minute_1Day" if "1Minute_1Day" in star_avail else star_avail[0]][0]))
        with cols[1]:
            trigbee_sel = st.selectbox("Trigbee", trigbees_avail, index=trigbees_avail.index(["buy_cross-0" if "buy_cross-0" in trigbees_avail else trigbees_avail[0]][0]))
        with cols[2]:
            # wave_blocks_option = st.selectbox("Block Time", KING['waveBlocktimes'])
            wave_blocks_option = st.selectbox("BlockTime", blocktime_avail, index=blocktime_avail.index(["morning_9-11" if "morning_9-11" in blocktime_avail else blocktime_avail[0]][0]))

        st.write(QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][ticker_option_qc].keys())
        st.write(QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][ticker_option_qc]['stars_kings_order_rules'][star_option_qc].keys())
        st.write(QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][ticker_option_qc]['stars_kings_order_rules'][star_option_qc]['trigbees'][trigbee_sel].keys())
        st.write(QUEEN_KING['king_controls_queen']['symbols_stars_TradingModel'][ticker_option_qc]['stars_kings_order_rules'][star_option_qc]['trigbees'][trigbee_sel][wave_blocks_option].keys())

        with st.form('trading model form'):
            st.subheader("Kings Order Rules Settings")
            #### TRADING MODEL ####
            # Ticker Level 1
            # Star Level 2
            # Trigbees Level 3
            cols = st.columns(3)

            trading_model__star = trading_model['stars_kings_order_rules'][star_option_qc]
            theme = st.selectbox(label=f'Theme', options=pollen_themes_selections, index=pollen_themes_selections.index(trading_model.get('theme')), key=f'theme_reset')
            king_order_rules_update = trading_model__star['trigbees'][trigbee_sel][wave_blocks_option]
            
            # with st.expander(f'{ticker_option_qc} Global Settings'):
            st.subheader(f'{ticker_option_qc} Global Settings')
            cols = st.columns((1,1,1,1,1))
            
            # all ticker settings
            for kor_option, kor_v in trading_model.items():
                # if kor_option in ticker_model_level_1.keys():
                #     item_type = ticker_model_level_1[kor_option]['type']
                #     if kor_option == 'theme':
                #         trading_model[kor_option] = st.selectbox(label=f'{ticker_option_qc}{"_"}{kor_option}', options=item_val, index=item_val.index(kor_v), key=f'{ticker_option_qc}{"_"}{kor_option}')

                #     if item_type == None:
                #         continue # not allowed edit
                if kor_option == 'stars_kings_order_rules':
                    continue

                if kor_option == 'status':
                    with cols[0]:
                        item_val = ticker_model_level_1[kor_option]['list']
                        trading_model[kor_option] = st.selectbox(label=f'{ticker_option_qc}{"_"}{kor_option}', options=item_val, index=item_val.index(kor_v), key=f'{ticker_option_qc}{"_"}{kor_option}')
            
                elif kor_option == 'total_budget':
                    with cols[1]:
                        trading_model[kor_option] = st.number_input(label=f'{ticker_option_qc}{"_"}{kor_option}', value=kor_v, key=f'{ticker_option_qc}{"_"}{kor_option}')

                elif kor_option == 'max_single_trade_amount':
                    with cols[1]:
                        trading_model[kor_option] = st.number_input(label=f'{ticker_option_qc}{"_"}{kor_option}', value=kor_v, key=f'{ticker_option_qc}{"_"}{kor_option}')

                elif kor_option == 'allow_for_margin':
                    with cols[0]:
                        trading_model[kor_option] = st.checkbox(label=f'{ticker_option_qc}{"_"}{kor_option}', value=kor_v, key=f'{ticker_option_qc}{"_"}{kor_option}')

                elif kor_option == 'short_position':
                    with cols[1]:
                        trading_model[kor_option] = st.checkbox(label=f'{ticker_option_qc}{"_"}{kor_option}', value=kor_v, key=f'{ticker_option_qc}{"_"}{kor_option}')
                
                elif kor_option == 'buy_ONLY_by_accept_from_QueenBeeTrader':
                    with cols[1]:
                        trading_model[kor_option] = st.checkbox(label=f'{ticker_option_qc}{"_"}{kor_option}', value=kor_v, key=f'{ticker_option_qc}{"_"}{kor_option}')

                elif kor_option == 'index_long_X':
                    with cols[0]:
                        item_val = ticker_model_level_1[kor_option]['list']
                        trading_model[kor_option] = st.selectbox(label=f'{ticker_option_qc}{"_"}{kor_option}', options=item_val, index=item_val.index(kor_v), key=f'{ticker_option_qc}{"_"}{kor_option}')
                elif kor_option == 'index_inverse_X':
                    with cols[0]:
                        item_val = ticker_model_level_1[kor_option]['list']
                        trading_model[kor_option] = st.selectbox(label=f'{ticker_option_qc}{"_"}{kor_option}', options=item_val, index=item_val.index(kor_v), key=f'{ticker_option_qc}{"_"}{kor_option}')
                
                elif kor_option == 'portforlio_weight_ask':
                    with cols[0]:
                        trading_model[kor_option] = st.slider(label=f'{"portforlio_weight_ask"}', key='portforlio_weight_ask', min_value=float(0.0), max_value=float(1.0), value=float(kor_v), help="Allocation to Strategy by portfolio")

                elif kor_option == 'trigbees':
                    with cols[4]:
                        st.write("Activate Trigbees")
                        item_val = ticker_model_level_1[kor_option]['list']
                        for trigbee, trigactive in trading_model['trigbees'].items():
                            trading_model[kor_option][trigbee] = st.checkbox(label=f'{trigbee}', value=trigactive, key=f'{ticker_option_qc}{"_"}{kor_option}{trigbee}')

                elif kor_option == 'time_blocks':
                    with cols[2]:
                        st.write("Trade Following Time Blocks")
                        for wave_block, waveactive in trading_model['time_blocks'].items():
                            trading_model[kor_option][wave_block] = st.checkbox(label=f'{wave_block}', value=waveactive, key=f'{ticker_option_qc}{"_"}{kor_option}{wave_block}')
                
                elif kor_option == 'power_rangers':
                    with cols[3]:
                        st.write('Trade Following Time Frames')
                        for power_ranger, pr_active in trading_model['power_rangers'].items():
                            trading_model[kor_option][power_ranger] = st.checkbox(label=f'{power_ranger}', value=pr_active, key=f'{ticker_option_qc}{"_"}{kor_option}{power_ranger}')
                
                elif kor_option == 'buyingpower_allocation_LongTerm':
                    with cols[0]:
                        trading_model["buyingpower_allocation_LongTerm"] = st.slider(label=f'{"Long Term Allocation"}', key='tic_long', min_value=float(0.0), max_value=float(1.0), value=float(trading_model['buyingpower_allocation_LongTerm']), help="Set the Length of the trades, lower number means short trade times")

                elif kor_option == 'buyingpower_allocation_ShortTerm':
                    with cols[0]:
                        trading_model['buyingpower_allocation_ShortTerm'] = st.slider(label=f'{"Short Term Allocation"}', key='tic_short', min_value=float(0.0), max_value=float(1.0), value=float(trading_model['buyingpower_allocation_ShortTerm']), help="Set the Length of the trades, lower number means short trade times")

                        # if long > short:
                        #     long = long
                        # else:
                        #     short = 1 - long
                        
                        # trading_model['buyingpower_allocation_ShortTerm'] = short
                        # trading_model["buyingpower_allocation_LongTerm"] = long
                else:
                    st.write("not accounted ", f'{kor_option} {trading_model.get(kor_option)}')

            # with st.expander(f'{star_option_qc} Time Frame'):
            st.subheader(f'Time Frame: {star_option_qc}')
            # st.write([i for i in star_level_2.keys() if i ])
            st.info("Set the Stars Gravity; allocation of power on the set of stars your Symbol's choice")
            cols = st.columns((1,1,1))
            
            for item_control, itc_vars in star_level_2.items():
                if item_control not in QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc]['stars_kings_order_rules'][star_option_qc].keys():
                    st.write(f'{item_control} not in scope')
                    continue
            

            with cols[0]: # total_budget
                trading_model['stars_kings_order_rules'][star_option_qc]['total_budget'] = st.number_input(label='$Budget', value=float(trading_model['stars_kings_order_rules'][star_option_qc]['total_budget']))

                st.write("L power ", trading_model['stars_kings_order_rules'][star_option_qc]['buyingpower_allocation_LongTerm'])
                st.write("S power ", trading_model['stars_kings_order_rules'][star_option_qc]['buyingpower_allocation_ShortTerm'])
            
            with cols[1]: # index_long_X
                trading_model['stars_kings_order_rules'][star_option_qc]['index_long_X'] = st.selectbox("Long X Weight", options=['1X', '2X', '3X'], index=['1X', '2X', '3X'].index(f'{trading_model["stars_kings_order_rules"][star_option_qc]["index_long_X"]}'))

            with cols[1]: # index_inverse_X
                trading_model['stars_kings_order_rules'][star_option_qc]['index_inverse_X'] = st.selectbox("Short X Weight", options=['1X', '2X', '3X'], index=['1X', '2X', '3X'].index(f'{trading_model["stars_kings_order_rules"][star_option_qc]["index_inverse_X"]}'))                    
            
            with cols[2]: # trade_using_limits
                trading_model['stars_kings_order_rules'][star_option_qc]['trade_using_limits'] = st.checkbox("trade_using_limits", value=trading_model['stars_kings_order_rules'][star_option_qc]['trade_using_limits'])
            
            page_line_seperator(height='3')
            
            with cols[1]:
                st.write('Star Allocation Power')
            page_line_seperator(height='1')

            cols = st.columns((1,1,1,1,1,1,6))
            
            c = 0
            for power_ranger, pr_active in trading_model['stars_kings_order_rules'][star_option_qc]['power_rangers'].items():
                # st.write(power_ranger, pr_active)
                c = 0 if c > 5 else c
                with cols[c]:
                    trading_model['stars_kings_order_rules'][star_option_qc]['power_rangers'][power_ranger] = st.slider(label=f'{power_ranger}', min_value=float(0.0), max_value=float(1.0), value=float(pr_active), key=f'{star_option_qc}{power_ranger}')
                c+=1
            
            # with st.expander(f'{wave_blocks_option} Time Block KOR'):
            st.subheader(f' Time Block KOR: {wave_blocks_option}')
            # mark_down_text(text=f'{trigbee_sel}{" >>> "}{wave_blocks_option}')
            # st.write(f'{wave_blocks_option} >>> WaveBlocktime KingOrderRules 4')
            cols = st.columns((1, 1, 2, 3))

            for kor_option, kor_v in king_order_rules_update.items():
                if kor_option in kor_option_mapping.keys():
                    st_func = kor_option_mapping[kor_option]
                    with cols[0]:
                        if kor_option == 'status':
                            st.write(kor_v)
                        if kor_option == 'theme':
                            st.write(kor_v)
                    
                    with cols[1]:
                        if kor_option == 'ignore_trigbee_in_vwap_range':
                            low = st.number_input(label=f'{"ignore_vwap_low"}', value=kor_v['low_range'], key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{"vwap_low_range"}')
                            high = st.number_input(label=f'{"ignore_vwap_high"}', value=kor_v['high_range'], key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{"vwap_high_range"}')
                            king_order_rules_update[kor_option] = {'high_range': high, "low_range": low}
                            # with cols[0]:
                            #     st.write("ignore_trigbee_in_vwap_range")

                    if kor_option == 'skip_sell_trigbee_distance_frequency':
                        with cols[3]:
                            king_order_rules_update[kor_option] = st.slider(label=f'{kor_option}', key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}', min_value=float(0.0), max_value=float(3.0), value=float(kor_v), help="Skip a sellcross trigger frequency")
                    
                    if kor_option == 'ignore_trigbee_at_power':
                        with cols[3]:
                            king_order_rules_update[kor_option] = st.slider(label=f'{kor_option}', key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}', min_value=float(0.0), max_value=float(3.0), value=float(kor_v), help="Trade Needs to be Powerful Enough as defined by the model allocation story")

                    if st_func == 'checckbox':
                        king_order_rules_update[kor_option] = st.checkbox(label=f'{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}')
                    elif st_func == 'number':
                        king_order_rules_update[kor_option] = st.number_input(label=f'{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}')
                    elif st_func == 'text':
                        king_order_rules_update[kor_option] = st.text_input(label=f'{kor_option}', value=kor_v, key=f'{trigbee_sel}{"_"}{wave_blocks_option}{"_"}{kor_option}')
                
                else:
                    # print('missing')
                    st.write("missing ", kor_option)
                    king_order_rules_update[kor_option] = kor_v

            # WaveBlock Time Levle 4 ## using all selections to change KingsOrderRules
            trading_model['stars_kings_order_rules'][star_option_qc]['trigbees'][trigbee_sel][wave_blocks_option] = king_order_rules_update

            cols = st.columns((1,1,1,1,3))
            with cols[0]:
                save_button_addranger = st.form_submit_button("Save Trading Model Settings")
            with cols[1]:
                savecopy_button_addranger = st.form_submit_button("Save Copy of Trading Model Settings")
            with cols[2]:
                replace_model_with_saved_selection = st.form_submit_button("replace model with saved selection")
            with cols[3]:
                refresh_to_theme = st.form_submit_button("Refresh Model To Selected Theme")           

            if save_button_addranger:
                app_req = create_AppRequest_package(request_name='trading_models_requests')
                app_req['trading_model'] = trading_model
                QUEEN_KING['trading_models_requests'].append(app_req)
                QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc] = trading_model
                
                PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
            
            elif savecopy_button_addranger:                        
                QUEEN_KING['saved_trading_models'].update(trading_model)
                PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)

            elif replace_model_with_saved_selection:                        
                app_req = create_AppRequest_package(request_name='trading_models_requests')
                app_req['trading_model'] = trading_model
                QUEEN_KING['trading_models_requests'].append(app_req)
                QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc] = trading_model
                
                PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
            elif refresh_to_theme:
                QUEEN_KING = refresh_tickers_TradingModels(QUEEN_KING=QUEEN_KING, ticker=ticker_option_qc, theme=theme)
                PickleData(pickle_file=PB_App_Pickle, data_to_store=QUEEN_KING)
                return_image_upon_save(title=f'Model Reset to Original Theme Settings')



        if st.button('show queens trading model'):
            st.write(QUEEN_KING['king_controls_queen'][control_option][ticker_option_qc])
    except Exception as e:
        print(e)
        print_line_of_error()

if __name__ == '__main__':

    qb = init_queenbee(client_user, prod, queen=True, queen_king=True, api=True, pg_migration=pg_migration)
    QUEEN = qb.get('QUEEN')
    QUEEN_KING = qb.get('QUEEN_KING')
    api = qb.get('api')

    update_trading_models(QUEEN_KING, KING)                             

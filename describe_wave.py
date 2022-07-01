# describe thee wave

# todays waves
# >split to today only
# 1m 1day: morning, pre-noon, afternoon
# how big are the morning waves? 
# how profitable has the morning waves been?

def return_macd_wave_story(df):
    # timeframes = {'morning': ["9:30", "12:00"],
    #             'afternoon': ["12:01", "16:00"]}
    POLLENSTORY = read_pollenstory()
    df = POLLENSTORY["SPY_1Minute_1Day"]
    t = split_today_vs_prior(df=df)
    dft = t['df_today']

    # morning = slice_by_time(dft, "9:30", "12:00")
    # wave_col_name = "buy_cross-0__wave"
    # sell_wave_col = "sell_cross-0__wave"
    # wave_vol_wavenumber = "buy_cross-0__wave_number"
    # sell_wave_num = "sell_cross-0__wave_number"

    # buy_waves = dft[wave_vol_wavenumber].tolist()
    # num_of_buy_waves = list(set(buy_waves))
    # num_of_buy_waves = [str(i) for i in sorted([int(i) for i in num_of_buy_waves])]

    # sell_waves = dft[sell_wave_num].tolist()
    # num_of_sell_waves = list(set(sell_waves))
    # num_of_sell_waves = [str(i) for i in sorted([int(i) for i in num_of_sell_waves])]


    # length and height of wave
    MACDWAVE_story = {'story': {}, 'buy_cross-0': {}, 'sell_cross-0': {}}

    waves_cols = ["buy_cross-0", "sell_cross-0"]
    waves_cols = [i+"__wave" for i in waves_cols]
    wave_trigger_list = ["buy_cross-0", "sell_cross-0"]
    for trigger in wave_trigger_list:
        wave_col_name = f'{trigger}{"__wave"}'
        wave_col_wavenumber = f'{trigger}{"__wave_number"}'
    
        num_waves = dft[wave_col_wavenumber].tolist()
        num_waves_list = list(set(num_waves))
        num_waves_list = [str(i) for i in sorted([int(i) for i in num_waves_list])]

        for wave_n in num_waves_list:
            MACDWAVE_story[trigger][wave_n] = {}
            if wave_n == '0':
                continue
            t = dft[['timestamp_est', wave_col_wavenumber, 'story_index', wave_col_name]].copy()
            t = dft[dft[wave_col_wavenumber] == wave_n] # slice by trigger event wave start / end 
            
            row_1 = t.iloc[0]['story_index']
            row_2 = t.iloc[-1]['story_index']
            # print(wave_n, row_2 - row_1, t.iloc[0]['timestamp_est'], t.iloc[-1]['timestamp_est'])
            
            MACDWAVE_story[trigger][wave_n].update({'length': row_2 - row_1, 'wave_times': (t.iloc[0]['timestamp_est'], t.iloc[-1]['timestamp_est'])})
            
            wave_height_value = max(t[wave_col_name].values)
            # how long was it profitable?
            profit_df = t[t[wave_col_name] > 0].copy()
            profit_length  = len(profit_df)
            if profit_length > 0:
                max_profit_index = profit_df[profit_df[wave_col_name] == wave_height_value].iloc[0]['story_index']
                time_to_max_profit = max_profit_index - row_1
                MACDWAVE_story[trigger][wave_n].update({'maxprofit': wave_height_value, 'time_to_max_profit': time_to_max_profit})

            else:
                MACDWAVE_story[trigger][wave_n].update({'maxprofit': wave_height_value, 'time_to_max_profit': 0})
        
        
    return MACDWAVE_story

# make conculsions: morning had X# of waves, Y# was profitable, big_waves_occured

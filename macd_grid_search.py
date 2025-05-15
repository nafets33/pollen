import os
import sys
import re
import pickle
import pandas as pd
from datetime import datetime
from tqdm import tqdm
import streamlit as st
from chess_piece.workerbees import queen_workerbees
from chess_piece.queen_hive import analyze_waves, send_email
from chess_piece.king import hive_master_root, workerbee_dbs_backtesting_root__STORY_bee, stars, master_swarm_QUEENBEE, ReadPickleData
from chess_piece.pollen_db import PollenDatabase

send_email(subject=f"Running BackTesting")
fast_vals = range(7,15)
slow_vals = range(15,33)
smooth_vals = range(6,13)

use_blocktime = True

if use_blocktime:
    df = pd.DataFrame(columns = ["ttf", "blocktime", "macd_fast", "macd_slow", "macd_smooth", "winratio", "maxprofit"]) 
else:
    df = pd.DataFrame(columns = ["ttf", "macd_fast", "macd_slow", "macd_smooth", "winratio", "maxprofit"]) 

pg_migration = os.getenv('pg_migration')

backtest_folder = workerbee_dbs_backtesting_root__STORY_bee()

def read_backtest_folder_assert_insight(backtest_folder, return_len=15):
    s = datetime.now()
    # pattern = re.compile(".*__{}-{}-{}_\.pkl".format(macd["fast"], macd["slow"], macd["smooth"]))
    # folder = "symbols_STORY_bee_dbs_backtesting"
    for filepath in os.listdir(backtest_folder):
        if filepath.endswith(".pkl"):
            pass
        else:
            continue
        with open(backtest_folder + "/" + filepath, "rb") as f:
            fast_val, slow_val, smooth_val = filepath.split("__")[1].split(".pkl")[0].split("-")
            ttf = filepath.split("__")[0]
            res = pickle.load(f)
            sb_temp = res["STORY_bee"]
            STORY_bee = {}
            STORY_bee[ttf] = sb_temp
            res = analyze_waves(STORY_bee, ticker_time_frame=False)
            res_data = res["d_agg_view_return"]
            buycross = res_data[ttf]["buy_cross-0"]
            if use_blocktime:
                for i, b in buycross.iterrows():
                    blocktime = b["wave_blocktime"]
                    winners = b["winners_n"]
                    losers = b["losers_n"]
                    if int(winners + losers) == 0:
                        win_ratio = 0
                    else:
                        win_ratio = winners / (winners + losers)
                    maxprofit = b["sum_maxprofit"]
                    df.loc[df.shape[0]] = [ttf, blocktime, fast_val, slow_val, smooth_val, win_ratio, maxprofit]
                    # print("{}, {}, {}, {}, {}, {}, {}".format(ttf, blocktime, fast_val, slow_val, smooth_val, win_ratio, maxprofit))
            else:
                winners = buycross["winners_n"].mean()
                losers = buycross["losers_n"].mean()
                if int(winners + losers) == 0:
                    win_ratio = 0
                else:
                    win_ratio = winners / (winners + losers)
                maxprofit = buycross["sum_maxprofit"].mean()
                df.loc[df.shape[0]] = [ttf, fast_val, slow_val, smooth_val, win_ratio, maxprofit]
                # print("{}, {}, {}, {}, {}, {}".format(ttf, fast_val, slow_val, smooth_val, win_ratio, maxprofit))
    print(df.head(5))
    if use_blocktime:   
        df.to_csv("backtesting/macd_grid_search_blocktime.txt")
    else:
        df.to_csv("backtesting/macd_grid_search.txt")

    ## back test analysis results ##
    back_test_blocktime = os.path.join(hive_master_root(), 'backtesting/macd_grid_search_blocktime.txt')
    df_backtest = pd.read_csv(back_test_blocktime, dtype=str)
    df_backtest['key'] = df_backtest["macd_fast"] + "_" + df_backtest["macd_slow"] + "_" + df_backtest["macd_smooth"]
    for col in ['macd_fast', 'macd_slow', 'macd_smooth', 'winratio', 'maxprofit']:
        df_backtest[col] = pd.to_numeric(df_backtest[col], errors='coerce')
    df_backtest_ttf = df_backtest.groupby(['ttf', 'key', 'macd_fast', 'macd_slow', 'macd_smooth'])[['winratio', 'maxprofit']].sum().reset_index()
    # st.dataframe(df_backtest)
    # standard_AGgrid(df_backtest_ttf)
    # standard_AGgrid(df_backtest)
    stars_times = stars().keys()
    tickers = set([i.split("_")[0] for i in df_backtest_ttf['ttf'].tolist()])
    results = []
    results_top = []
    for ticker in tickers:
        for tframes in stars_times:
            spy = df_backtest_ttf[df_backtest_ttf['ttf'] == f'{ticker}_{tframes}']
            spy_ = spy[spy.index.isin(spy['maxprofit'].nlargest(n=return_len).index.tolist())]
            mf = int(round(sum(spy_['macd_fast']) / return_len,0))
            ms = int(round(sum(spy_['macd_slow']) / return_len,0))
            mss = int(round(sum(spy_['macd_smooth']) / return_len,0))
            spy_['avg_ratio'] = f'{mf}_{ms}_{mss}'
            spy_result = spy_[['ttf', 'avg_ratio']].drop_duplicates()
            results_top.append(spy_result)
            results.append(spy_)

    df_top5 = pd.concat(results)
    df_top5_results = pd.concat(results_top)

    df_top5_results.to_csv(os.path.join(hive_master_root(), 'backtesting') + '/macd_backtest_analysis.txt')

    e = datetime.now()
    run_time = (e-s)
    send_email(subject=f"BackTesting Wave Analysis {run_time}")


def run_backtesting_pollenstory(QUEENBEE=None, run_wave_analysis=True, qcp_s=['castle', 'knight', 'bishop'], skip_patter_if_exists=False):

        # Total number of iterations
    total_iterations = len(fast_vals) * len(slow_vals) * len(smooth_vals)

    # Initialize the progress bar
    ittt = st.empty()
    progress_bar = st.progress(0)
    iteration = 0
    s = datetime.now()
    for fast_val in tqdm(fast_vals):
        for slow_val in slow_vals:
            for smooth_val in smooth_vals:
                if fast_val >= smooth_val or smooth_val >= slow_val:
                    continue
                macd = {
                    "fast": fast_val, 
                    "slow": slow_val, 
                    "smooth": smooth_val
                }
                # print("macd = {}".format(macd))

                if skip_patter_if_exists:
                    # Check that macd was already processed.            
                    pattern = re.compile(".*__{}-{}-{}_\.pkl".format(macd["fast"], macd["slow"], macd["smooth"]))
                    folder = "symbols_STORY_bee_dbs_backtesting"
                    to_continue = False
                    # if not pg_migration:
                    #     key_paths = os.listdir(backtest_folder)
                    # else:
                    #     key_paths = PollenDatabase.get_all_keys('pollen_store_backtesting')
                    for filepath in os.listdir(backtest_folder):
                        if pattern.match(filepath):
                            print("\tcontinued")
                            to_continue = True 
                            break
                    if to_continue:
                        continue
                iteration += 1
                progress_bar.progress(iteration / total_iterations)
                with ittt.container():
                    st.write(f"loop count, {iteration} out of {total_iterations}")

                try:
                    queen_workerbees(
                                    QUEENBEE=QUEENBEE,
                                    qcp_s=qcp_s,
                                     prod = False, 
                                     backtesting = True, 
                                     macd = macd,
                                     reset_only=True)
                except Exception as e:
                    print('heynow', e)
    if run_wave_analysis:
        read_backtest_folder_assert_insight(backtest_folder)


    e = datetime.now()
    run_time = (e-s)
    send_email(subject=f"BackTesting Run {run_time}")

if __name__ == '__main__':
    prod = True
    pg_migration = True
    if pg_migration:
        table_name = 'db' if prod else 'db_sandbox'
        QUEENBEE = PollenDatabase.retrieve_data(table_name, key='QUEEN')
    else:
        QUEENBEE = ReadPickleData(master_swarm_QUEENBEE(prod=prod))

    QUEENBEE = ReadPickleData(master_swarm_QUEENBEE(prod=True))

    run_backtesting_pollenstory(QUEENBEE=QUEENBEE, run_wave_analysis=True, qcp_s=['castle', ]) # 'knight', 'bishop', 'pawn_6', 'Basic Materials', 'Communication Services', 'Technology', 'Consumer Cyclical', 'Financial Services', 'Industrials'
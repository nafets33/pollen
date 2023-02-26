import os
import sys
import re
import pickle
import pandas as pd


sys.path.append("./chess_piece")


from chess_piece.queen_worker_bees import queen_workerbees
from queen_hive import analyze_waves


fast_vals = range(8,15)
slow_vals = range(23,33)
smooth_vals = range(6,13)

use_blocktime = True

if use_blocktime:
    df = pd.DataFrame(columns = ["ttf", "blocktime", "macd_fast", "macd_slow", "macd_smooth", "winratio", "maxprofit"]) 
else:
    df = pd.DataFrame(columns = ["ttf", "macd_fast", "macd_slow", "macd_smooth", "winratio", "maxprofit"]) 


for fast_val in fast_vals:
    for slow_val in slow_vals:
        for smooth_val in smooth_vals:
            if fast_val >= smooth_val or smooth_val >= slow_val:
                continue
            macd = {
                "fast": fast_val, 
                "slow": slow_val, 
                "smooth": smooth_val
            }
            print("macd = {}".format(macd))

            """
            # Check that macd was already processed.            
            pattern = re.compile(".*__{}-{}-{}_\.pkl".format(macd["fast"], macd["slow"], macd["smooth"]))
            folder = "symbols_STORY_bee_dbs_backtesting"
            to_continue = False
            for filepath in os.listdir(folder):
                if pattern.match(filepath):
                    print("\tcontinued")
                    to_continue = True 
                    break
            if to_continue:
                continue

            try:
                queen_workerbees(prod = False, 
                                 backtesting = True, 
                                 macd = macd)
            except Exception as e:
                print(e)
            """
            
            pattern = re.compile(".*__{}-{}-{}_\.pkl".format(macd["fast"], macd["slow"], macd["smooth"]))
            folder = "symbols_STORY_bee_dbs_backtesting"
            for filepath in os.listdir(folder):
                if pattern.match(filepath):
                    with open(folder + "/" + filepath, "rb") as f:
                        ttf = filepath.split("__")[0]
                        res = pickle.load(f)
                        sb_temp = res["STORY_bee"]
                        STORY_bee = {}
                        STORY_bee[ttf] = sb_temp
                        res = analyze_waves(STORY_bee = STORY_bee, ttframe_wave_trigbee = False)
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
                                print("{}, {}, {}, {}, {}, {}, {}".format(ttf, blocktime, fast_val, slow_val, smooth_val, win_ratio, maxprofit))
                        else:
                            winners = buycross["winners_n"].mean()
                            losers = buycross["losers_n"].mean()
                            if int(winners + losers) == 0:
                                win_ratio = 0
                            else:
                                win_ratio = winners / (winners + losers)
                            maxprofit = buycross["sum_maxprofit"].mean()
                            df.loc[df.shape[0]] = [ttf, fast_val, slow_val, smooth_val, win_ratio, maxprofit]
                            print("{}, {}, {}, {}, {}, {}".format(ttf, fast_val, slow_val, smooth_val, win_ratio, maxprofit))
    
print(df.head(5))
if use_blocktime:   
    df.to_csv("macd_grid_search_blocktime.csv")
else:
    df.to_csv("macd_grid_search.csv")



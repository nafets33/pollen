import os
import sys
import re
import pickle


sys.path.append("./chess_piece")


from chess_piece.queen_worker_bees import queen_workerbees
from queen_hive import analyze_waves


fast_vals = range(8,15)
slow_vals = range(23,33)
smooth_vals = range(6,13)


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
            queen_workerbees(prod = False, 
                             backtesting = True, 
                             macd = macd)
            """
            pattern = re.compile(".*__{}-{}-{}_\.pkl".format(macd["fast"], macd["slow"], macd["smooth"]))
            folder = "symbols_STORY_bee_dbs_backtesting"
            for filepath in os.listdir(folder):
                if pattern.match(filepath):
                    print("")
                    print(filepath)
                    with open(folder + "/" + filepath, "rb") as f:
                        res = pickle.load(f)
                        print(res.keys())
                        #dict_list_ttf = analyze_waves(res["STORY_bee"], ttframe_wave_trigbee = False)["d_agg_view_return"]
                        res = analyze_waves(res["STORY_bee"], ttframe_wave_trigbee = False)
                        print(res.keys())
                        print(res["df"])
                        print(res["d_agg_view_return"])
                        print(res["df_agg_view_return"])
                        print(res["df_bestwaves"])
                        #print(res["STORY_bee"])
                        assert False
            assert False



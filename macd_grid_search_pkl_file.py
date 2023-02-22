import sys
import pickle


sys.path.append("./chess_piece")


from queen_hive import analyze_waves


if __name__ == "__main__":
    """
    fname = "symbols_pollenstory_dbs_backtesting/AAPL_1Day_1Year__8-23-9.pkl"
    with open(fname, "rb") as f:
        res = pickle.load(f)
        df = res["pollen_story"]
        dict_list_ttf = analyze_waves(df, ttframe_wave_trigbee = False)["d_agg_view_return"]
        print("pollen")
        print("-----")
        print(dict_list_ttf)
    """
    fname_story = "symbols_STORY_bee_dbs_backtesting/AAPL_1Day_1Year__8-23-9_.pkl"
    with open(fname_story, "rb") as f_story:
        res = pickle.load(f_story)
        print("pollen_story")
        print("------------")
        print(res)
        print("")
        #print(res["STORY_bee"]["waves"])
        #print("")
        #print(res["STORY_bee"]["KNIGHTSWORD"])
        assert False
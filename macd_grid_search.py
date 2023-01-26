from chess_piece.queen_worker_bees import queen_workerbees

fast_vals = range(1,50)
slow_vals = range(1,50)
smooth_vals = range(1,50)

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
            #queen_workerbees(prod = False, 
            #                 backtesting = True, 
            #                 macd = macd)
#queen_workerbees(prod = False, backtesting = False)



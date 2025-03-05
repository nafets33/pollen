

# # WORKERBEE MOVE TO UTILS

# def generate_TradingModel(
#     theme="nuetral", portfolio_name="Jq", ticker="SPY",
#     stars=stars, trigbees=["buy_cross-0", "sell_cross-0"], 
#     trading_model_name="MACD", status="active", portforlio_weight_ask=0.01, init=False,
#     ):
#     # theme level settings
#     themes = [
#         "nuetral", # Custom
#         "custom", # Custom
#         "long_star", # 1yr + 6Mon
#         "short_star", # 1min(safe) + 5Min(safe) + 
#         "day_shark",
#         "safe",
#         "star__storywave_AI", # 
#     ]

#     def theme_king_order_rules(theme, stars=stars):
#         # " time duration in minutes" ### DOUBLE CHECK SOME NOT ALIGNED IN SECONDS ###
#         # Returns Star KOR for all waveblocktimes
        
#         # Default Model Settings return all levels of model
#         symbol_theme_vars = {
#             "power_rangers": {
#                 "1Minute_1Day": True,
#                 "5Minute_5Day" : True,
#                 "30Minute_1Month": True,
#                 "1Hour_3Month": True,
#                 "2Hour_6Month": True,
#                 "1Day_1Year": True,

#             }
#         }        
#         star_theme_vars = {
#                 "1Minute_1Day": {
#                     'stagger_profits':False, 
#                     'buyingpower_allocation_LongTerm': .03,
#                     'buyingpower_allocation_ShortTerm': .03,
#                     'use_margin': False,
#                     },
#                 "5Minute_5Day" : {
#                     'stagger_profits':False, 
#                     'buyingpower_allocation_LongTerm': .5,
#                     'buyingpower_allocation_ShortTerm': .4,
#                     'use_margin': False,
#                     },
#                 "30Minute_1Month": {
#                     'stagger_profits':False, 
#                     'buyingpower_allocation_LongTerm': .6,
#                     'buyingpower_allocation_ShortTerm': .4,
#                     'use_margin': False,
#                     },
#                 "1Hour_3Month": {
#                     'stagger_profits':False, 
#                     'buyingpower_allocation_LongTerm': .8,
#                     'buyingpower_allocation_ShortTerm': .5,
#                     'use_margin': False,
#                     },
#                 "2Hour_6Month": {
#                     'stagger_profits':False, 
#                     'buyingpower_allocation_LongTerm': .8,
#                     'buyingpower_allocation_ShortTerm': .8,
#                     'use_margin': False,
#                     },
#                 "1Day_1Year": {
#                     'stagger_profits':False, 
#                     'buyingpower_allocation_LongTerm': .8,
#                     'buyingpower_allocation_ShortTerm': .8,
#                     'use_margin': False,
#                     },
#         }
#         wave_block_theme__kor = {}

#         if theme.lower() == 'nuetral':
#             symbol_theme_vars = symbol_theme_vars
#             star_theme_vars = star_theme_vars
#             wave_block_theme__kor = {
#                 "1Minute_1Day": kings_order_rules(
#                                     theme=theme,
#                                     status='active',
#                                     doubledown_timeduration=60,
#                                     trade_using_limits=False,
#                                     max_profit_waveDeviation=3,
#                                     max_profit_waveDeviation_timeduration=5,
#                                     timeduration=360,
#                                     take_profit=.01,
#                                     sell_out=0,
#                                     sell_trigbee_trigger=False,
#                                     sell_trigbee_trigger_timeduration=60,#mins
#                                     stagger_profits=False,
#                                     scalp_profits=False,
#                                     scalp_profits_timeduration=30,
#                                     stagger_profits_tiers=1,
#                                     limitprice_decay_timeduration=1,
#                                     skip_sell_trigbee_distance_frequency=1,
#                                     ignore_trigbee_at_power=0.01,
#                                     # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
#                                     take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
#                                     short_position=False,
#                                     use_wave_guage=False,
#                                     close_order_today=False,
#                                     revisit_trade_frequency=60,
#                 ),
#                 "5Minute_5Day": kings_order_rules(
#                                     theme=theme,
#                                     status='active',
#                                     doubledown_timeduration=60,
#                                     trade_using_limits=False,
#                                     max_profit_waveDeviation=3,
#                                     max_profit_waveDeviation_timeduration=10,
#                                     timeduration=320,
#                                     take_profit=.05,
#                                     sell_out=0,
#                                     sell_trigbee_trigger=True,
#                                     sell_trigbee_trigger_timeduration=60*5,#mins
#                                     stagger_profits=False,
#                                     scalp_profits=False,
#                                     scalp_profits_timeduration=30,
#                                     stagger_profits_tiers=3,
#                                     limitprice_decay_timeduration=1,
#                                     skip_sell_trigbee_distance_frequency=0,
#                                     ignore_trigbee_at_power=0.01,
#                                     # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
#                                     take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
#                                     short_position=False,
#                                     use_wave_guage=False,
#                                     close_order_today=False,
#                                     revisit_trade_frequency=5 * 3600,
#                 ),
#                 "30Minute_1Month": kings_order_rules(
#                                     theme=theme,
#                                     status='active',
#                                     doubledown_timeduration=60,
#                                     trade_using_limits=False,
#                                     max_profit_waveDeviation=2,
#                                     max_profit_waveDeviation_timeduration=30,
#                                     timeduration=43800,
#                                     take_profit=.08,
#                                     sell_out=0,
#                                     sell_trigbee_trigger=True,
#                                     sell_trigbee_trigger_timeduration=60*30,#mins
#                                     stagger_profits=False,
#                                     scalp_profits=False,
#                                     scalp_profits_timeduration=30,
#                                     stagger_profits_tiers=1,
#                                     limitprice_decay_timeduration=1,
#                                     skip_sell_trigbee_distance_frequency=0,
#                                     ignore_trigbee_at_power=0.01,
#                                     # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
#                                     take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
#                                     short_position=False,
#                                     use_wave_guage=False,
#                                     close_order_today=False,
#                                     revisit_trade_frequency=10 * 3600,
#                 ),
#                 "1Hour_3Month": kings_order_rules(
#                                     theme=theme,
#                                     status='active',
#                                     doubledown_timeduration=60,
#                                     trade_using_limits=False,
#                                     max_profit_waveDeviation=2,
#                                     max_profit_waveDeviation_timeduration=60,
#                                     timeduration=43800 * 3,
#                                     take_profit=.1,
#                                     sell_out=0,
#                                     sell_trigbee_trigger=True,
#                                     sell_trigbee_trigger_timeduration=60*60,#mins
#                                     stagger_profits=False,
#                                     scalp_profits=False,
#                                     scalp_profits_timeduration=30,
#                                     stagger_profits_tiers=1,
#                                     limitprice_decay_timeduration=1,
#                                     skip_sell_trigbee_distance_frequency=0,
#                                     ignore_trigbee_at_power=0.01,
#                                     # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
#                                     take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
#                                     short_position=False,
#                                     use_wave_guage=False,
#                                     close_order_today=False,
#                                     revisit_trade_frequency=10 * 3600,
#                 ),
#                 "2Hour_6Month": kings_order_rules(
#                                     theme='nuetral',
#                                     status='active',
#                                     doubledown_timeduration=60,
#                                     trade_using_limits=False,
#                                     max_profit_waveDeviation=2,
#                                     max_profit_waveDeviation_timeduration=120,
#                                     timeduration=43800 * 6,
#                                     take_profit=.2,
#                                     sell_out=0,
#                                     sell_trigbee_trigger=True,
#                                     sell_trigbee_trigger_timeduration=60*120,#mins
#                                     stagger_profits=False,
#                                     scalp_profits=False,
#                                     scalp_profits_timeduration=30,
#                                     stagger_profits_tiers=1,
#                                     limitprice_decay_timeduration=1,
#                                     skip_sell_trigbee_distance_frequency=0,
#                                     ignore_trigbee_at_power=0.01,
#                                     # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
#                                     take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
#                                     short_position=False,
#                                     use_wave_guage=False,
#                                     close_order_today=False,
#                                     revisit_trade_frequency=10 * 3600,
#                 ),
#                 "1Day_1Year": kings_order_rules(
#                                     theme=theme,
#                                     status='active',
#                                     doubledown_timeduration=60,
#                                     trade_using_limits=False,
#                                     max_profit_waveDeviation=3,
#                                     max_profit_waveDeviation_timeduration=60 * 24, 
#                                     timeduration=525600,
#                                     take_profit=.5,
#                                     sell_out=0,
#                                     sell_trigbee_trigger=True,
#                                     sell_trigbee_trigger_timeduration=60*300,#mins
#                                     stagger_profits=False,
#                                     scalp_profits=False,
#                                     scalp_profits_timeduration=30,
#                                     stagger_profits_tiers=1,
#                                     limitprice_decay_timeduration=1,
#                                     skip_sell_trigbee_distance_frequency=0,
#                                     ignore_trigbee_at_power=0.01,
#                                     # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
#                                     take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
#                                     short_position=False,
#                                     use_wave_guage=False,
#                                     close_order_today=False,
#                                     revisit_trade_frequency=60 * 3600,
#                 ),
#             }
#         elif theme.lower() == 'long_star':
#             symbol_theme_vars = symbol_theme_vars
#             star_theme_vars = {
#                 "1Minute_1Day": {
#                     'stagger_profits':False, 
#                     'buyingpower_allocation_LongTerm': 0,
#                     'buyingpower_allocation_ShortTerm': 0,
#                     'use_margin': False,
#                     },
#                 "5Minute_5Day" : {
#                     'stagger_profits':False, 
#                     'buyingpower_allocation_LongTerm': .3,
#                     'buyingpower_allocation_ShortTerm': 0,
#                     'use_margin': False,
#                     },
#                 "30Minute_1Month": {
#                     'stagger_profits':False, 
#                     'buyingpower_allocation_LongTerm': .4,
#                     'buyingpower_allocation_ShortTerm': 0,
#                     'use_margin': False,
#                     },
#                 "1Hour_3Month": {
#                     'stagger_profits':False, 
#                     'buyingpower_allocation_LongTerm': .5,
#                     'buyingpower_allocation_ShortTerm': 0,
#                     'use_margin': False,
#                     },
#                 "2Hour_6Month": {
#                     'stagger_profits':False, 
#                     'buyingpower_allocation_LongTerm': .8,
#                     'buyingpower_allocation_ShortTerm': 0,
#                     'use_margin': False,
#                     },
#                 "1Day_1Year": {
#                     'stagger_profits':False, 
#                     'buyingpower_allocation_LongTerm': .89,
#                     'buyingpower_allocation_ShortTerm': 0,
#                     'use_margin': False,
#                     },
#         }
#             wave_block_theme__kor = {
#                 "1Minute_1Day": kings_order_rules(
#                                     theme=theme,
#                                     status='active',
#                                     doubledown_timeduration=60,
#                                     trade_using_limits=False,
#                                     max_profit_waveDeviation=1,
#                                     max_profit_waveDeviation_timeduration=5,
#                                     timeduration=120,
#                                     take_profit=.005,
#                                     sell_out=-.089,
#                                     sell_trigbee_trigger=True,
#                                     stagger_profits=False,
#                                     scalp_profits=False,
#                                     scalp_profits_timeduration=30,
#                                     stagger_profits_tiers=1,
#                                     limitprice_decay_timeduration=1,
#                                     skip_sell_trigbee_distance_frequency=0,
#                                     ignore_trigbee_at_power=0.01,
#                                     # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
#                                     take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
#                                     short_position=False,
#                                     use_wave_guage=False,
#                                     close_order_today=True,
#                 ),
#                 "5Minute_5Day": kings_order_rules(
#                                     theme=theme,
#                                     status='active',
#                                     doubledown_timeduration=60,
#                                     trade_using_limits=False,
#                                     max_profit_waveDeviation=1,
#                                     max_profit_waveDeviation_timeduration=5,
#                                     timeduration=320,
#                                     take_profit=.01,
#                                     sell_out=-.0089,
#                                     sell_trigbee_trigger=True,
#                                     stagger_profits=False,
#                                     scalp_profits=False,
#                                     scalp_profits_timeduration=30,
#                                     stagger_profits_tiers=1,
#                                     limitprice_decay_timeduration=1,
#                                     skip_sell_trigbee_distance_frequency=0,
#                                     ignore_trigbee_at_power=0.01,
#                                     # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
#                                     take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
#                                     short_position=False,
#                                     use_wave_guage=False,
#                                     close_order_today=True,
#                 ),
#                 "30Minute_1Month": kings_order_rules(
#                                     theme=theme,
#                                     status='active',
#                                     doubledown_timeduration=60,
#                                     trade_using_limits=False,
#                                     max_profit_waveDeviation=1,
#                                     max_profit_waveDeviation_timeduration=30,
#                                     timeduration=43800,
#                                     take_profit=.01,
#                                     sell_out=-.0089,
#                                     sell_trigbee_trigger=True,
#                                     stagger_profits=False,
#                                     scalp_profits=False,
#                                     scalp_profits_timeduration=30,
#                                     stagger_profits_tiers=1,
#                                     limitprice_decay_timeduration=1,
#                                     skip_sell_trigbee_distance_frequency=0,
#                                     ignore_trigbee_at_power=0.01,
#                                     # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
#                                     take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
#                                     short_position=False,
#                                     use_wave_guage=False,
#                 ),
#                 "1Hour_3Month": kings_order_rules(
#                                     theme=theme,
#                                     status='active',
#                                     doubledown_timeduration=60,
#                                     trade_using_limits=False,
#                                     max_profit_waveDeviation=1,
#                                     max_profit_waveDeviation_timeduration=60,
#                                     timeduration=43800 * 3,
#                                     take_profit=.01,
#                                     sell_out=-.0089,
#                                     sell_trigbee_trigger=True,
#                                     stagger_profits=False,
#                                     scalp_profits=False,
#                                     scalp_profits_timeduration=30,
#                                     stagger_profits_tiers=1,
#                                     limitprice_decay_timeduration=1,
#                                     skip_sell_trigbee_distance_frequency=0,
#                                     ignore_trigbee_at_power=0.01,
#                                     # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
#                                     take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
#                                     short_position=False,
#                                     use_wave_guage=False,
#                 ),
#                 "2Hour_6Month": kings_order_rules(
#                                     theme='nuetral',
#                                     status='active',
#                                     doubledown_timeduration=60,
#                                     trade_using_limits=False,
#                                     max_profit_waveDeviation=1,
#                                     max_profit_waveDeviation_timeduration=120,
#                                     timeduration=43800 * 6,
#                                     take_profit=.01,
#                                     sell_out=-.0089,
#                                     sell_trigbee_trigger=True,
#                                     stagger_profits=False,
#                                     scalp_profits=False,
#                                     scalp_profits_timeduration=30,
#                                     stagger_profits_tiers=1,
#                                     limitprice_decay_timeduration=1,
#                                     skip_sell_trigbee_distance_frequency=0,
#                                     ignore_trigbee_at_power=0.01,
#                                     # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
#                                     take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
#                                     short_position=False,
#                                     use_wave_guage=False,
#                 ),
#                 "1Day_1Year": kings_order_rules(
#                                     theme=theme,
#                                     status='active',
#                                     doubledown_timeduration=60,
#                                     trade_using_limits=False,
#                                     max_profit_waveDeviation=1,
#                                     max_profit_waveDeviation_timeduration=60 * 24, 
#                                     timeduration=525600,
#                                     take_profit=.05,
#                                     sell_out=-.015,
#                                     sell_trigbee_trigger=True,
#                                     stagger_profits=False,
#                                     scalp_profits=False,
#                                     scalp_profits_timeduration=30,
#                                     stagger_profits_tiers=1,
#                                     limitprice_decay_timeduration=1,
#                                     skip_sell_trigbee_distance_frequency=0,
#                                     ignore_trigbee_at_power=0.01,
#                                     # ignore_trigbee_in_vwap_range={"low_range": -0.05, "high_range": 0.05},
#                                     take_profit_in_vwap_deviation_range={"low_range": -0.05, "high_range": 0.05},
#                                     short_position=False,
#                                     use_wave_guage=False,
#                 ),
#             }
#         else: # custom catch all ? Random AI
#             print("there is no else, get it right")

#         return symbol_theme_vars, star_theme_vars,  wave_block_theme__kor
    
#     def star_trading_model_vars(star_theme_vars, wave_block_theme__kor, trigbees, stars=stars):

#         def star_kings_order_rules_mapping(stars, trigbees, waveBlocktimes, wave_block_theme__kor=wave_block_theme__kor,):
#             # symbol_theme_vars, star_theme_vars, wave_block_theme__kor =  theme_king_order_rules(theme=theme, stars=stars)
#             # star_kings_order_rules_dict["1Minute_1Day"][trigbee]
#             # for theme in themes
#             # import copy
#             star_kings_order_rules_dict = {} # Master Return
#             for star in stars().keys():
#                 star_kings_order_rules_dict[star] = {}
#                 for trigbee in trigbees:
#                     star_kings_order_rules_dict[star][trigbee] = {}
#                     for blocktime in waveBlocktimes:
#                         star_kings_order_rules_dict[star][trigbee][blocktime] = wave_block_theme__kor.get(star) # theme=theme

#             return star_kings_order_rules_dict

#         def star_vars_mapping(star_theme_vars, trigbees, waveBlocktimes, stars=stars,theme=theme,):
#             return_dict = {}
            
#             trigbees_king_order_rules = star_kings_order_rules_mapping(stars=stars, trigbees=trigbees, waveBlocktimes=waveBlocktimes)
            
#             star = "1Minute_1Day"
#             return_dict[star] = {
#                 "total_budget": 0,
#                 "trade_using_limits": False,
#                 "buyingpower_allocation_LongTerm": star_theme_vars[star].get('buyingpower_allocation_LongTerm'),
#                 "buyingpower_allocation_ShortTerm": star_theme_vars[star].get('buyingpower_allocation_ShortTerm'),
#                 "stagger_profits": star_theme_vars[star].get('stagger_profits'),
#                 "use_margin": star_theme_vars[star].get('use_margin'),
#                 "power_rangers": {k: 1 for k in stars().keys()},
#                 "trigbees": trigbees_king_order_rules[star],
#                 "short_position": False,
#                 "ticker_family": [ticker],
#                 "theme": theme,
#             }
#             star = "5Minute_5Day"
#             return_dict[star] = {
#                 "total_budget": 0,
#                 "trade_using_limits": False,
#                 "buyingpower_allocation_LongTerm": star_theme_vars[star].get('buyingpower_allocation_LongTerm'),
#                 "buyingpower_allocation_ShortTerm": star_theme_vars[star].get('buyingpower_allocation_ShortTerm'),
#                 "stagger_profits": star_theme_vars[star].get('stagger_profits'),
#                 "use_margin": star_theme_vars[star].get('use_margin'),
#                 "power_rangers": {k: 1 for k in stars().keys()},
#                 "trigbees": trigbees_king_order_rules[star],
#                 "short_position": False,
#                 "ticker_family": [ticker],
#                 "theme": theme,
#             }
#             star = "30Minute_1Month"
#             return_dict[star] = {
#                 "total_budget": 0,
#                 "trade_using_limits": False,
#                 "buyingpower_allocation_LongTerm": star_theme_vars[star].get('buyingpower_allocation_LongTerm'),
#                 "buyingpower_allocation_ShortTerm": star_theme_vars[star].get('buyingpower_allocation_ShortTerm'),
#                 "stagger_profits": star_theme_vars[star].get('stagger_profits'),
#                 "use_margin": star_theme_vars[star].get('use_margin'),
#                 "power_rangers": {k: 1 for k in stars().keys()},
#                 "trigbees": trigbees_king_order_rules[star],
#                 "short_position": False,
#                 "ticker_family": [ticker],
#                 "theme": theme,
#             }
#             star = "1Hour_3Month"
#             return_dict[star] = {
#                 "total_budget": 0,
#                 "trade_using_limits": False,
#                 "buyingpower_allocation_LongTerm": star_theme_vars[star].get('buyingpower_allocation_LongTerm'),
#                 "buyingpower_allocation_ShortTerm": star_theme_vars[star].get('buyingpower_allocation_ShortTerm'),
#                 "stagger_profits": star_theme_vars[star].get('stagger_profits'),
#                 "use_margin": star_theme_vars[star].get('use_margin'),
#                 "power_rangers": {k: 1 for k in stars().keys()},
#                 "trigbees": trigbees_king_order_rules[star],
#                 "short_position": False,
#                 "ticker_family": [ticker],
#                 "theme": theme,
#             }
#             star = "2Hour_6Month"
#             return_dict[star] = {
#                 "total_budget": 0,
#                 "trade_using_limits": False,
#                 "buyingpower_allocation_LongTerm": star_theme_vars[star].get('buyingpower_allocation_LongTerm'),
#                 "buyingpower_allocation_ShortTerm": star_theme_vars[star].get('buyingpower_allocation_ShortTerm'),
#                 "stagger_profits": star_theme_vars[star].get('stagger_profits'),
#                 "use_margin": star_theme_vars[star].get('use_margin'),
#                 "power_rangers": {k: 1 for k in stars().keys()},
#                 "trigbees": trigbees_king_order_rules[star],
#                 "short_position": False,
#                 "ticker_family": [ticker],
#                 "theme": theme,
#             }
#             star = "1Day_1Year"
#             return_dict[star] = {
#                 "total_budget": 0,
#                 "trade_using_limits": False,
#                 "buyingpower_allocation_LongTerm": star_theme_vars[star].get('buyingpower_allocation_LongTerm'),
#                 "buyingpower_allocation_ShortTerm": star_theme_vars[star].get('buyingpower_allocation_ShortTerm'),
#                 "stagger_profits": star_theme_vars[star].get('stagger_profits'),
#                 "use_margin": star_theme_vars[star].get('use_margin'),
#                 "power_rangers": {k: 1 for k in stars().keys()},
#                 "trigbees": trigbees_king_order_rules[star],
#                 "short_position": False,
#                 "ticker_family": [ticker],
#                 "theme": theme,
#             }

#             return return_dict

#         def star_vars(star, star_vars_mapping):
#             return {
#                 "star": star,
#                 # 'status': star_vars_mapping[star]['status'],
#                 "trade_using_limits": star_vars_mapping[star]["trade_using_limits"],
#                 "total_budget": star_vars_mapping[star]["total_budget"],
#                 "buyingpower_allocation_LongTerm": star_vars_mapping[star]["buyingpower_allocation_LongTerm"],
#                 "buyingpower_allocation_ShortTerm": star_vars_mapping[star]["buyingpower_allocation_ShortTerm"],
#                 "power_rangers": star_vars_mapping[star]["power_rangers"],
#                 "trigbees": star_vars_mapping[star]["trigbees"],
#                 "short_position": star_vars_mapping[star]["short_position"],
#                 "ticker_family": star_vars_mapping[star]["ticker_family"],
#             }

#         # Get Stars Trigbees and Blocktimes to create kings order rules
#         all_stars = stars().keys()
#         waveBlocktimes = [
#             "premarket",
#             "morning_9-11",
#             "lunch_11-2",
#             "afternoon_2-4",
#             "afterhours",
#             "Day",
#         ]
#         star_vars_mapping_dict = star_vars_mapping(
#             trigbees=trigbees, waveBlocktimes=waveBlocktimes, stars=stars, theme=theme, star_theme_vars=star_theme_vars
#         )

#         return_dict = {
#             star: star_vars(star=star, star_vars_mapping=star_vars_mapping_dict)
#             for star in all_stars
#         }

#         return return_dict

#     def model_vars(trading_model_name, star, stars_vars, stars=stars):
#         return {
#             # 'status': stars_vars[star]['status'],
#             "buyingpower_allocation_LongTerm": stars_vars[star]["buyingpower_allocation_LongTerm"],
#             "buyingpower_allocation_ShortTerm": stars_vars[star]["buyingpower_allocation_ShortTerm"],
#             "power_rangers": stars_vars[star]["power_rangers"],
#             "trade_using_limits": stars_vars[star]["trade_using_limits"],
#             "total_budget": stars_vars[star]["total_budget"],
#             "trigbees": stars_vars[star]["trigbees"],
#             "index_inverse_X": "1X",
#             "index_long_X": "1X",
#             "trading_model_name": trading_model_name,
#         }

#     def tradingmodel_vars(
#         symbol_theme_vars,
#         stars_vars,
#         trigbees=trigbees,
#         ticker=ticker,
#         trading_model_name=trading_model_name,
#         status=status,
#         portforlio_weight_ask=portforlio_weight_ask,
#         stars=stars,
#         portfolio_name=portfolio_name,
#         theme=theme,):
        
#         afterhours = True if ticker in crypto_currency_symbols else False
#         afternoon = True if ticker in crypto_currency_symbols else True
#         lunch = True if ticker in crypto_currency_symbols else True
#         morning = True if ticker in crypto_currency_symbols else True
#         premarket = True if ticker in crypto_currency_symbols else False
#         Day = True if ticker in crypto_currency_symbols else False

#         time_blocks = {
#             "premarket": premarket,
#             "afterhours": afterhours,
#             "morning_9-11": morning,
#             "lunch_11-2": lunch,
#             "afternoon_2-4": afternoon,
#             "afterhours": afterhours,
#             "Day": Day,
#         }

#         allow_for_margin = [False if ticker in crypto_currency_symbols else True][0]
#         # etf_X_direction = ["1X", "2X", "3X"]  # Determined by QUEEN

#         def init_stars_allocation():
#             return {}

#         model1 = {
#             "theme": theme,
#             "QueenBeeTrader": "Jq",
#             "status": status,
#             "buyingpower_allocation_LongTerm": 1,
#             "buyingpower_allocation_ShortTerm": 0,
#             "index_long_X": "1X",
#             "index_inverse_X": "1X",
#             "portforlio_weight_ask": portforlio_weight_ask,
#             "total_budget": 0,
#             "max_single_trade_amount": 100000,
#             "allow_for_margin": allow_for_margin,
#             "buy_ONLY_by_accept_from_QueenBeeTrader": False,
#             "trading_model_name": trading_model_name,
#             "portfolio_name": portfolio_name,
#             "trigbees": {k: True for k in trigbees},
#             "time_blocks": time_blocks,
#             "power_rangers": {k: True for k in stars().keys()},
#             "stars": {k: True for k in stars().keys()},
#             "stars_kings_order_rules": {
#                 star: model_vars(
#                     trading_model_name=trading_model_name,
#                     star=star,
#                     stars_vars=stars_vars,
#                 )
#                 for star in stars().keys()
#             },
#             "short_position": False,  # flip all star allocation to short
#             "ticker_family": [ticker],
#             "refresh_star" : None, # WORKERBEE needs to update model to add in different stars
#         }

#         star_model = {ticker: model1}

#         return star_model

#     try:
#         # Trading Model Version 1
#         symbol_theme_vars, star_theme_vars, wave_block_theme__kor =  theme_king_order_rules(theme=theme, stars=stars)
#         stars_vars = star_trading_model_vars(star_theme_vars, wave_block_theme__kor, trigbees)
#         # {ticker: model_vars}
#         macd_model = tradingmodel_vars(symbol_theme_vars=symbol_theme_vars, stars_vars=stars_vars)

#         # if init==False:
#         #     print(f'{trading_model_name} {ticker} {theme} Model Generated')

#         return {"MACD": macd_model}
#     except Exception as e:
#         print_line_of_error("generate trading model error")
#         return None


import os
import sqlite3


def hive_master_root():
    return os.getcwd()


def init_clientUser_dbroot(client_user):
    main_root = hive_master_root() # os.getcwd()  # hive root
    client_user_db_dir = os.path.join(os.path.dirname(main_root), 'client_user_dbs')

    if client_user in ['stefanstapinski@gmail.com', 'pollen']:  ## admin
        db_root = os.path.join(main_root, 'db')
    else:
        client_user = client_user.split("@")[0]
        db_root = os.path.join(client_user_db_dir, f'db__{client_user}')
        if os.path.exists(db_root) == False:
            os.mkdir(db_root)
            os.mkdir(os.path.join(db_root, 'logs'))

    return db_root


def init_symbol_dbs__pollenstory():
    main_root = hive_master_root() # os.getcwd()  # hive root
    symbol_dbs = os.path.join(os.path.dirname(main_root), 'symbols_pollenstory_dbs')

    if os.path.exists(symbol_dbs) == False:
        print("Init symbols_dbs")
        os.mkdir(symbol_dbs)

    return symbol_dbs


def streamlit_config_colors():
    # read config file and parse from there
    return {
    'default_text_color': '#59490A',
    'default_font': "sans serif",
    'default_yellow_color': '#C5B743',
    }


def local__filepaths_misc():
    
    jpg_root = os.path.join(hive_master_root(), 'misc')
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
    queen_flair_gif = os.path.join(jpg_root, 'queen_flair.gif')
    chess_piece_queen = "https://cdn.pixabay.com/photo/2012/04/18/00/42/chess-36311_960_720.png"
    runaway_bee_gif = os.path.join(jpg_root, 'runaway_bee_gif.gif')
    queen_png = "https://cdn.shopify.com/s/files/1/0925/9070/products/160103_queen_chess_piece_wood_shape_600x.png?v=1461105893"
    castle_png = "https://images.vexels.com/media/users/3/255175/isolated/lists/3c6de0f0c883416d9b6bd981a4471092-rook-chess-piece-line-art.png"
    bishop_png = "https://images.vexels.com/media/users/3/255170/isolated/lists/efeb124323c55a60510564779c9e1d38-bishop-chess-piece-line-art.png"
    knight_png = "https://cdn2.iconfinder.com/data/icons/chess-set-pieces/100/Chess_Set_04-White-Classic-Knight-512.png"
    queen_flair_gif = os.path.join(jpg_root, 'queen_flair.gif')
    mainpage_bee_png = "https://i.pinimg.com/originals/a8/95/e8/a895e8e96c08357bfeb92d3920cd7da0.png"
    runaway_bee_gif = os.path.join(jpg_root, 'runaway_bee_gif.gif')
    floating_queen_gif = os.path.join(jpg_root, "floating-queen-unscreen.gif")
    chess_board__gif = os.path.join(jpg_root, "chess_board.gif")
    bishop_unscreen = os.path.join(jpg_root, "bishop_unscreen.gif")
    alpaca_portfolio_keys_png = os.path.join(jpg_root, "alpaca_portfolio_snap_keys.PNG")

    return {
        'jpg_root': jpg_root,
        'bee_image': bee_image,
        'bee_power_image': bee_power_image,
        'hex_image': hex_image,
        'hive_image': hive_image,
        'queen_image': queen_image,
        'queen_angel_image': queen_angel_image,
        'flyingbee_gif_path': flyingbee_gif_path,
        'flyingbee_grey_gif_path': flyingbee_grey_gif_path,
        'bitcoin_gif': bitcoin_gif,
        'power_gif': power_gif,
        'uparrow_gif': uparrow_gif,
        'learningwalk_bee': learningwalk_bee,
        'queen_flair_gif': queen_flair_gif,
        'chess_piece_queen': chess_piece_queen,
        'runaway_bee_gif': runaway_bee_gif,
        'castle_png': castle_png,
        'bishop_png': bishop_png,
        'knight_png': knight_png,
        'queen_png': queen_png,
        'queen_flair_gif': queen_flair_gif,
        'mainpage_bee_png': mainpage_bee_png,
        'runaway_bee_gif': runaway_bee_gif,
        'floating_queen_gif': floating_queen_gif,
        'chess_board__gif': chess_board__gif,
        'bishop_unscreen': bishop_unscreen,
        'alpaca_portfolio_keys_png':alpaca_portfolio_keys_png,
    }

def kingdom__grace_to_find_a_Queen():
    # create list for userdb
    con = sqlite3.connect("db/users.db")
    cur = con.cursor()
    users = cur.execute("SELECT * FROM users").fetchall()
    
    users_allowed_queen_email = [
        "stevenweaver8@gmail.com",
        "stefanstapinski@gmail.com",
        "adivergentthinker@gmail.com",
    ]

    users_allowed_queen_emailname = [client_user.split("@")[0] for client_user in users_allowed_queen_email]

    return users_allowed_queen_email, users_allowed_queen_emailname
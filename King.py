import os

def hive_master_root():
    return os.getcwd()


def init_clientUser_dbroot(client_user):
    main_root = hive_master_root() # os.getcwd()  # hive root
    if client_user in ['stefanstapinski@gmail.com', 'pollen']:  ## admin
        db_root = os.path.join(main_root, 'db')
    else:
        client_user = client_user.split("@")[0]
        db_root = os.path.join(main_root, f'db__{client_user}')
        if os.path.exists(db_root) == False:
            os.mkdir(db_root)
            os.mkdir(os.path.join(db_root, 'logs'))

    return db_root


def streamlit_config_colors():
    # read config file and parse from there
    return {
    'default_text_color': '#59490A',
    'default_font': "sans serif",
    'default_yellow_color': '#C5B743',
    }
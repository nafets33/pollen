# LiveBot
from pages.conscience import queens_conscience
from chess_piece.queen_hive import init_queenbee, kingdom__grace_to_find_a_Queen
from chess_piece.king import return_app_ip
import streamlit as st


def demo_bot():
    client_user = 'stefanstapinski@gmail.com'
    prod = False
    KING, users_allowed_queen_email, users_allowed_queen_emailname__db = kingdom__grace_to_find_a_Queen()

    st.session_state["ip_address"] = return_app_ip()
    st.session_state["username"] = client_user
    st.session_state['db_root'] = 'db__stefanstapinski_11854791'
    st.session_state['prod'] = False
    

    qb = init_queenbee(client_user=client_user, prod=prod, 
                       queen_king=True, api=True, init=True, 
                       revrec=True, 
                       demo=True)
    QUEEN_KING = qb.get('QUEEN_KING')
    api = qb.get('api')
    revrec = qb.get('revrec') 
    queens_conscience(revrec, KING, QUEEN_KING, api, sneak_peak=True)
if __name__ == '__main__':
    demo_bot()
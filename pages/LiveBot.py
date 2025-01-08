# LiveBot
from pages.conscience import queens_conscience
from chess_piece.queen_hive import init_queenbee, kingdom__grace_to_find_a_Queen
import streamlit as st


st.session_state['sneak_peak'] = True
client_user = 'stefanstapinski@yahoo.com'
prod = False
KING, users_allowed_queen_email, users_allowed_queen_emailname__db = kingdom__grace_to_find_a_Queen()

qb = init_queenbee(client_user=client_user, prod=prod, queen_king=True, api=True, init=True, revrec=True)
QUEEN_KING = qb.get('QUEEN_KING')
api = qb.get('api')
revrec = qb.get('revrec') 
queens_conscience(revrec, KING, QUEEN_KING, api)

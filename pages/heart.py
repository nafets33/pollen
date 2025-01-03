import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from dotenv import load_dotenv
import os
from pq_auth import signin_main

signin_main()

if 'authentication_status' not in st.session_state or st.session_state['authentication_status'] != True:
    switch_page('pollen')

from chess_piece.king import print_line_of_error, master_swarm_KING
from chess_piece.queen_hive import init_queenbee, hive_master_root, ReadPickleData, PickleData
print("HeartBeat")
def find_all_circular_references(obj, seen=None, path="root", found_refs=None):
    if seen is None:
        seen = set()
    if found_refs is None:
        found_refs = []

    # Check if the object ID has already been encountered
    if id(obj) in seen:
        circular_ref_path = f"Circular reference detected at: {path}"
        print(circular_ref_path)
        found_refs.append(circular_ref_path)
        return found_refs

    # Add the current object ID to the seen set
    seen.add(id(obj))

    # Recursively check for circular references in dictionaries and lists
    if isinstance(obj, dict):
        for key, value in obj.items():
            find_all_circular_references(value, seen.copy(), path=f"{path} -> {key}", found_refs=found_refs)
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            find_all_circular_references(item, seen.copy(), path=f"{path} -> [{index}]", found_refs=found_refs)

    # Return the list of all found circular references
    return found_refs

main_root = hive_master_root()
load_dotenv(os.path.join(main_root, ".env"))

client_user=st.session_state['client_user']
prod=st.session_state['prod']

KING = ReadPickleData(master_swarm_KING(prod=prod))

qb = init_queenbee(client_user, prod, queen=True, queen_king=True, api=True, queen_heart=True)
QUEEN = qb.get('QUEEN')
QUEEN_KING = qb.get('QUEEN_KING')
api = qb.get('api')
QUEENsHeart = qb.get('QUEENsHeart')

tabs = st.tabs([i for i in QUEEN.keys()])
c = 0
for k,v in QUEEN.items():
    with tabs[c]:
        # st.write(type(v))
        c+=1
        st.write( "------------------------------")

st.write(QUEEN['queen'].keys())

st.write("HB", QUEENsHeart['heartbeat'].keys())
# st.write("HB", QUEEN['heartbeat'])
# st.write("cleaned", QUEEN['heartbeat']['beat'].keys())
# st.write("CB", QUEEN['heartbeat']['charlie_bee'].keys())

if find_all_circular_references(QUEENsHeart):
    print("C Error")
try:
    with st.expander("Heartbeat"):
        st.write(QUEENsHeart)
except Exception as e:
    print(e)

try:
    with st.expander("QUEENsHeart"):
        for k, v in QUEEN['heartbeat'].items():
            st.write(k, v)
except Exception as e:
    print(e)
if st.button("Queen Heartbeat Surgery"):
    if 'heartbeat' in QUEENsHeart['heartbeat'].keys():
        print("CLEAN Heartbeat")
        QUEENsHeart['heartbeat'].pop('heartbeat') 
    if 'beat' in QUEENsHeart['heartbeat'].keys():
        print("CLEAN beat")
        QUEENsHeart['heartbeat'].pop('beat')

    if 'heartbeat' in QUEEN['heartbeat'].keys():
        print("CLEAN heartbeat")
        QUEEN['heartbeat'].pop('heartbeat')
    if 'beat' in QUEEN['heartbeat'].keys():
        print("CLEAN beat")
        QUEEN['heartbeat'].pop('beat')
    # if 'charelie_bee' in QUEEN['heartbeat'].keys():
    #     QUEEN['heartbeat'].pop('charelie_bee')

    PickleData(QUEEN.get('source'), QUEEN)
    PickleData(QUEENsHeart.get('source'), QUEENsHeart)

st.header("order update requests")
st.write(QUEEN_KING['update_order_rules'])
if st.button('clear update order requests'):
    QUEEN_KING['update_order_rules'] = []
    PickleData(QUEEN_KING.get('source'), QUEEN_KING)
    st.success('app requests cleared')
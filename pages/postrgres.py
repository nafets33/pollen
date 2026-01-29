import pandas as pd
import os
import pandas as pd
from datetime import datetime, timedelta, date
import pytz
from dotenv import load_dotenv
import os
import streamlit as st
from pq_auth import signin_main

# main chess piece
from chess_piece.king import return_db_root, ReadPickleData
from chess_piece.queen_hive import return_all_client_users__db, init_queenbee, init_swarm_dbs
from chess_piece.app_hive import trigger_py_script, standard_AGgrid
from chess_piece.pollen_db import PollenDatabase, MigratePostgres
from tqdm import tqdm

import sys

pg_migration = os.environ.get('pg_migration')

pd.options.mode.chained_assignment = None
est = pytz.timezone("US/Eastern")

if 'authorized_user' not in st.session_state:
    signin_main("workerbees")

if st.session_state["authorized_user"] != True:
    st.error("you do not have permissions young fellow")
    st.stop()

client_user = st.session_state['username']
prod = st.session_state['prod']
if not prod:
    st.warning(f'SandBox')



def get_size_of_object(obj):
    """Get approximate size of object in bytes."""
    if isinstance(obj, pd.DataFrame):
        return obj.memory_usage(deep=True).sum()
    else:
        return sys.getsizeof(obj)

def inspect_key_breakdown(table_name, key):
    """Show size breakdown of nested keys using existing retrieve_data."""
    st.subheader(f"📊 Data Breakdown for: `{key}`")
    
    # Use your existing retrieve_data function
    with st.spinner(f"Loading {key}..."):
        data = PollenDatabase.retrieve_data(table_name, key)
    
    if not data:
        st.error(f"No data found for key: {key}")
        return
    
    # Calculate sizes
    size_data = []
    total_size = 0
    
    if isinstance(data, dict):
        for nested_key, value in data.items():
            # Skip metadata fields added by retrieve_data
            if nested_key in ['key', 'table_name', 'db_root']:
                continue
                
            size_bytes = get_size_of_object(value)
            total_size += size_bytes
            
            # Get type info
            if isinstance(value, pd.DataFrame):
                value_type = f"DataFrame ({len(value)} rows × {len(value.columns)} cols)"
            elif isinstance(value, dict):
                value_type = f"dict ({len(value)} keys)"
            elif isinstance(value, list):
                value_type = f"list ({len(value)} items)"
            else:
                value_type = type(value).__name__
            
            size_data.append({
                'nested_key': nested_key,
                'type': value_type,
                'size_bytes': size_bytes,
                'size_kb': round(size_bytes / 1024, 2),
                'size_mb': round(size_bytes / (1024**2), 3),
            })
    
    if not size_data:
        st.warning("No nested data found (or data is not a dict)")
        return
    
    # Calculate percentages
    for item in size_data:
        item['pct_of_total'] = round((item['size_bytes'] / total_size) * 100, 2)
    
    # Create DataFrame and sort by size
    df_sizes = pd.DataFrame(size_data).sort_values('size_bytes', ascending=False)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Size", f"{total_size / (1024**2):.2f} MB")
    with col2:
        st.metric("Nested Keys", len(df_sizes))
    with col3:
        if len(df_sizes) > 0:
            largest = df_sizes.iloc[0]['nested_key']
            st.metric("Largest Key", largest)
    
    # Show table
    st.dataframe(
        df_sizes[['nested_key', 'type', 'size_mb', 'pct_of_total']],
        use_container_width=True,
        hide_index=True
    )
    
    # Show chart
    if len(df_sizes) > 1:
        st.bar_chart(df_sizes.set_index('nested_key')['size_mb'])
    
    # Quick preview option
    st.divider()
    selected_key = st.selectbox(
        "Preview nested key:",
        options=df_sizes['nested_key'].tolist(),
        key=f"preview_{table_name}_{key}"
    )
    
    if st.button("Show Preview", key=f"btn_preview_{table_name}_{key}"):
        nested_value = data[selected_key]
        
        st.write(f"**Type:** `{type(nested_value).__name__}`")
        
        if isinstance(nested_value, pd.DataFrame):
            st.write(f"**Shape:** {nested_value.shape}")
            st.dataframe(nested_value.head(20))
        elif isinstance(nested_value, dict):
            st.json({k: str(type(v).__name__) for k, v in list(nested_value.items())[:20]})
        elif isinstance(nested_value, list):
            st.write(f"**Length:** {len(nested_value)}")
            st.json(nested_value[:20])
        else:
            st.write(nested_value)

def create_pg_table():
    table_name = st.text_input('Table Name', 'db_store')
    if st.button(f"Create {table_name}"):
        PollenDatabase.create_table_if_not_exists(table_name)
        st.success(f"{table_name} created")


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


def get_connection_and_cursor():
    conn = MigratePostgres.get_server_connection()
    cur = conn.cursor()
    return conn, cur


def copy_data_between_tables(source_table, target_table):
    try:
        # Get connection and cursor
        source_con, source_cur = PollenDatabase.return_db_conn(return_curser=True)
        target_con, target_cur = get_connection_and_cursor()

        # Fetch data from the source table
        source_cur.execute(f"SELECT * FROM {source_table};")
        rows = source_cur.fetchall()

        # Get column names from the source table
        source_cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{source_table}';")
        columns = [row[0] for row in source_cur.fetchall()]
        column_list = ", ".join(columns)

        # Prepare the INSERT statement for the target table
        placeholders = ", ".join(["%s"] * len(columns))
        insert_query = f"INSERT INTO {target_table} ({column_list}) VALUES ({placeholders});"

        # Write each row into the target table
        for row in rows:
            target_cur.execute(insert_query, row)

        # Commit changes to the target table
        target_con.commit()
        print(f"Data successfully copied from {source_table} to {target_table}.")

    except Exception as e:
        print(e)
    finally:
        # Ensure both connections are closed
        if source_cur:
            source_cur.close()
        if source_con:
            source_con.close()
        if target_cur:
            target_cur.close()
        if target_con:
            target_con.close()


if __name__ == '__main__':
    print("POSTGRES", pg_migration)

    admin = st.session_state['admin']

    if not admin:
        st.error("Join The Team for Admin Access To This Page")
        st.stop()

    tables = PollenDatabase.get_all_tables()
    tables = sorted(tables)
    db=init_swarm_dbs(prod, init=True, pg_migration=pg_migration)
    st.write(pd.DataFrame(PollenDatabase.get_all_tables_with_sizes()))

    # if st.button("DELETE ALL POLLEN_STORY data"):
    #     table_name='pollen_store'
    #     numm = st.empty()
    #     for idx, key in enumerate(PollenDatabase.get_all_keys(table_name)):
    #         if 'POLLEN_STORY' in key:
    #             PollenDatabase.delete_key(table_name, key)
    #             with numm.container():
    #                 st.write(idx)

    tab_list = ['Tables', 'Create', 'Migrate', 'Delete'] + tables
    tabs = st.tabs(tab_list)

    if admin:
        with tabs[3]:
            del_tables = st.selectbox("delete table", options=tables)
            if st.button(f"Delete Table {del_tables}"):
                PollenDatabase.delete_table(del_tables)
                st.success(f"Table {del_tables} Deleted")
            sub_tabs = st.tabs([i for i in tables])
            s_t = 0
            for table in tables:
                with sub_tabs[s_t]:
                    # with st.form(f"Del Key Table {table}"):
                    table_keys = PollenDatabase.get_all_keys(table_name=table)
                    del_key = st.selectbox(f"delete key from {table}", options=table_keys, key=table)
                    # print(del_key)
                    if del_key:
                        if st.button(f"Delete Key {table} {del_key}"):
                            # data = PollenDatabase.retrieve_data(table, key=del_key)
                            PollenDatabase.delete_key(table, key_column=del_key)
                s_t+=1
        s_t = 4
        for table in tables:
            with tabs[s_t]:
                st.write(table)
                df = pd.DataFrame(
                    PollenDatabase.get_all_keys_with_timestamps_and_sizes(table)
                ).rename(columns={
                    0: 'key', 
                    1: 'timestamp', 
                    2: 'size_bytes',      # Add raw bytes
                    3: 'size_display'     # Human readable
                })                # df[2] = pd.to_numeric(2)
                # st.write(sum(df[2]))
                if table == 'client_user_store':
                    try:
                        df['key_name'] = df['key'].apply(lambda x: x.split("-")[-1])
                    except Exception as e:
                        print("PG", e)
                if len(df) > 0:
                    dat = df.iloc[0].get('timestamp')

                st.write(df)

                # Key Inspector
                st.divider()
                if len(df) > 0:
                    selected_key = st.selectbox(
                        f"Select key to inspect:",
                        options=df['key'].tolist(),
                        key=f"select_{table}"
                    )
                    
                    if st.button("🔍 Inspect Key", key=f"inspect_{table}"):
                        inspect_key_breakdown(table, selected_key)

                s_t+=1

        with tabs[1]:
            create_pg_table()
        with tabs[0]: 
            st.subheader("Migrate local-PG to PG-Server")
            migrated_data = []
            tables_to_migrate = st.multiselect('migrate Tables', options=tables)
            migrate_keys_that_contain = st.text_input('migrate Keys that contain text (optional)', value='')
            if st.button(f"Migrate PostGres Table Keys {tables_to_migrate}"):
                # Create progress bar for tables
                table_progress = st.progress(0)
                table_status = st.empty()
                
                migrated_data = []
                total_tables = len(tables_to_migrate)
                
                for table_idx, table in enumerate(tables_to_migrate):
                    # Update table progress
                    table_progress.progress((table_idx) / total_tables)
                    table_status.text(f"Processing table {table_idx + 1}/{total_tables}: {table}")
                    
                    if table == 'client_users':
                        copy_data_between_tables(source_table='client_users', target_table='client_users')
                        continue

                    df = pd.DataFrame(PollenDatabase.get_all_keys_with_timestamps(table)).rename(columns={0: 'key', 1: 'timestamp'})
                    
                    if migrate_keys_that_contain:
                        df = df[df['key'].str.contains(migrate_keys_that_contain)]

                    # Filter for last 3 days if table is 'pollen_store'
                    if table == 'pollen_store':
                        three_days_ago = datetime.now() - timedelta(days=3)
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                        df = df[df['timestamp'] >= three_days_ago]
                    
                    st.write(f"Table: {table} - Keys to migrate: {len(df)}")
                    
                    # Create progress bar for keys within this table
                    key_progress = st.progress(0)
                    key_status = st.empty()
                    
                    keys = df['key'].tolist()
                    total_keys = len(keys)
                    
                    for key_idx, key in enumerate(keys):
                        # Update key progress
                        if total_keys > 0:
                            key_progress.progress((key_idx + 1) / total_keys)
                            key_status.text(f"Migrating key {key_idx + 1}/{total_keys}")
                        
                        data = PollenDatabase.retrieve_data(table, key)
                        if MigratePostgres.upsert_migrate_data(table, key, data):
                            migrated_data.append({'table': table, 'key': key})
                        else:
                            st.error(f"Failed to migrate {key} in table {table}")
                    
                    # Clean up key progress bars for this table
                    key_progress.empty()
                    key_status.empty()
                
                # Complete table progress
                table_progress.progress(1.0)
                table_status.text("Migration completed!")
                
                st.success("MIGRATION COMPLETED")
                st.write(pd.DataFrame(migrated_data))

            with st.sidebar:
                table_name = st.selectbox('table_name', options=tables)
                if st.button(f'add last mod to table: {table_name}'):
                    PollenDatabase.update_table_schema(table_name)
            st.divider()
            if st.button(f'migrate_db enviroment={prod}'):
                swarm = init_swarm_dbs(prod=True, pg_migration=False)
                print(swarm)
                table_name = 'db' if prod else 'db_sandbox'
                for db_name, db_file in swarm.items():
                    data = ReadPickleData(db_file)
                    PollenDatabase.upsert_data(table_name, key=db_name, value=data)
                    st.success(f'{db_name} saved')
            
            users, all_users = return_all_client_users__db()
            grid = standard_AGgrid(all_users, height=250)
            
            with tabs[2]:
                table_name = 'client_user_store' if prod else 'client_user_store_sandbox'
                c_user = st.selectbox('Client Users', options=all_users['email'].tolist())
                c_user_root = return_db_root(c_user)
                c_user_root_name = os.path.split(c_user_root)[-1]
                st.write(f'{c_user} <> {c_user_root} <> {c_user_root_name}')

                migrate_keys = ['QUEEN_KING']
                migrate_key = st.selectbox("migrate key", options=migrate_keys)
                if st.button(f"Migration Pickle to Postgres {migrate_key}"):
                    if migrate_key == 'QUEEN_KING':
                        QUEEN_KING = init_queenbee(c_user, prod, queen_king=True, pg_migration=False).get('QUEEN_KING') # orders_final=True handle in new table
                        key_name = f'{c_user_root_name}-{"QUEEN_KING"}'
                        data = QUEEN_KING
                
                    st.write(f'Uploading {key_name}')
                    if data:
                        if not find_all_circular_references(data):
                            if PollenDatabase.upsert_data(table_name=table_name, key=key_name, value=data):
                                st.success(f'{key_name} Saved')
                        else:
                            st.error(f"{key_name} C error")
                
                st.subheader("Migrate PICKLE to PG Server")
                
                # WORKERBEE Fix OrderSv2, double check what this doing
                # if st.button(f"Migrate user {c_user_root_name} pg tables to PG Server"):
                #     st.write("PG Migration")
                #     with st.spinner("Reading Client User DB"):
                #         qb = init_queenbee(c_user, prod, queen=True, queen_king=True, orders=True, broker=True, broker_info=True, revrec=True, queen_heart=True, pg_migration=False, charlie_bee=True) # orders_final=True handle in new table
                #     for db_name in qb.keys():
                #         data = qb.get(db_name)
                #         if db_name == 'revrec':
                #             print(f'{db_name} change')
                #             db_name = 'REVREC'
                #         elif db_name == 'broker_info':
                #             print(f'{db_name} change')
                #             db_name = 'ACCOUNT_INFO'
                #             data = data.get('account_info')

                #         key_name = f'{c_user_root_name}-{db_name}'
                #         st.write(f'Uploading {key_name}')
                #         if data:
                #             if not find_all_circular_references(data):
                #                 if PollenDatabase.upsert_data(table_name=table_name, key=key_name, value=data):
                #                     st.success(f'{key_name} Saved')
                #             else:
                #                 st.error(f"{key_name} C error")
                #     st.success("MIGRATION COMPLETED")
        
            st.divider()
            st.subheader("LOCAL Copy Data Between Tables")

            col1, col2 = st.columns(2)
            with col1:
                table_main1 = st.selectbox("Source Table", options=tables, key="table_main1")
            with col2:
                table_main2 = st.selectbox("Target Table", options=tables, key="table_main2")


            if st.button(f"Copy all data from {table_main1} → {table_main2}"):
                with st.spinner(f"Copying data from {table_main1} to {table_main2}..."):
                    PollenDatabase.copy_table_to_table(table_main1, table_main2)
                st.success(f"Copied all data from {table_main1} to {table_main2}!")
        

        # VACCUM TABLE
        table_key = st.selectbox("Vaccum Table", options=tables)
        if st.button(f"Vaccum Table {table_key}"):
            PollenDatabase.vacuum_table(table_key)
        
        demo_sync = st.sidebar.toggle("Sync Orders v2 DEMO ")
        if st.toggle('Sync Orders v2'):
            if demo_sync:
                prod = False
                client_user = 'stapinskistefan@gmail.com'
            table_name = 'queen_orders' if prod else 'queen_orders_sandbox'
            print(c_user, prod)
            ORDERS = init_queenbee(client_user, prod, orders=True, pg_migration=pg_migration).get('ORDERS')
            st.write(ORDERS['db_root'])
            df = ORDERS['queen_orders']

            if st.button(f"sync orders to table **{table_name}** --{client_user} prod={prod}"):
                print('len', len(df))
                for i, idx in enumerate(df.index):
                    # print(i)
                    key = f"{ORDERS['db_root']}___{idx}"
                    data = df.loc[idx].to_dict()

                    PollenDatabase.upsert_data(table_name=table_name, key=key, value=data, console=True)
                st.success(f"Orders synced to {table_name} for {client_user} prod={prod}")
            # run_order = PollenDatabase.retrieve_data(table_name, key=f"{ORDERS.get('db_root')}___{ORDERS['queen_orders'].iloc[-1]['client_order_id']}")
            # st.write(run_order)
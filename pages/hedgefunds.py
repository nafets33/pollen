from chess_piece.queen_hive import return_Ticker_Universe
import streamlit as st
import pandas as pd
import os
from chess_piece.king import hive_master_root_db
from chess_piece.app_hive import standard_AGgrid
from pq_auth import signin_main
from chess_piece.pollen_db import PollenDatabase
from chess_piece.king import hash_string
from tqdm import tqdm

pg_migration = True #os.getenv('pg_migration')


local_db_root = hive_master_root_db()

@st.cache_data
def read_infotable():
    # if pg_migration:
    #     table_name = 'hedgefund_13f_data'
    #     keys = PollenDatabase.get_all_keys(table_name)
    #     if 'INFOTABLE' not in keys:
    #         df = pd.read_csv(os.path.join(local_db_root, 'INFOTABLE.tsv'), sep='\t')
    #         PollenDatabase.upsert_data(table_name, 'INFOTABLE', df)
    #     df = PollenDatabase.retrieve_data(table_name, 'INFOTABLE')
    # else:
    df = pd.read_csv(os.path.join(local_db_root, 'INFOTABLE.tsv'), sep='\t')
    return df

@st.cache_data
def read_filer_names_coverpage():
    # df = pd.read_csv(os.path.join(local_db_root, 'COVERPAGE.tsv'), sep='\t')

    if pg_migration:
        table_name = 'hedgefund_13f_data'
        keys = PollenDatabase.get_all_keys(table_name)
        if 'COVERPAGE' not in keys:
            df = pd.read_csv(os.path.join(local_db_root, 'COVERPAGE.tsv'), sep='\t')
            PollenDatabase.upsert_data(table_name, 'COVERPAGE', df)
        df = PollenDatabase.retrieve_data(table_name, 'COVERPAGE')
    else:
        df = pd.read_csv(os.path.join(local_db_root, 'COVERPAGE.tsv'), sep='\t')

    return df


if __name__ == '__main__':
    signin_main()

    # tabs = st.tabs(['Cover Page'])

    # COVER PAGE
    df = read_filer_names_coverpage()
    st.write("Cover Page", df)
    filer_names = dict(zip(df['ACCESSION_NUMBER'], df['FILINGMANAGER_NAME']))
    filer_names_ = {v:k for k,v in filer_names.items()}

    # # submission data
    # df = pd.read_csv(os.path.join(local_db_root, 'SUBMISSION.tsv'), sep='\t')
    # st.write("SUBMISSION", df)
    # df = pd.read_csv(os.path.join(local_db_root, 'SIGNATURE.tsv'), sep='\t')
    # st.write("SIGNATURE", df)

    # INFO TABLE MAKE A FUNCTION
    df = read_infotable()
    df = df.dropna(subset=['NAMEOFISSUER'])
    df['VALUE'] = pd.to_numeric(df['VALUE'], errors='coerce').fillna(0).astype(int)
    cusip_mapping = pd.read_csv(os.path.join(local_db_root, 'cusip_tickers.csv'))
    st.write("CUSIP MAPPING", cusip_mapping.head())
    cusip_mapping = dict(zip(cusip_mapping['CUSIP'], cusip_mapping['Ticker']))
    df['symbol'] = df['CUSIP'].map(cusip_mapping).fillna("MISSING")

    df['FILINGMANAGER_NAME'] = df['ACCESSION_NUMBER'].map(filer_names).fillna("MISSING")
    token = df.groupby(['symbol']).agg({'VALUE': 'sum'}).reset_index()
    token = token.sort_values('VALUE', ascending=False)
    st.write("Top Tickers")
    standard_AGgrid(token)
    st.write("Top Funds")
    token_ = df.groupby(['FILINGMANAGER_NAME']).agg({'VALUE': 'sum'}).reset_index()
    gridd = standard_AGgrid(token_, use_checkbox=True)

    alpaca_symbols_dict = return_Ticker_Universe().get('alpaca_symbols_dict')
    token['alpaca'] = token['symbol'].isin(list(alpaca_symbols_dict.keys()))
    st.write(len(token[token['alpaca']==True]))
    

    if st.button("Save Current Hudge Funds to DB"):
        hedge_funds = list(set(df['FILINGMANAGER_NAME'].tolist()))[:1000]
        for fund in tqdm(hedge_funds):
            token = df[df['FILINGMANAGER_NAME'] == fund]
            # accession_num = token.iloc[0]['ACCESSION_NUMBER']
            if len(token) > 0:
                # key = f'{accession_num}'
                # st.write(key, len(token))
                PollenDatabase.upsert_data('hedgefund_holdings', key=filer_names_[fund], value=token)


    filers_found = list(set(df['FILINGMANAGER_NAME'].tolist()))
    st.write("num of filers", len(filers_found))

    sample_filer = df[df['FILINGMANAGER_NAME'] == filers_found[88]]

    sample_filer['pct_allocation'] = sample_filer['VALUE'] / sample_filer['VALUE'].sum()
    st.write("filer 89", sample_filer)

    ACCESSION_NUMBER = df.iloc[223]['ACCESSION_NUMBER']
    data = PollenDatabase.retrieve_data('hedgefund_holdings', ACCESSION_NUMBER)
    # print("HF", data)




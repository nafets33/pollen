import streamlit as st
import pandas as pd
import os
from chess_piece.king import hive_master_root_db

local_db_root = hive_master_root_db()

@st.cache_data
def read_infotable():
    df = pd.read_csv(os.path.join(local_db_root, 'INFOTABLE.tsv'), sep='\t')
    return df

df = read_infotable()
cusip_mapping = pd.read_csv(os.path.join(local_db_root, 'cusip_tickers.csv'))
st.write(cusip_mapping.head())
cusip_mapping = dict(zip(cusip_mapping['CUSIP'], cusip_mapping['Ticker']))
df['symbol'] = df['CUSIP'].map(cusip_mapping).fillna("MISSING")
# df_return = pd.DataFrame()
# filers = set(df['NAMEOFISSUER'])
# for filer in tqdm(filers):
#     token = df[df['NAMEOFISSUER'] == filer]
#     if len(token) == 0:
#         print("NO DATA", filer)
#         continue
#     total_value = token['VALUE'].sum()
#     token['pct_allocation'] = token['VALUE'] / total_value
#     df_return = pd.concat([df_return, token])

df = df.dropna(subset=['NAMEOFISSUER'])
df['VALUE'] = pd.to_numeric(df['VALUE'], errors='coerce').fillna(0).astype(int)
df['pct_allocation'] = df.groupby('NAMEOFISSUER')['VALUE'].transform(lambda x: x / x.sum())

st.write(df.loc[:33])

# Ensure 'VALUE' is numeric
df = df.dropna(subset=['NAMEOFISSUER'])
df['VALUE'] = pd.to_numeric(df['VALUE'], errors='coerce').fillna(0).astype(int)

# Calculate the total VALUE for each group of NAMEOFISSUER, CUSIP, and INVESTMENTDISCRETION
df['total_value'] = df.groupby(['NAMEOFISSUER', 'CUSIP', 'INVESTMENTDISCRETION'])['VALUE'].transform('sum')

# Calculate the percentage allocation for each issuer
df['pct_allocation'] = (df['VALUE'] / df['total_value']) * 100

# Drop the total_value column as it's no longer needed
df.drop(columns=['total_value'], inplace=True)

st.write(df.loc[:33])

st.write(df['NAMEOFISSUER'].tolist()[:33])

df = df[df['NAMEOFISSUER'] == df['NAMEOFISSUER'].tolist()[23]]
st.write(df)



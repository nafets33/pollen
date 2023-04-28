import streamlit as st
from custom_grid import st_custom_grid, GridOptionsBuilder

def main():
  gb = GridOptionsBuilder.create()
  gb.configure_default_column(100)
  flash_def = {
    'pinned':'left',
    'cellRenderer': 'agAnimateShowChangeCellRenderer',
    'enableCellChangeFlash': True,
    }
  gb.configure_column('honey', flash_def)
  gb.configure_column('$honey',flash_def)
  gb.configure_column('symbol')
  gb.configure_column('ticker_time_frame')
  gb.configure_column('trigname')
  gb.configure_column('datetime')
  gb.configure_column('honey_time_in_profit')
  gb.configure_column('filled_qty')
  gb.configure_column('qty_available')
  gb.configure_column('filled_avg_price')
  go = gb.build()
  st_custom_grid(username='sven0227', 
                 api='http://127.0.0.1:8000/api/data/queen', 
                 refresh_sec= 2, 
                 refresh_cutoff_sec= 60, 
                 key = False,
                 api_url='http://127.0.0.1:8000/api/data/queen_app_Sellorder_request',
                 button_name='sell',
                 prod=False,
                 grid_options=go
                 )

if __name__ == '__main__':
  main()

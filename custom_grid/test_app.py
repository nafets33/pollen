import streamlit as st
from custom_grid import st_custom_grid, GridOptionsBuilder


def main():
    gb = GridOptionsBuilder.create()
    gb.configure_default_column(column_width=100, editable=True)
    flash_def = {
        'pinned': 'left',
        'cellRenderer': 'agAnimateShowChangeCellRenderer',
        'type':["numericColumn", "numberColumnFilter", "customCurrencyFormat"],
        'custom_currency_symbol':"%",
        'enableCellChangeFlash': True,
    }
    # Configure index field
    gb.configure_index('client_order_id')
    # gb.configure_column('a', {'pinned': 'left', 'headerName': 'cc',
    #                             'type':["numericColumn", "numberColumnFilter", "customCurrencyFormat"],
    #                             'custom_currency_symbol':"%"
    #                             })
    gb.configure_column('honey', flash_def)
    gb.configure_column('$honey', flash_def)
    gb.configure_column('symbol')
    gb.configure_column('ticker_time_frame')
    gb.configure_column('trigname')
    gb.configure_column('datetime',
                        {'type': ["dateColumnFilter", "customDateTimeFormat"],
                         "custom_format_string": "MM/dd/yy HH:mm"})
    gb.configure_column('honey_time_in_profit')
    gb.configure_column('filled_qty')
    gb.configure_column('qty_available')
    gb.configure_column('filled_avg_price')
    gb.configure_column('cost_basis')
    gb.configure_column('wave_amo', {'hide': True})

    go = gb.build()
    st_custom_grid(
        username="C:\sven\stefan\pollen\client_user_dbs\db__sven0227_82402505",
        api="http://127.0.0.1:8000/api/data/queen",
        api_update="http://127.0.0.1:8000/api/data/update_orders",
        refresh_sec=None,
        refresh_cutoff_sec=500,
        prod=False,
        key='maingrid',
        api_url='http://127.0.0.1:8000/api/data/queen_app_Sellorder_request',
        button_name="Sell",
        grid_options=go,
        # kwargs from here
        api_key="my_key",
        filter={"status": "running", "para1": "value1"},
        prompt_message ="Custom prompt message",
        prompt_field = "qty_available",
    )


if __name__ == '__main__':
    main()

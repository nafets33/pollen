import streamlit as st
from custom_grid import st_custom_grid, GridOptionsBuilder
from chess_piece.king import get_ip_address


def main():
    ip_address = get_ip_address()
    gb = GridOptionsBuilder.create()
    gb.configure_grid_options(
        pagination=True,
        enableRangeSelection=True,
        copyHeadersToClipboard=True,
        sideBar=False,
    )
    gb.configure_default_column(
        column_width=100,
        resizable=True,
        editable=True,
        textWrap=True,
        wrapHeaderText=True,
        autoHeaderHeight=True,
        autoHeight=True,
        suppress_menu=False,
        filterable=True,
    )
    flash_def = {
        # 'pinned': 'left',
        # 'cellRenderer': 'agAnimateShowChangeCellRenderer',
        # 'type': ["numericColumn", "numberColumnFilter", "customCurrencyFormat"],
        # 'custom_currency_symbol': "%",
        # 'enableCellChangeFlash': True,
    }
    # Configure index field
    gb.configure_index("client_order_id")
    # https://www.ag-grid.com/javascript-data-grid/themes/
    # ag-theme-alpine ag-theme-alpine-dark (default) ag-theme-balham ag-theme-balham-dark ag-theme-material
    gb.configure_theme("ag-theme-alpine")
    # gb.configure_column('a', {'pinned': 'left', 'headerName': 'cc',
    #                             'type':["numericColumn", "numberColumnFilter", "customCurrencyFormat"],
    #                             'custom_currency_symbol':"%"
    #                             })
    gb.configure_column("honey", flash_def)
    gb.configure_column("$honey", flash_def)
    gb.configure_column(
        "symbol",
        {
            "filter": True,
            "suppressMenu": False,
        },
    )
    gb.configure_column(
        "ticker_time_ frame",
        {
            "wrapText": True,
            "autoHeight": True,
            "wrapHeaderText": True,
            "autoHeaderHeight": True,
        },
    )
    gb.configure_column("trigname")
    gb.configure_column(
        "datetime",
        {
            "type": ["dateColumnFilter", "customDateTimeFormat"],
            "custom_format_string": "MM/dd/yy HH:mm",
        },
    )
    gb.configure_column("honey_time _in_profit")
    gb.configure_column("filled_qty")
    gb.configure_column("qty_available")
    gb.configure_column("filled_avg_price")
    # 123456 -> 123,456
    # gb.configure_column('cost_basis',
    #                     {"type": ["customNumberFormat"]})
    # hyperlink field
    gb.configure_column(
        field="cost_basis",
        header_name="hyperLink",
        other_column_properties={
            "type": ["customHyperlinkRenderer"],
            "baseURL": "http://pollenq.com",
            "linkField": "qty_available",
        },
    )
    gb.configure_column("wave_amo", {"hide": True})

    go = gb.build()
    st_custom_grid(
        username="F:/Work/2023-04/stefan/pollen/client_user_dbs/db__sven0227_82402505",
        api=f"http://{ip_address}:8000/api/data/queen",
        api_update="http://127.0.0.1:8000/api/data/update_orders",
        refresh_sec=5,
        refresh_cutoff_sec=500,
        prod=False,
        key="maingrid",
        grid_options=go,
        # kwargs from here
        api_key="my_key",
        filter={"status": "running", "para1": "value1"},
        buttons=[
            {
                "button_name": "button1",
                "button_api": "api1",
                "prompt_message": "message1",
                "prompt_field": None,
                "col_headername": "Buy button",
                "col_header": "symbol",
                "col_width": 100,
                "border_color": "green",
            },
            {
                "button_name": "button2",
                "button_api": f"http://{ip_address}:8000/api/data/queen_sell_orders",
                "prompt_message": "edit orders",
                "prompt_field": "origin_wave",
                "col_headername": "Sell button",
                "col_width": 100,
                "pinned": "left",
                "prompt_order_rules": [
                    "maxprofit",
                    "sell_out",
                    "take_profit",
                    "borrowed_funds",
                ],
                "border_color": "red",
            },
        ],
        grid_height="350px",
        toggle_views=["buys", "sells", "today", "closed"],
    )


if __name__ == "__main__":
    main()

# https://pablocfonseca-streamlit-aggrid-examples-example-jyosi3.streamlit.app/
from distutils import errors
from distutils.log import error
import streamlit as st
import pandas as pd 
import numpy as np
import altair as alt
from itertools import cycle

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode

np.random.seed(42)

@st.cache(allow_output_mutation=True)
def fetch_data(samples):
    deltas = cycle([
            pd.Timedelta(weeks=-2),
            pd.Timedelta(days=-1),
            pd.Timedelta(hours=-1),
            pd.Timedelta(0),
            pd.Timedelta(minutes=5),
            pd.Timedelta(seconds=10),
            pd.Timedelta(microseconds=50),
            pd.Timedelta(microseconds=10)
            ])
    dummy_data = {
        "date_time_naive":pd.date_range('2021-01-01', periods=samples),
        "apple":np.random.randint(0,100,samples) / 3.0,
        "banana":np.random.randint(0,100,samples) / 5.0,
        "chocolate":np.random.randint(0,100,samples),
        "group": np.random.choice(['A','B'], size=samples),
        "date_only":pd.date_range('2020-01-01', periods=samples).date,
        "timedelta":[next(deltas) for i in range(samples)],
        "date_tz_aware":pd.date_range('2022-01-01', periods=samples, tz="Asia/Katmandu")
    }
    return pd.DataFrame(dummy_data)

#Example controlers
st.sidebar.subheader("St-AgGrid example options")

sample_size = st.sidebar.number_input("rows", min_value=10, value=30)
grid_height = st.sidebar.number_input("Grid height", min_value=200, max_value=800, value=300)

return_mode = st.sidebar.selectbox("Return Mode", list(DataReturnMode.__members__), index=1)
return_mode_value = DataReturnMode.__members__[return_mode]

update_mode = st.sidebar.selectbox("Update Mode", list(GridUpdateMode.__members__), index=6)
update_mode_value = GridUpdateMode.__members__[update_mode]

#enterprise modules
enable_enterprise_modules = st.sidebar.checkbox("Enable Enterprise Modules")
if enable_enterprise_modules:
    enable_sidebar =st.sidebar.checkbox("Enable grid sidebar", value=False)
else:
    enable_sidebar = False

#features
fit_columns_on_grid_load = st.sidebar.checkbox("Fit Grid Columns on Load")

enable_selection=st.sidebar.checkbox("Enable row selection", value=True)
if enable_selection:
    st.sidebar.subheader("Selection options")
    selection_mode = st.sidebar.radio("Selection Mode", ['single','multiple'], index=1)
    
    use_checkbox = st.sidebar.checkbox("Use check box for selection", value=True)
    if use_checkbox:
        groupSelectsChildren = st.sidebar.checkbox("Group checkbox select children", value=True)
        groupSelectsFiltered = st.sidebar.checkbox("Group checkbox includes filtered", value=True)

    if ((selection_mode == 'multiple') & (not use_checkbox)):
        rowMultiSelectWithClick = st.sidebar.checkbox("Multiselect with click (instead of holding CTRL)", value=False)
        if not rowMultiSelectWithClick:
            suppressRowDeselection = st.sidebar.checkbox("Suppress deselection (while holding CTRL)", value=False)
        else:
            suppressRowDeselection=False
    st.sidebar.text("___")

enable_pagination = st.sidebar.checkbox("Enable pagination", value=False)
if enable_pagination:
    st.sidebar.subheader("Pagination options")
    paginationAutoSize = st.sidebar.checkbox("Auto pagination size", value=True)
    if not paginationAutoSize:
        paginationPageSize = st.sidebar.number_input("Page size", value=5, min_value=0, max_value=sample_size)
    st.sidebar.text("___")

df = fetch_data(sample_size)

#Infer basic colDefs from dataframe types
gb = GridOptionsBuilder.from_dataframe(df)

#customize gridOptions
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
gb.configure_column("date_only", type=["dateColumnFilter","customDateTimeFormat"], custom_format_string='yyyy-MM-dd', pivot=True)
gb.configure_column("date_tz_aware", type=["dateColumnFilter","customDateTimeFormat"], custom_format_string='yyyy-MM-dd HH:mm zzz', pivot=True)

gb.configure_column("apple", type=["numericColumn","numberColumnFilter","customNumericFormat"], precision=2, aggFunc='sum')
gb.configure_column("banana", type=["numericColumn", "numberColumnFilter", "customNumericFormat"], precision=1, aggFunc='avg')
gb.configure_column("chocolate", type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="R$", aggFunc='max')

#configures last row to use custom styles based on cell's value, injecting JsCode on components front end
cellsytle_jscode = JsCode("""
function(params) {
    if (params.value == 'A') {
        return {
            'color': 'white',
            'backgroundColor': 'darkred'
        }
    } else {
        return {
            'color': 'black',
            'backgroundColor': 'white'
        }
    }
};
""")
gb.configure_column("group", cellStyle=cellsytle_jscode)

if enable_sidebar:
    gb.configure_side_bar()

if enable_selection:
    gb.configure_selection(selection_mode)
    if use_checkbox:
        gb.configure_selection(selection_mode, use_checkbox=True, groupSelectsChildren=groupSelectsChildren, groupSelectsFiltered=groupSelectsFiltered)
    if ((selection_mode == 'multiple') & (not use_checkbox)):
        gb.configure_selection(selection_mode, use_checkbox=False, rowMultiSelectWithClick=rowMultiSelectWithClick, suppressRowDeselection=suppressRowDeselection)

if enable_pagination:
    if paginationAutoSize:
        gb.configure_pagination(paginationAutoPageSize=True)
    else:
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=paginationPageSize)

gb.configure_grid_options(domLayout='normal')
gridOptions = gb.build()

#Display the grid
st.header("Streamlit Ag-Grid")
st.markdown("""
    AgGrid can handle many types of columns and will try to render the most human readable way.  
    On editions, grid will fallback to string representation of data, DateTime and TimeDeltas are converted to ISO format.
    Custom display formating may be applied to numeric fields, but returned data will still be numeric.
""")

grid_response = AgGrid(
    df, 
    gridOptions=gridOptions,
    height=grid_height, 
    width='100%',
    data_return_mode=return_mode_value, 
    update_mode=update_mode_value,
    fit_columns_on_grid_load=fit_columns_on_grid_load,
    allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
    enable_enterprise_modules=enable_enterprise_modules
    )

df = grid_response['data']
selected = grid_response['selected_rows']
selected_df = pd.DataFrame(selected).apply(pd.to_numeric, errors='coerce')


with st.spinner("Displaying results..."):
    #displays the chart
    chart_data = df.loc[:,['apple','banana','chocolate']].assign(source='total')

    if not selected_df.empty :
        selected_data = selected_df.loc[:,['apple','banana','chocolate']].assign(source='selection')
        chart_data = pd.concat([chart_data, selected_data])

    chart_data = pd.melt(chart_data, id_vars=['source'], var_name="item", value_name="quantity")
    #st.dataframe(chart_data)
    chart = alt.Chart(data=chart_data).mark_bar().encode(
        x=alt.X("item:O"),
        y=alt.Y("sum(quantity):Q", stack=False),
        color=alt.Color('source:N', scale=alt.Scale(domain=['total','selection'])),
    )

    st.header("Component Outputs - Example chart")
    st.markdown("""
    This chart is built with data returned from the grid. rows that are selected are also identified.
    Experiment selecting rows, group and filtering and check how the chart updates to match.
    """)

    st.altair_chart(chart, use_container_width=True)

    st.subheader("Returned grid data:") 
    #returning as HTML table bc streamlit has issues when rendering dataframes with timedeltas:
    # https://github.com/streamlit/streamlit/issues/3781
    st.markdown(grid_response['data'].to_html(), unsafe_allow_html=True)

    st.subheader("grid selection:")
    st.write(grid_response['selected_rows'])

    st.header("Generated gridOptions")
    st.markdown("""
        All grid configuration is done thorugh a dictionary passed as ```gridOptions``` parameter to AgGrid call.
        You can build it yourself, or use ```gridOptionBuilder``` helper class.  
        Ag-Grid documentation can be read [here](https://www.ag-grid.com/documentation)
    """)
    st.write(gridOptions)





# def qrd_AGgrid(data, int_cols, reload_data=False, fit_columns_on_grid_load=False, height=750, update_mode_value='GRID_CHANGED', paginationOn=True, use_checkbox=True, oth_cols_hidden=False):
#     # ['NO_UPDATE', # 'MANUAL',# 'VALUE_CHANGED',    # 'SELECTION_CHANGED',# 'FILTERING_CHANGED',# 'SORTING_CHANGED',  # 'COLUMN_RESIZED',   # 'COLUMN_MOVED',     # 'COLUMN_PINNED',    # 'COLUMN_VISIBLE',   # 'MODEL_CHANGED',# 'COLUMN_CHANGED', # 'GRID_CHANGED']
#     gb = GridOptionsBuilder.from_dataframe(data, min_column_width=30)
#     if paginationOn:
#         gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
#     gb.configure_side_bar() #Add a sidebar
#     # if use_checkbox:
#     gb.configure_selection('multiple', use_checkbox=use_checkbox, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
    
#     cellsytle_jscode = JsCode("""
#     function(params) {
#         if (params.value == 'EXCEL') {
#             return {
#                 'color': 'white',
#                 'backgroundColor': 'lightblue'
#             }
#         } else {
#             return {
#                 'color': 'white',
#                 'backgroundColor': 'purple'
#             }
#         }
#     };
#     """)

#     test = JsCode("""
#     function(params) {
#         if (params.value > .1 || params.value < -.1)
#             return {
#                 'color': 'white',
#                 'backgroundColor': 'red'
#                 }
#         };
#     """)

#     rome_excel_link = """
#     function(params) {
#         if (params.value == 'ROME') {
#             return '<a href="https://' + params.data.full_IO_Num + "/summary" + '" target="_blank">'+ params.value+'</a>'
#             }
#         else {
#             return '<a href="https://' + params.data.IO_Num + '" target="_blank">'+ params.value+'</a>'
#         }
#         } """

#     excel_link = """
#     function(params) {
#             return '<a href="https:///' + params.data.IO_Num + '" target="_blank">'+ params.value+'</a>'
#             }"""

#     status_cellsytle_jscode = JsCode("""
#     function(params) {
#         if (params.value == 'ACTIVE') {
#             return {
#                 'color': 'black',
#                 'backgroundColor': 'lightgreen'
#             }
#         }
#         else if (params.value == 'NonRev_ACTIVE') {
#             return {
#                 'color': 'black',
#                 'backgroundColor': 'lightgreen'
#             }
#         }
#         else if (params.value == 'FINAL') {
#             return {
#                 'color': 'white',
#                 'backgroundColor': 'black'
#             }
#         }
#         else if (params.value == 'COMPLETED') {
#             return {
#                 'color': 'white',
#                 'backgroundColor': 'grey'
#             }
#         }
#     };
#     """)
    
#     ra_done_list = ['PreClose', 'Open Item', 'Ready Open Item', 'Ready', 'FINAL',  '' ]
#     rr_done_list = ['PreClose', 'Okay', 'Revisit', 'FINAL',  '' ]


#     gb.configure_column("13", header_name='System', pinned='left', cellStyle=cellsytle_jscode, cellRenderer=JsCode(rome_excel_link), maxWidth=100, autoSize=True)
#     gb.configure_column("IO_Num", pinned='left', cellRenderer=JsCode(excel_link), maxWidth=100, autoSize=True)
#     gb.configure_column("RR.Done", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': ra_done_list }, maxWidth=120, autoSize=True)
#     gb.configure_column("Review.Sign.Off", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': rr_done_list }, maxWidth=130, autoSize=True)
#     gb.configure_column('Status', cellStyle=status_cellsytle_jscode, pinned='left', maxWidth=100, autoSize=True)
#     gb.configure_column('IO.Comment', editable=True, maxWidth=1000, wrapText=True, autoHeight=True, resizable=True)
#     gb.configure_column('Resolution', header_name='Reviewer.Comment', editable=True, wrapText=True, autoHeight=True, resizable=True, maxWidth=1000,)
#     gb.configure_column('Open Cases', maxWidth=110, autoSize=True, wrapText=True, autoHeight=True, resizable=True)
#     gb.configure_column('RR.vs.SF', cellStyle=test, maxWidth=100, autoSize=True)
#     gb.configure_column("SF.Start.Date", type=["dateColumnFilter","customDateTimeFormat"], custom_format_string='MM-dd-yyyy', pivot=True, initialWidth=100, autoSize=True)
#     gb.configure_column("SF.End.Date", type=["dateColumnFilter","customDateTimeFormat"], custom_format_string='MM-dd-yyyy', pivot=True, initialWidth=100, autoSize=True)
#     gb.configure_column("RR.Start.Date", type=["dateColumnFilter","customDateTimeFormat"], custom_format_string='MM-dd-yyyy', pivot=True)
#     gb.configure_column("RR.End.Date", type=["dateColumnFilter","customDateTimeFormat"], custom_format_string='MM-dd-yyyy', pivot=True)
#     gb.configure_column("RA", maxWidth=110, autoSize=True)
#     gb.configure_column("AM", maxWidth=110, autoSize=True)
#     gb.configure_column("RR.Check", wrapText=True, resizable=True, maxWidth=200, autoSize=True, autoHeight=True)
#     gb.configure_column("Reviewer(s)", maxWidth=110, autoSize=True)
#     gb.configure_column("RR.Amount", wrapText=True, resizable=True, maxWidth=110, autoSize=True)
#     gb.configure_column("SF.Amount", wrapText=True, resizable=True, maxWidth=110, autoSize=True)
#     gb.configure_column("NetTerms", wrapText=True, resizable=True, maxWidth=80, autoSize=True)
#     gb.configure_column("NS_Cust.Num", wrapText=True, resizable=True, maxWidth=110, autoSize=True)
#     gb.configure_column("NS_Cust.Name", wrapText=True, resizable=True, maxWidth=110, autoSize=True)
#     gb.configure_column("SF.Billing.Cap", wrapText=True, resizable=True, maxWidth=100, autoSize=True, wrapHeaderText=True, initialWidth=80)
#     gb.configure_column("Unbilled", wrapText=True, resizable=True, maxWidth=110, autoSize=True, wrapHeaderText=True, initialWidth=80)
#     gb.configure_column("Deferred", wrapText=True, resizable=True, maxWidth=110, autoSize=True, wrapHeaderText=True, initialWidth=80)
#     gb.configure_column("Contract Assett", wrapText=True, resizable=True, maxWidth=110, autoSize=True, wrapHeaderText=True, initialWidth=80)
#     gb.configure_column("Contract Liability", wrapText=True, resizable=True, maxWidth=110, autoSize=True, wrapHeaderText=True, initialWidth=80)


#     if oth_cols_hidden:
#         for col in oth_cols_hidden:
#             gb.configure_column(col, hide=True)

#     k_sep_formatter = JsCode("""
#     function(params) {
#         return (params.value == null) ? params.value : params.value.toLocaleString('en-US',{style: "currency", currency: "USD"}); 
#     }
#     """)
#     gb.configure_columns(int_cols, valueFormatter=k_sep_formatter)
#     # for int_col in int_cols:
#     #     gb.configure_column(int_col, type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="$", aggFunc='max')

#     gridOptions = gb.build()
#     gridOptions['rememberGroupStateWhenNewData'] = 'true'
#     gridOptions['resizable'] = 'true'
#     gridOptions['wrapHeaderText'] = 'true'

#     grid_response = AgGrid(
#         data,
#         gridOptions=gridOptions,
#         data_return_mode='AS_INPUT', 
#         update_mode=update_mode_value, 
#         fit_columns_on_grid_load=fit_columns_on_grid_load,
#         enable_enterprise_modules=True,
#         height=height, 
#         reload_data=reload_data,
#         allow_unsafe_jscode=True,
#     )
#     return grid_response
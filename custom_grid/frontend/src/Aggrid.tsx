import React, { useState, useEffect, useMemo, useRef, useCallback, StrictMode } from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import 'ag-grid-enterprise';
import './styles.css';
import axios from "axios"
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib";
import {
  ColDef,
  ColGroupDef,
  ColumnResizedEvent,
  GetRowIdFunc,
  GetRowIdParams,
  Grid,
  GridOptions,
  GridReadyEvent,
  SideBarDef,
  ValueParserParams,
} from 'ag-grid-community';

type Props = {
  username: string,
  api: string,
  refresh_sec?: number,
  refresh_cutoff_sec?: number,
  gridoption_build?: any,
  prod?: boolean,
  api_url: string,
  button_name: string,
  grid_options?: GridOptions<any>,
  index: string,
}

let g_rowdata: any[] = [];

const AgGrid = (props: Props) => {

  const BtnCellRenderer = (props: any) => {
    const btnClickedHandler = () => {
      props.clicked(props.value);
    }

    return (
      <button onClick={btnClickedHandler}>{button_name}</button>
    )
  }

  const defaultColumnDefs: ColDef[] = [
    {
      field: 'honey',
      headerName: 'honey',
      filter: "agTextColumnFilter",
      pinned: 'left',
      cellRenderer: 'agAnimateShowChangeCellRenderer',
      enableCellChangeFlash: true,
    },
    {
      field: '$honey',
      headerName: '$honey',
      resizable: true,
      cellRenderer: 'agAnimateShowChangeCellRenderer',
      enableCellChangeFlash: true,
    },
    { field: 'symbol', headerName: 'Symbol', resizable: true },
    { field: 'ticker_time_frame', headerName: 'ticker_time_frame', resizable: true },
    { field: 'trigname', headerName: 'trigname', resizable: true },
    { field: 'datetime', headerName: 'datetime', resizable: true },
    { field: 'honey_time_in_profit', headerName: 'honey_time_in_profit', resizable: true },
    { field: 'filled_qty', headerName: 'filled_qty', resizable: true },
    { field: 'qty_available', headerName: 'qty_available', resizable: true },
    { field: 'filled_avg_price', headerName: 'filled_avg_price', resizable: true },
    { field: 'limit_price', headerName: 'limit_price', resizable: true },
    { field: 'cost_basis', headerName: 'cost_basis', resizable: true },
    { field: 'wave_amo', headerName: 'wave_amo', resizable: true },
    { field: 'status_q', headerName: 'status_q', resizable: true },
    { field: 'client_order_id', headerName: 'client_order_id', resizable: true },
    { field: 'origin_wave', headerName: 'origin_wave', resizable: true },
    { field: 'wave_at_creation', headerName: 'wave_at_creation', resizable: true },
    { field: 'sell_reason', headerName: 'sell_reason', resizable: true },
    { field: 'exit_order_link', headerName: 'exit_order_link', resizable: true },
    { field: 'queen_order_state', headerName: 'queen_order_state', resizable: true },
    { field: 'order_rules', headerName: 'order_rules', resizable: true },
    { field: 'order_rules.sellout', headerName: 'order_rules.sellout', width: 150, resizable: true },
    { field: 'order_trig_sell_stop', headerName: 'order_trig_sell_stop', resizable: true },
    { field: 'side', headerName: 'side', width: 70, pinned: 'right', resizable: true },
    {
      field: "client_order_id",
      headerName: 'action',
      width: 80,
      cellRenderer: BtnCellRenderer,
      cellRendererParams: {
        clicked: async function (field: any) {
          try {
            console.log('g_rowdata.find((row) => row.client_order_id == field).qty_available :>> ', g_rowdata.find((row) => row.client_order_id == field).qty_available);
            const num = prompt(`Please input number`, g_rowdata.find((row) => row.client_order_id == field).qty_available);
            console.log("prompt", num);
            if (num == null) return;
            const res = await axios.get(api_url, {
              params: {
                username: username,
                prod: prod,
                client_order_id: field,
                number_shares: num,
              }
            })
            alert("Success Sellorder_request!");
          } catch (error) {
            alert(`${error}`);
          }
        },
      },
      pinned: 'right',
    }
  ];

  const gridRef = useRef<AgGridReact>(null);
  const { username, api, refresh_sec = 1, refresh_cutoff_sec = 0, prod = true, api_url, button_name, grid_options = {}, index } = props;
  const [rowData, setRowData] = useState<any[]>([]);
  const [columnDefs, setColumnDefs] = useState<(ColDef | ColGroupDef)[]>(defaultColumnDefs)
  useEffect(() => {
    Streamlit.setFrameHeight()
    grid_options.columnDefs!.push({
      field: "client_order_id",
      headerName: 'action',
      width: 80,
      cellRenderer: BtnCellRenderer,
      cellRendererParams: {
        clicked: async function (field: any) {
          try {
            console.log('g_rowdata.find((row) => row.client_order_id == field).qty_available :>> ', g_rowdata.find((row) => row.client_order_id == field).qty_available);
            const num = prompt(`Please input number`, g_rowdata.find((row) => row.client_order_id == field).qty_available);
            console.log("prompt", num);
            if (num == null) return;
            const res = await axios.get(api_url, {
              params: {
                username: username,
                prod: prod,
                client_order_id: field,
                number_shares: num,
              }
            })
            alert("Success Sellorder_request!");
          } catch (error) {
            alert(`${error}`);
          }
        },
      },
      pinned: 'right',
    })
  });


  const addIds = (array: any[]) => {
    return array.map((item, idx) => {
      return { ...item, idx }
    })
  }

  const fetchAndSetData = async () => {
    const array = await fetchData();
    const api = gridRef.current!.api;
    const id_array = array.map((item: any) => item[index])
    const old_id_array = g_rowdata.map((item: any) => item[index])
    const toUpdate = g_rowdata.filter((row: any) => id_array.includes(row[index]))
    const toRemove = g_rowdata.filter((row) => !id_array.includes(row[index]))
    const toAdd = array.filter((row: any) => !old_id_array.includes(row[index]))
    api.applyTransactionAsync({ update: toUpdate, remove: toRemove, add: toAdd });
    g_rowdata = array
    console.log("index", index);
  };

  const fetchData = async () => {
    const res = await axios.get(api, {
      params: {
        username: username,
        prod: prod,
      }
    });
    const array = JSON.parse(res.data);
    return array;
  };

  const postRowId = async (id: any) => {
    const res = await axios.post(api, {
      username: username,
      prod: prod,
      id: id,
    });
    return res;
  };

  useEffect(() => {
    const interval = setInterval(fetchAndSetData, refresh_sec * 1000);
    let timeout: NodeJS.Timeout;
    if (refresh_cutoff_sec > 0) {
      console.log(refresh_cutoff_sec);
      timeout = setTimeout(() => {
        clearInterval(interval);
        console.log("Fetching data ended, refresh rate:", refresh_sec);
      }, refresh_cutoff_sec * 1000);
    }
    console.error("rendered==========", props);
    return () => {
      clearInterval(interval);
      if (timeout) clearTimeout(timeout);
    }
  }, [props]);

  const autoSizeAll = useCallback((skipHeader: boolean) => {
    const allColumnIds: string[] = [];
    gridRef.current!.columnApi.getColumns()!.forEach((column: any) => {
      allColumnIds.push(column.getId());
    });
    gridRef.current!.columnApi.autoSizeColumns(allColumnIds, skipHeader);
  }, []);

  const sizeToFit = useCallback(() => {
    gridRef.current!.api.sizeColumnsToFit({
      defaultMinWidth: 100,
    });
  }, []);

  const onGridReady = useCallback(async (params: GridReadyEvent) => {
    setTimeout(async () => {
      const array = await fetchData();
      setRowData(array);
      g_rowdata = array;
    }, 100);
  }, []);

  const autoGroupColumnDef = useMemo<ColDef>(() => {
    return {
      minWidth: 200,
    };
  }, []);

  const getRowId = useMemo<GetRowIdFunc>(() => {
    return (params: GetRowIdParams) => {
      return params.data[index];
    };
  }, [index]);

  const sideBar = useMemo<
    SideBarDef | string | string[] | boolean | null
  >(() => {
    return {
      toolPanels: [
        {
          id: 'columns',
          labelDefault: 'Columns',
          labelKey: 'columns',
          iconKey: 'columns',
          toolPanel: 'agColumnsToolPanel',
        },
        {
          id: 'filters',
          labelDefault: 'Filters',
          labelKey: 'filters',
          iconKey: 'filter',
          toolPanel: 'agFiltersToolPanel',
        },
      ],
      defaultToolPanel: 'customStats',
    };
  }, []);
  return (
    <div style={{ display: 'flex', flexDirection: 'row', height: '300px', width: "100" }} id='myGrid'>
      <div className="ag-theme-alpine-dark" style={{ width: "100%", height: "100%" }}>
        <AgGridReact
          ref={gridRef}
          rowData={rowData}
          // columnDefs={columnDefs}
          // defaultColDef={defaultColDef}
          rowStyle={{ fontSize: 12, padding: 0 }}
          headerHeight={30}
          rowHeight={30}
          onGridReady={onGridReady}
          autoGroupColumnDef={autoGroupColumnDef}
          sideBar={sideBar}
          animateRows={true}
          suppressAggFuncInHeader={true}
          getRowId={getRowId}
          gridOptions={grid_options}
        />
      </div>
    </div>
  );
};

export default AgGrid;

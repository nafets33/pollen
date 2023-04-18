import React, { useState, useEffect, useMemo, useRef, useCallback, StrictMode } from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import './styles.css';
import axios from "axios"
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib";
import { IOlympicData } from './interfaces';
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
}

const BtnCellRenderer = (props: any) => {
  const btnClickedHandler = () => {
    props.clicked(props.value);
  }

  return (
    <button onClick={btnClickedHandler}>Sell</button>
  )
}

const defaultWidth = 100;



let g_rowdata: any[] = [];

const AgGrid = (props: Props) => {
  const defaultColumnDefs: ColDef[] = [
    { field: "idx", pinned: "left", width: 60 },
    { field: 'honey', headerName: 'honey', width: defaultWidth, pinned: 'left', cellRenderer: 'agAnimateShowChangeCellRenderer', aggFunc: "sum" },
    { field: '$honey', headerName: '$honey', width: defaultWidth, resizable: true },
    { field: 'symbol', headerName: 'Symbol', width: defaultWidth, resizable: true },
    { field: 'ticker_time_frame', headerName: 'ticker_time_frame', width: defaultWidth, resizable: true },
    { field: 'trigname', headerName: 'trigname', width: defaultWidth, resizable: true },
    { field: 'datetime', headerName: 'datetime', width: defaultWidth, resizable: true },
    { field: 'honey_time_in_profit', headerName: 'honey_time_in_profit', width: defaultWidth, resizable: true },
    { field: 'filled_qty', headerName: 'filled_qty', width: defaultWidth, resizable: true },
    { field: 'qty_available', headerName: 'qty_available', width: defaultWidth, resizable: true },
    { field: 'filled_avg_price', headerName: 'filled_avg_price', width: defaultWidth, resizable: true },
    { field: 'limit_price', headerName: 'limit_price', width: defaultWidth, resizable: true },
    { field: 'cost_basis', headerName: 'cost_basis', width: defaultWidth, resizable: true },
    { field: 'wave_amo', headerName: 'wave_amo', width: defaultWidth, resizable: true },
    { field: 'status_q', headerName: 'status_q', width: defaultWidth, resizable: true },
    { field: 'client_order_id', headerName: 'client_order_id', width: defaultWidth, resizable: true },
    { field: 'origin_wave', headerName: 'origin_wave', width: defaultWidth, resizable: true },
    { field: 'wave_at_creation', headerName: 'wave_at_creation', width: defaultWidth, resizable: true },
    { field: 'sell_reason', headerName: 'sell_reason', width: defaultWidth, resizable: true },
    { field: 'exit_order_link', headerName: 'exit_order_link', width: defaultWidth, resizable: true },
    { field: 'queen_order_state', headerName: 'queen_order_state', width: defaultWidth, resizable: true },
    { field: 'order_rules', headerName: 'order_rules', width: defaultWidth, resizable: true },
    { field: 'order_rules.sellout', headerName: 'order_rules.sellout', width: 150, resizable: true },
    { field: 'order_trig_sell_stop', headerName: 'order_trig_sell_stop', width: defaultWidth, resizable: true },
    { field: 'side', headerName: 'side', width: 70, pinned: 'right', resizable: true },
    {
      field: "client_order_id",
      headerName: 'action',
      width: 80,
      cellRenderer: BtnCellRenderer,
      cellRendererParams: {
        clicked: async function (field: any) {
          try {
            const res: any = await postRowId(field)
            alert(`id : ${field}, result: ${res.data}`);

          } catch (error) {
            alert("failed!");

          }
        },
      },
      pinned: 'right',
    }
  ];
  const gridRef = useRef<any>();
  const { username, api, refresh_sec = 1, refresh_cutoff_sec = 0, prod = true } = props;
  const [rowData, setRowData] = useState<any[]>([]);
  const [columnDefs, setColumnDefs] = useState<(ColDef | ColGroupDef)[]>(defaultColumnDefs)
  useEffect(() => Streamlit.setFrameHeight());

  const addIds = (array: any[]) => {
    return array.map((item, idx) => {
      return { ...item, idx }
    })
  }

  const fetchAndSetData = async () => {
    const array = await fetchData();
    const idAdded = addIds(array);
    gridRef.current!.api.setRowData(idAdded);
  };

  const fetchData = async () => {
    const res = await axios.get(api, {
      params: {
        username: username,
        prod: prod,
      }
    });
    const array = JSON.parse(res.data);
    const idAdded = addIds(array)
    g_rowdata = idAdded;
    return idAdded;
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
    gridRef.current.api.sizeColumnsToFit({
      defaultMinWidth: 100,
    });
  }, []);

  const onGridReady = useCallback(async (params: GridReadyEvent) => {
    setTimeout(async () => {
      const data = await fetchData();
      setRowData(data);
    }, 100);
  }, []);

  const autoGroupColumnDef = useMemo<ColDef>(() => {
    return {
      minWidth: 200,
    };
  }, []);

  const defaultColDef = useMemo<ColDef>(() => {
    return {
      width: 120,
      sortable: true,
      resizable: true,
    };
  }, []);

  const getRowId = useMemo<GetRowIdFunc>(() => {
    return (params: GetRowIdParams<any>) => params.data.id;
  }, []);

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
    <div
      className="ag-theme-alpine-dark"
    >
      <AgGridReact
        ref={gridRef}
        rowData={rowData}
        columnDefs={columnDefs}
        defaultColDef={defaultColDef}
        rowStyle={{ fontSize: 12, padding: 0 }}
        headerHeight={30}
        rowHeight={30}
        domLayout={"autoHeight"}
        onGridReady={onGridReady}
        autoGroupColumnDef={autoGroupColumnDef}
        sideBar={sideBar}
        enableCellChangeFlash={true}
        animateRows={true}
        suppressAggFuncInHeader={true}
      // getRowId={getRowId}
      />
    </div>
  );
};

export default AgGrid;

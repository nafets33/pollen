import React, {
  useState,
  useEffect,
  useMemo,
  useRef,
  useCallback
} from "react"
import { AgGridReact } from "ag-grid-react"
import { RowClassParams } from 'ag-grid-community';

import toastr from "toastr"
import "toastr/build/toastr.min.css"
import "ag-grid-community/styles/ag-grid.css"
import "ag-grid-community/styles/ag-theme-alpine.css"
import "ag-grid-community/styles/ag-theme-balham.css"
import "ag-grid-community/styles/ag-theme-material.css"
import MyModal from './components/Modal'
import "ag-grid-enterprise"
import { parseISO, compareAsc, set, sub } from "date-fns"
import { format } from "date-fns-tz"
import { duration } from "moment"
import "./styles.css"
import axios from "axios"
// import { io } from "socket.io-client";

import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib"
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
} from "ag-grid-community"
import {deepMap} from "./utils"


type Props = {
  username: string
  api: string
  api_update: string
  refresh_sec?: number
  refresh_cutoff_sec?: number
  gridoption_build?: any
  prod?: boolean
  grid_options?: any
  index: string
  enable_JsCode: boolean
  kwargs: any
}

let g_rowdata: any[] = []
let g_newRowData: any = null

function dateFormatter(isoString: string, formaterString: string): String {
  try {
    let date = new Date(isoString)
    return format(date, formaterString)
  } catch {
    return isoString
  } finally {
  }
}

function currencyFormatter(number: any, currencySymbol: string): String {
  let n = Number.parseFloat(number)
  if (!Number.isNaN(n)) {
    return currencySymbol + n.toFixed(2)
  } else {
    return number
  }
}

function numberFormatter(number: any, precision: number): String {
  let n = Number.parseFloat(number)
  if (!Number.isNaN(n)) {
    return n.toFixed(precision)
  } else {
    return number
  }
}

const columnFormaters = {
  columnTypes: {
    dateColumnFilter: {
      filter: "agDateColumnFilter",
      filterParams: {
        comparator: (filterValue: any, cellValue: string) =>
          compareAsc(parseISO(cellValue), filterValue),
      },
    },
    numberColumnFilter: {
      filter: "agNumberColumnFilter",
    },
    shortDateTimeFormat: {
      valueFormatter: (params: any) =>
        dateFormatter(params.value, "dd/MM/yyyy HH:mm"),
    },
    customDateTimeFormat: {
      valueFormatter: (params: any) =>
        dateFormatter(params.value, params.column.colDef.custom_format_string),
    },
    customNumericFormat: {
      valueFormatter: (params: any) =>
        numberFormatter(params.value, params.column.colDef.precision ?? 2),
    },
    customCurrencyFormat: {
      valueFormatter: (params: any) =>
        currencyFormatter(
          params.value,
          params.column.colDef.custom_currency_symbol
        ),
    },
    timedeltaFormat: {
      valueFormatter: (params: any) => duration(params.value).humanize(true),
    },
  },
}

const HyperlinkRenderer = (props: any) => {
  return (
    <a
      href={`${props.column.colDef.baseURL}/${
        props.data[props.column.colDef["linkField"]]
      }`}
      target="_blank"
    >
      {props.value}
    </a>
  )
}

toastr.options = {
  positionClass: "toast-top-full-width",
  hideDuration: 300,
  timeOut: 3000,
}

const AgGrid = (props: Props) => {
  const BtnCellRenderer = (props: any) => {
    const btnClickedHandler = () => {
      props.clicked(props.node.id)
    }
    // console.log("props.cellStyle", props.cellStyle)
    return (
      <button
        onClick={btnClickedHandler}
        style={{
          background: "transparent",
          border: (props.cellStyle && props.cellStyle.border !== undefined)
            ? props.cellStyle.border
            : "none",          
          width: props.width ? props.width : "100%",
              ...(props.cellStyle || {}), // <-- Merge in cellStyle from params ? NOT WORKING?
        }}
      >
        {props.col_header ? props.value : props.buttonName}
      </button>
    )
  }

  const gridRef = useRef<AgGridReact>(null)
  const {
    username,
    api,
    api_update,
    refresh_sec = undefined,
    refresh_cutoff_sec = 0,
    prod = true,
    index,
    enable_JsCode,
    kwargs,
  } = props
  let { grid_options = {} } = props

  //parsing must be done here. For some unknow reason if its moved after the
  //button mapping, deepMap gets lots of React objects (api, symbolRefs, etc.)
  //this impacts performance and crashes the grid.
  if (enable_JsCode) {
    grid_options = deepMap(grid_options, parseJsCodeFromPython, ["rowData"])
  }

  const [subtotalsRow, setSubtotalsRow] = useState<any[]>([]);
  let { buttons, toggle_views, api_key, api_lastmod_key = null, columnOrder=[], 
    refresh_success=null, total_col=false, subtotal_cols=[], filter_button=''} = kwargs
  const [rowData, setRowData] = useState<any[]>([])
  const [modalShow, setModalshow] = useState(false)
  const [modalData, setModalData] = useState({})
  const [promptText, setPromptText] = useState("")
  const [viewId, setViewId] = useState(0)
  const [lastModified, setLastModified] = useState<string | null>(null);
  const [previousViewId, setpreviousViewId] = useState(89)
  const [activeFilter, setActiveFilter] = useState<string | null>(null);

  const checkLastModified = async (): Promise<boolean> => {
    try {
      if (api_lastmod_key === null) {
        console.log("api key is null, returning false");
        return true;
      }
      if (api_lastmod_key !== null && api_lastmod_key !== undefined) {
        const baseurl = api.split('/').slice(0, -1).join('/');
        const res = await axios.get(`${baseurl}/lastmod_key`, {
          params: {
            api_key: api_key,
            client_user: username,
            prod: prod,
            api_lastmod_key: api_lastmod_key,
          },
        });
        // console.log("fetching data...", res.data.lastModified);
        if (res.data?.lastModified !== lastModified) {
          // console.log("setting modified changed, fetching data...", res.data.lastModified, lastModified);
          setLastModified(res.data.lastModified);
          return true;
        } else {
          return false;
        }
      }
      return false;
    } catch (error: any) {
      toastr.error(`Failed to check last modified: ${error.message}`);
      return false;
    }
  };

  const checkViewIdChanged = async (currentViewId: number, previousViewId: number): Promise<boolean> => {
    if (currentViewId !== previousViewId) {
      // console.log("viewId has changed from", previousViewId, "to", currentViewId);
      setpreviousViewId(currentViewId);
      return true;
    } else {
      // console.log("viewId has not changed");
      return false;
    }
  };

  useEffect(() => {
    Streamlit.setFrameHeight();
  
    if (buttons.length) {
      buttons = deepMap(buttons, parseJsCodeFromPython, ["rowData"]); // process JsCode from buttons props
  
      buttons.forEach((button: any) => {
        const {
          prompt_field,
          prompt_message,
          button_api,
          prompt_order_rules,
          col_header,
          col_headername,
          col_width,
          pinned,
          button_name,
          border_color,
          border,
          add_symbol_row_info,
          display_grid_column,
          editableCols,
          ...otherKeys
        } = button;

        let filterParams = button.filterParams || {};
        if (kwargs['filter_apply']) {
          filterParams = { ...filterParams, buttons: ['apply', 'reset'] };
        }

        grid_options.columnDefs!.push({
          ...otherKeys,
          field: col_header || index,
          headerName: col_headername,
          width: col_width,
          pinned: pinned,
          cellRenderer: BtnCellRenderer,
          filterParams,
          cellRendererParams: {
            col_header,
            buttonName: button_name,
            borderColor: border_color,
            border: border,
            filterParams,
            cellStyle: button.cellStyle,
            ...(button.cellRendererParams || {}),
            clicked: async function (row_index: any) {
              try {
                const selectedRow = g_rowdata.find((row) => row[index] === row_index);
                if (prompt_order_rules) {
                  const str = selectedRow[prompt_field];
                  const selectedField =
                    typeof str === "string"
                      ? JSON.parse(
                          selectedRow[prompt_field]
                            .replace(/'/g, '"')
                            .replace(/\n/g, "")
                            .replace(/\s/g, "")
                            .replace(/False/g, "false")
                            .replace(/True/g, "true")
                        )
                      : str;
  
                  setModalshow(true);
                  setModalData({
                    prompt_message,
                    button_api: button_api,
                    username: username,
                    prod: prod,
                    selectedRow: selectedRow,
                    kwargs: kwargs,
                    prompt_field,
                    prompt_order_rules,
                    selectedField,
                    add_symbol_row_info,
                    display_grid_column,
                    editableCols,
                  });
  
                  const rules_value: any = {};
                  prompt_order_rules.forEach((rule: string) => {
                    rules_value[rule] = selectedField[rule];
                  });
  
                  setPromptText(rules_value);
                } else if (prompt_field && prompt_message) {
                  setModalshow(true);
                  setModalData({
                    prompt_message,
                    button_api: button_api,
                    username: username,
                    prod: prod,
                    selectedRow: selectedRow,
                    kwargs: kwargs,
                  });
                  setPromptText(selectedRow[prompt_field]);
                } else {
                  if (window.confirm(prompt_message)) {
                    await axios.post(button_api, {
                      username: username,
                      prod: prod,
                      selected_row: selectedRow,
                      ...kwargs,
                    });
                  }
                  toastr.success("Success!");
                }
              } catch (error) {
                alert(`${error}`);
              }
            },
          },
        });
      });
    }
  
    // Reorder columns based on a predefined list
    // const columnOrder = ["sector", "broker_qty_available", "queens_suggested_sell"]; // Replace with your desired column order
    
    if (columnOrder.length > 0 && grid_options.columnDefs) {
      grid_options.columnDefs.sort((a: any, b: any) => {
      // If both columns are in the columnOrder array, maintain their order
      if (columnOrder.indexOf(a.field) !== -1 && columnOrder.indexOf(b.field) !== -1) {
        return columnOrder.indexOf(a.field) - columnOrder.indexOf(b.field);
      }
    
      // If one of the columns isn't in columnOrder, keep its original position
      if (columnOrder.indexOf(a.field) === -1) return 1;
      if (columnOrder.indexOf(b.field) === -1) return -1;
    
      return 0;
      });
    }
    
  
    // Optional: Refresh header if necessary (if needed)
    if (gridRef.current?.api) {
      gridRef.current.api.refreshHeader();
    }
  }, [buttons, grid_options.columnDefs]);

  const fetchAndSetData = async () => {
    const array = await fetchData();
    if (array === false) return false;
    setRowData(array);
    g_rowdata = array;
    return true;
  };

  useEffect(() => {
    onRefresh()
  }, [viewId])


  const fetchData = async () => {
    try {
      let toggle_view = toggle_views ? toggle_views[viewId] : "none";
      const hasViewChanged = await checkViewIdChanged(viewId, previousViewId);
      // console.log("hasViewChanged", hasViewChanged, viewId, previousViewId);

      // If view has changed, skip checkLastModified
      if (!hasViewChanged && refresh_sec && refresh_sec > 0) {
        const isLastModified = await checkLastModified();
        // console.log("isLastModified", isLastModified, api);
        if (!isLastModified) {
          return false;
        }
      }

      console.log("fetching data...", api);
      const res = await axios.post(api, {
        username: username,
        prod: prod,
        ...kwargs,
        toggle_view_selection: toggle_view
      });
      const array = JSON.parse(res.data);


      return array;
    }
    catch (error: any) {
      toastr.error(`Fetch Error: ${error.message}`);
      return false;
    }
  };

 /// for title outside grid
// const [subtotals, setSubtotals] = useState<any>(null);

// const calculateSubtotals = useCallback(() => {
//   if (!gridRef.current) return;
//   if (!subtotal_cols || subtotal_cols.length === 0) {
//     setSubtotals(null);
//     return;
//   }
//   const api = gridRef.current.api;
//   let filteredRows: any[] = [];
//   api.forEachNodeAfterFilterAndSort((node) => {
//     if (node.data) filteredRows.push(node.data);
//   });

//   if (filteredRows.length === 0) {
//     setSubtotals(null);
//     return;
//   }

//   let subtotal: any = {};
//   subtotal[total_col] = "Subtotal";
//   subtotal_cols.forEach((col: string) => {
//     subtotal[col] = filteredRows.reduce((sum, row) => sum + (Number(row[col]) || 0), 0);
//   });

//   setSubtotals(subtotal);
// }, [subtotal_cols, total_col]);
// const onFilterChanged = useCallback(() => {
//   calculateSubtotals();
// }, [calculateSubtotals]);

// const [subtotalsRow, setSubtotalsRow] = useState<any[]>([]);

const calculateSubtotals = useCallback(() => {
  if (!gridRef.current) return;
  if (!subtotal_cols || subtotal_cols.length === 0) {
    setSubtotalsRow([]);
    return;
  }
  const api = gridRef.current.api;
  let filteredRows: any[] = [];
  api.forEachNodeAfterFilterAndSort((node) => {
    if (node.data) filteredRows.push(node.data);
  });

  if (filteredRows.length === 0) {
    setSubtotalsRow([]);
    return;
  }

let subtotal: any = {};
// Ensure total_col is a valid string and exists in the columns
let allCols: string[] = [];
if (grid_options && grid_options.columnDefs) {
  allCols = grid_options.columnDefs.map((colDef: any) => colDef.field).filter(Boolean);
} else if (filteredRows.length > 0) {
  allCols = Object.keys(filteredRows[0]);
}

// Place "subTotals" label in the correct column
if (typeof total_col === "string" && allCols.includes(total_col)) {
  subtotal[total_col] = "subTotals";
} else if (allCols.length > 0) {
  subtotal[allCols[0]] = "subTotals"; // fallback to first column
}

allCols.forEach((col: string) => {
  if (subtotal_cols.includes(col)) {
    const sum = filteredRows.reduce((sum, row) => sum + (Number(row[col]) || 0), 0);
    subtotal[col] = isNaN(sum) ? "" : sum;
  } else if (subtotal[total_col] !== "subTotals" || col !== total_col) {
    subtotal[col] = ""; // or null, or a placeholder
  }
});

  setSubtotalsRow([subtotal]);
}, [subtotal_cols, total_col]);
const onFilterChanged = useCallback(() => {
  calculateSubtotals();
}, [calculateSubtotals]);

  useEffect(() => {
    if (refresh_sec && refresh_sec > 0) {
      const interval = setInterval(fetchAndSetData, refresh_sec * 1000)
      let timeout: NodeJS.Timeout
      if (refresh_cutoff_sec > 0) {
        console.log(refresh_cutoff_sec)
        timeout = setTimeout(() => {
          clearInterval(interval)
          console.log("Fetching data ended, refresh rate:", refresh_sec)
        }, refresh_cutoff_sec * 1000)
      }
      console.error("rendered==========", props)
      return () => {
        clearInterval(interval)
        if (timeout) clearTimeout(timeout)
      }
    }
  }, [props, viewId])

  // useEffect(() => {
  //   const baseurl = api.split('/').slice(0, -1).join('/');
  //   const socket = io(`${baseurl}/ws`);

  //   socket.on("dataUpdated", () => {
  //     console.log("Data update received via WebSocket");
  //     onRefresh();
  //   });

  //   return () => {
  //     socket.disconnect();
  //   };
  // }, []);


  const autoSizeAll = useCallback((skipHeader: boolean) => {
    const allColumnIds: string[] = []
    gridRef.current!.columnApi.getColumns()!.forEach((column: any) => {
      allColumnIds.push(column.getId())
    })
    gridRef.current!.columnApi.autoSizeColumns(allColumnIds, skipHeader)
  }, [])

  const sizeToFit = useCallback(() => {
    gridRef.current!.api.sizeColumnsToFit({
      defaultMinWidth: 100,
    })
  }, [])

  const onGridReady = useCallback(async (params: GridReadyEvent) => {
    setTimeout(async () => {
      try {
        const array = await fetchData()
        // console.log("AAAAAAAAAAAAAAAAAAAAAAA", array)
        if (array === false) {
          // toastr.error(`Error: ${array.message}`)
          return
        }
        setRowData(array)
        g_rowdata = array
      
      if (subtotal_cols && subtotal_cols.length > 0) {
        calculateSubtotals();
      } else {
        setSubtotalsRow([]);
      }

      } catch (error: any) {
        toastr.error(`Error: ${error.message}`)
      }
    }, 100)
  }, [])

  const autoGroupColumnDef = useMemo<ColDef>(() => {
    return {
      minWidth: 200,
    }
  }, [])

  const getRowId = useMemo<GetRowIdFunc>(() => {
    return (params: GetRowIdParams) => {
      return params.data[index]
    }
  }, [index])

  const sideBar = useMemo<
    SideBarDef | string | string[] | boolean | null
  >(() => {
    return {
      toolPanels: [
        {
          id: "columns",
          labelDefault: "Columns",
          labelKey: "columns",
          iconKey: "columns",
          toolPanel: "agColumnsToolPanel",
        },
        {
          id: "filters",
          labelDefault: "Filters",
          labelKey: "filters",
          iconKey: "filter",
          toolPanel: "agFiltersToolPanel",
        },
      ],
      defaultToolPanel: "customStats",
    }
  }, [])

  const onCellValueChanged = useCallback((event) => {
    if (g_newRowData === null) g_newRowData = {}
    g_newRowData[event.data[index]] = event.data
    console.log("Data after change is", g_newRowData)
  }, [])


  const [loading, setLoading] = useState(false);
  const subtotalTimeout = useRef<NodeJS.Timeout | null>(null);

  const onRefresh = async () => {
    setLoading(true);
    try {
      const success = await fetchAndSetData();
      
      refresh_success && success && toastr.success("Refresh success!");
    } catch (error: any) {
      toastr.error(`Refresh Failed! ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const onUpdate = async () => {
    if (g_newRowData === null) {
      toastr.warning(`No changes to update`)
      return
    }
    try {
      const res: any = await axios.post(api_update, {
        username: username,
        prod: prod,
        new_data: g_newRowData,
        ...kwargs,
      })
      g_newRowData = null
      if (res.status) toastr.success(`Successfully Updated! `)
      else toastr.error(`Failed! ${res.message}`)
    } catch (error) {
      toastr.error(`Failed! ${error}`)
    }
  }

  const columnTypes = useMemo<any>(() => {
    return {
      dateColumnFilter: {
        filter: "agDateColumnFilter",
        filterParams: {
          comparator: (filterValue: any, cellValue: string) =>
            compareAsc(new Date(cellValue), filterValue),
        },
      },
      numberColumnFilter: {
        filter: "agNumberColumnFilter",
      },
      shortDateTimeFormat: {
        valueFormatter: (params: any) =>
          dateFormatter(params.value, "dd/MM/yyyy HH:mm"),
      },
      customDateTimeFormat: {
        valueFormatter: (params: any) =>
          dateFormatter(
            params.value,
            params.column.colDef.custom_format_string
          ),
      },
      customNumericFormat: {
        valueFormatter: (params: any) =>
          numberFormatter(params.value, params.column.colDef.precision ?? 2),
      },
      customCurrencyFormat: {
        valueFormatter: (params: any) =>
          currencyFormatter(
            params.value,
            params.column.colDef.custom_currency_symbol
          ),
      },
      timedeltaFormat: {
        valueFormatter: (params: any) => duration(params.value).humanize(true),
      },
      customNumberFormat: {
        valueFormatter: (params: any) =>
          Number(params.value).toLocaleString("en-US", {
            minimumFractionDigits: 0,
          }),
      },
      customHyperlinkRenderer: {
        // valueGetter: (params: any) =>
        //   params.column.colDef.baseURL + params.data.honey,
        cellRenderer: HyperlinkRenderer,
        cellRendererParams: {
          baseURL: "URLSearchParams.co",
        },
      },
    }
  }, [])

  const onClick = () => {
    toastr.clear()
    setTimeout(() => toastr.success(`Settings updated `), 300)
  }

  type RowStyle = {
    background?: string;
    color?: string;
    fontWeight?: string;
  };

  function parseJsCodeFromPython(v: string) {
    const JS_PLACEHOLDER = "::JSCODE::"
    let funcReg = new RegExp(
      `${JS_PLACEHOLDER}\\s*((function|class)\\s*.*)\\s*${JS_PLACEHOLDER}`
    )
  
    let match = funcReg.exec(v)
  
    if (match) {
  
      const funcStr = match[1]
      // eslint-disable-next-line
      return new Function("return " + funcStr)()
    } else {
      return v
    }
  }

  const getRowStyle = (params: RowClassParams<any>): RowStyle | undefined => {
        if (params.data && params.data[total_col] === "subTotals") {
      return { fontWeight: "bold", background: "#f8f8f8" }; // Add background if you want
    }
    try {
      const background = params.data["color_row"] ?? undefined;
      const color = params.data["color_row_text"] ?? undefined;
      return { background, color };
    } catch (error) {
      console.error("Error accessing row style:", error);
      return undefined; // Return undefined when an error occurs
    }
  };

  // interface Props {
  //   toggle_views: string[];
  //   viewId: number;
  //   setViewId: (id: number) => void;
  //   loading: boolean;
  //   onUpdate: () => void;
  // }
  const getButtonStyle = (length: number) => {
    if (length < 3) {
      return { padding: "15px 18px", fontSize: "18px" };
    } else if (length < 8) {
      return { padding: "15px 18px", fontSize: "15px" };
    } else if (length < 15) {
      return { padding: "12px 13px", fontSize: "13px" };
    } else if (length < 35) {
      return { padding: "10px 12px", fontSize: "11px" };
    } else {
      return { padding: "3px 5px", fontSize: "10px" };
    }
  };

  const buttonStyle = getButtonStyle(toggle_views.length);

  const button_color = "#3498db"; // Set your custom button color here

  // let pinnedTopRowData: any[] = [];
  // let filteredRowData = rowData;
  
  // console.log("total_col", total_col)
  // if (total_col) {
  //   // Use total_col as the column to check for "Total" row
  //   const totalRow = rowData.find(row => row[total_col] === "Total");
  //   pinnedTopRowData = totalRow ? [totalRow] : [];
  //   filteredRowData = rowData.filter(row => row[total_col] !== "Total");
  // }


  const getUniqueColumnValues = (column: string, rowData: any[]) => {
    return Array.from(new Set(rowData.map(row => row[column]))).filter(
      v => v !== undefined && v !== null
    );
  };
// let filter_button = "piece_name";

const uniqueValues = useMemo(
  () => getUniqueColumnValues(filter_button, rowData),
  [rowData, filter_button]
);

const handleButtonFilter = (value: string | null) => {
  setActiveFilter(value);

  if (gridRef.current && gridRef.current.api) {
    const api = gridRef.current.api;
    if (value) {
      api.setFilterModel({
        ...api.getFilterModel(),
        [filter_button]: { filterType: "set", values: [value] }
      });
    } else {
      const model = api.getFilterModel();
      delete model[filter_button];
      api.setFilterModel(model);
    }
  }
};

  return (
    <>
      <MyModal
        isOpen={modalShow}
        closeModal={() => setModalshow(false)}
        modalData={modalData}
        promptText={promptText}
        setPromptText={setPromptText}
        toastr={toastr}
      />
      <div
        style={{ flexDirection: "row", height: "100%", width: "100%" }}
        id="myGrid"
      >
        <div className="d-flex justify-content-between align-items-center">
          {(refresh_sec == undefined || refresh_sec == 0) && (
            <div style={{ display: "flex" }}>
              <div style={{ margin: "5px 5px 5px 2px" }}>
                <button
                  className="btn"
                  style={{
                    backgroundColor: button_color,
                    color: "white",
                    padding: "5px 8px", // Smaller padding
                    fontSize: "12px", // Smaller font size
                    borderRadius: "4px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    minWidth: "80px", // Ensure width stays the same during loading
                  }}
                  onClick={onRefresh}
                  disabled={loading} // Disable button while loading
                >
                  {loading ? (
                    <div
                      style={{
                        width: "14px",
                        height: "14px",
                        border: "2px solid white",
                        borderTop: "2px solid transparent",
                        borderRadius: "50%",
                        animation: "spin 0.8s linear infinite",
                      }}
                    />
                  ) : (
                    "Refresh"
                  )}
                </button>

                {/* Add CSS for spinner animation */}
                <style>
                  {`
                    @keyframes spin {
                      to {
                        transform: rotate(360deg);
                      }
                    }
                  `}
                </style>
              </div>
              <div style={{ margin: "5px 5px 5px 2px" }}>
                <button
                  className="btn"
                  style={{
                    backgroundColor: "green",
                    color: "white",
                    padding: "5px 8px", // Smaller padding
                    fontSize: "12px", // Smaller font size
                    borderRadius: "4px",
                  }}
                  onClick={onUpdate}
                >
                  Update
                </button>
              </div>
            </div>
          )}
          {toggle_views && toggle_views.length > 0 && (
  <>
    {toggle_views.length < 20 ? (
      // Render normal buttons if toggle_views is less than 20
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "10px",
          padding: "10px",
          marginBottom: "10px",
        }}
      >
        {toggle_views.map((view: string, index: number) => (
          <button
            key={index}
            className={`btn ${viewId === index ? "btn-danger" : "btn-secondary"}`}
            style={{
              ...buttonStyle,
              borderRadius: "8px",
              color: "#055A6E",
              backgroundColor: "#F3FAFD",
              fontWeight: "bold",
            }}
            onClick={() => {
              setViewId(index);
              setpreviousViewId(viewId);
            }}
            disabled={loading}
          >
            {view}
            {loading && viewId === index ? (
              <div
                style={{
                  width: "14px",
                  height: "14px",
                  border: "2px solid black",
                  borderTop: "2px solid transparent",
                  borderRadius: "50%",
                  animation: "spin 0.8s linear infinite",
                  marginLeft: "8px",
                }}
              />
            ) : null}
          </button>
        ))}
      </div>
    ) : (
      // Render overlap container if toggle_views is 20 or more
      <div
        className="toggle-view-container"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(100px, 1fr))",
          gap: "10px",
          overflowY: "auto",
          maxHeight: "200px",
          padding: "10px",
          border: "1px solid #ddd",
          borderRadius: "8px",
          backgroundColor: "#eef9f8",
          width: "100%",
          marginBottom: "10px",
        }}
      >
        {toggle_views.map((view: string, index: number) => (
          <button
            key={index}
            className={`btn ${viewId === index ? "btn-danger" : "btn-secondary"}`}
            style={{
              ...buttonStyle,
              borderRadius: "8px",
              color: "#055A6E",
              backgroundColor: "#F3FAFD",
              fontWeight: "bold",
            }}
            onClick={() => {
              setViewId(index);
              setpreviousViewId(viewId);
            }}
            disabled={loading}
          >
            {view}
            {loading && viewId === index ? (
              <div
                style={{
                  width: "14px",
                  height: "14px",
                  border: "2px solid black",
                  borderTop: "2px solid transparent",
                  borderRadius: "50%",
                  animation: "spin 0.8s linear infinite",
                  marginLeft: "8px",
                }}
              />
            ) : null}
          </button>
        ))}
      </div>
    )}
  </>
)}
        </div>
  
        <div
          className={grid_options.theme || "ag-theme-alpine-dark"}
          style={{
            width: "100%",
            height: kwargs["grid_height"] ? kwargs["grid_height"] : "100%",
          }}
        >
          {/* Add test streaming_list_text to kwargs for testing
          {(() => {
            if (!kwargs.streaming_list_text) {
              kwargs.streaming_list_text = ["some", "test", "list"];
            }
            return null;
          })()} */}
          {/* Streamer for streaming_list_text if present */}
          {kwargs.streaming_list_text && Array.isArray(kwargs.streaming_list_text) && (
            <div
              style={{
              width: "100%",
              background: "#F3FAFD", // Match toggle_views button background
              color: "#055A6E",      // Match toggle_views button text color
              padding: "4px 10px",
              fontSize: "13px",
              borderBottom: "1px solid #ddd",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
              marginBottom: "4px",
              fontWeight: "bold",    // Match bold style from buttons
              }}
            >
              <div
              style={{
                display: "block",
                width: "100%",
                whiteSpace: "nowrap",
                overflow: "hidden",
                position: "relative",
              }}
              >
              <div
                style={{
                display: "inline-block",
                paddingLeft: "100%",
                animation: "scroll-left 20s linear infinite",
                }}
              >
                {kwargs.streaming_list_text.join("   |   ")}
              </div>
              <style>
                {`
                @keyframes scroll-left {
                  0% {
                  transform: translateX(0%);
                  }
                  100% {
                  transform: translateX(-100%);
                  }
                }
                `}
              </style>
              </div>
            </div>
          )}

{kwargs['filter_button'] && kwargs['filter_button'] !== '' && (
  <div style={{ marginBottom: 8 }}>
    {uniqueValues.map(val => (
      <button
        key={val}
        onClick={() => handleButtonFilter(val)}
        style={{
          background: activeFilter === val ? "#3498db" : "#F3FAFD", // match main button color and toggle_views bg
          color: activeFilter === val ? "white" : "#055A6E",        // match toggle_views text color
          border: activeFilter === val ? "2px solid #1abc9c" : "1px solid #ddd",
          borderRadius: "6px",
          fontWeight: "bold",
          fontSize: "12px",
          padding: "5px 10px",
          margin: "0 4px 4px 0",
          boxShadow: activeFilter === val ? "0 2px 6px rgba(52,152,219,0.10)" : "none",
          transition: "all 0.15s",
          cursor: "pointer",
        }}
      >
        {val}
      </button>
    ))}
    <button
      onClick={() => handleButtonFilter(null)}
      style={{
        background: "#b0c4de", // blue-grey (LightSteelBlue)
        color: "#055A6E",
        border: "1.5px solid #8fa6bc",
        borderRadius: "6px",
        fontWeight: "bold",
        fontSize: "12px",
        padding: "5px 10px",
        margin: "0 4px 4px 0",
        boxShadow: "0 2px 6px rgba(176,196,222,0.10)",
        transition: "all 0.15s",
        cursor: "pointer",
      }}
    >
      Clear
    </button>
  </div>
)}


          <AgGridReact
            ref={gridRef}
            rowData={rowData}
            pinnedBottomRowData={subtotalsRow}
            onFilterChanged={onFilterChanged}
            getRowStyle={getRowStyle}
            rowStyle={{ fontSize: 12, padding: 0 }}
            headerHeight={30}
            rowHeight={30}
            onGridReady={onGridReady}
            autoGroupColumnDef={autoGroupColumnDef}
            animateRows={true}
            suppressAggFuncInHeader={true}
            getRowId={getRowId}
            gridOptions={grid_options}
            onCellValueChanged={onCellValueChanged}
            columnTypes={columnTypes}
            sideBar={grid_options.sideBar === false ? false : sideBar}
          />
        </div>
      </div>
    </>
  );
}

export default AgGrid

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
import { parseISO, compareAsc } from "date-fns"
import { format } from "date-fns-tz"
import { duration } from "moment"
import "./styles.css"
import axios from "axios"
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

import { order_rules_default } from "./utils/order_rules"

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
    return (
      <button
        onClick={btnClickedHandler}
        style={{
          background: "transparent",
          color: "black",
          width: "100%",
          borderColor: props.borderColor ? props.borderColor : "black",
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

  let { buttons, toggle_views } = kwargs
  const [rowData, setRowData] = useState<any[]>([])
  const [modalShow, setModalshow] = useState(false)
  const [modalData, setModalData] = useState({})
  const [promptText, setPromptText] = useState("")
  const [viewId, setViewId] = useState(0)

  useEffect(() => {
    Streamlit.setFrameHeight()
    if (buttons.length) {

      buttons = deepMap(buttons, parseJsCodeFromPython, ["rowData"]) //if JsCode comes through buttons props

      buttons.map((button: any) => {
        //extracts know parameters from button, all other unknow parameters sent are stored in otherKeys
        const { prompt_field, prompt_message, button_api, prompt_order_rules, col_header, col_headername, col_width, 
          pinned, button_name, border_color, ...otherKeys
        } = button
        grid_options.columnDefs!.push({
          ...otherKeys, //merges all other parameters sent on buttons array on columnDefs
          field: col_header ? col_header : index,
          headerName: col_headername,
          width: col_width,
          pinned: pinned,
          cellRenderer: BtnCellRenderer,
          cellRendererParams: {
            col_header: col_header,
            buttonName: button_name,
            borderColor: border_color,
            clicked: async function (row_index: any) {
              try {
                const selectedRow = g_rowdata.find(
                  (row) => row[index] == row_index
                )
                if (prompt_order_rules) {
                  const str = selectedRow[prompt_field]
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
                      : str
                  setModalshow(true)
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
                  })
                  const rules_value: any = {}
                  prompt_order_rules.map((rule: string) => {
                    rules_value[rule] = selectedField[rule]
                  })
                  setPromptText(rules_value)
                } else if (prompt_field && prompt_message) {
                  setModalshow(true)
                  setModalData({
                    prompt_message,
                    button_api: button_api,
                    username: username,
                    prod: prod,
                    selectedRow: selectedRow,
                    kwargs: kwargs,
                  })
                  setPromptText(selectedRow[prompt_field])
                  // const num = prompt(prompt_message, selectedRow[prompt_field]);
                  // if (num == null) return;
                  // const res = await axios.post(button_api, {
                  //   username: username,
                  //   prod: prod,
                  //   selected_row: selectedRow,
                  //   default_value: num,
                  //   ...kwargs,
                  // })
                } else {
                  if (window.confirm(prompt_message)) {
                    const res = await axios.post(button_api, {
                      username: username,
                      prod: prod,
                      selected_row: selectedRow,
                      ...kwargs,
                    })
                  }
                  toastr.success("Success!")
                }
              } catch (error) {
                alert(`${error}`)
              }
            },
          },
        })
      })
    }
    // parseGridoptions()
  })

  const fetchAndSetData = async () => {
    const array = await fetchData()
    if (array === false) return false
    setRowData(array)
    g_rowdata = array
    // const api = gridRef.current!.api
    // const id_array = array.map((item: any) => item[index])
    // const old_id_array = g_rowdata.map((item: any) => item[index])
    // const toUpdate = array.filter((row: any) => id_array.includes(row[index]))
    // const toRemove = g_rowdata.filter((row) => !id_array.includes(row[index]))
    // const toAdd = array.filter((row: any) => !old_id_array.includes(row[index]))
    // api.applyTransactionAsync({
    //   update: toUpdate,
    //   remove: toRemove,
    //   add: toAdd,
    // })
    // g_rowdata = array
    return true
  }

  useEffect(() => {
    onRefresh()
  }, [viewId])

  const fetchData = async () => {
    try {
      const res = await axios.post(api, {
        username: username,
        prod: prod,
        ...kwargs,
        toggle_view_selection: toggle_views ? toggle_views[viewId] : "none",
      })
      const array = JSON.parse(res.data)
      console.log(
        "toggle_views[viewId],viewId :>> ",
        toggle_views[viewId],
        viewId
      )
      console.log("table data :>> ", array)
      if (array.status == false) {
        toastr.error(`Fetch Error: ${array.message}`)
        return false
      }
      return array
    } catch (error: any) {
      toastr.error(`Fetch Error: ${error.message}`)
      return false
    }
  }

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
        if (array == false) {
          // toastr.error(`Error: ${array.message}`)
          return
        }
        setRowData(array)
        g_rowdata = array
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
    if (g_newRowData == null) g_newRowData = {}
    g_newRowData[event.data[index]] = event.data
    console.log("Data after change is", g_newRowData)
  }, [])

  const onRefresh = async () => {
    try {
      const success = await fetchAndSetData()
      success && toastr.success("Refresh success!")
    } catch (error: any) {
      toastr.error(`Refresh Failed! ${error.message}`)
    }
  }

  const onUpdate = async () => {
    if (g_newRowData == null) {
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
    try {
      const background = params.data["color_row"] ?? undefined;
      const color = params.data["color_row_text"] ?? undefined;
      return { background, color };
    } catch (error) {
      console.error("Error accessing row style:", error);
      return undefined; // Return undefined when an error occurs
    }
  };

  const button_color = "#3498db"; // Set your custom button color here

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
                  }}
                  onClick={onRefresh}
                >
                  Refresh
                </button>
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
          <div className="d-flex flex-row gap-2">
            {toggle_views?.map((view: string, index: number) => (
              <span key={index}>
                <button
                  className={`btn ${
                    viewId === index ? "btn-danger" : "btn-secondary"
                  }`}
                  style={{
                    padding: "5px 8px", // Smaller padding
                    fontSize: "12px", // Smaller font size
                    borderRadius: "4px",
                  }}
                  onClick={() => setViewId(index)}
                >
                  {view}
                </button>
              </span>
            ))}
          </div>
        </div>
  
        <div
          className={grid_options.theme || "ag-theme-alpine-dark"}
          style={{
            width: "100%",
            height: kwargs["grid_height"] ? kwargs["grid_height"] : "100%",
          }}
        >
          <AgGridReact
            ref={gridRef}
            rowData={rowData}
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
          />
        </div>
      </div>
    </>
  );
}

export default AgGrid

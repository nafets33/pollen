import Select from "react-select";
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
import Ozz from "./components/VoiceChatModal";
import TickerSearchModal from "./components/TickerSearchModal";

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
import { deepMap } from "./utils"

const isDev = process.env.NODE_ENV === 'development';
const log = isDev ? console.log : () => { };
const warn = isDev ? console.warn : () => { };
const error = console.error; // Always log errors

type Props = {
  username: string
  api: string
  api_update: string
  api_ws?: string
  refresh_sec?: number
  refresh_cutoff_sec?: number
  gridoption_build?: any
  prod?: boolean
  grid_options?: any
  index: string
  enable_JsCode: boolean
  kwargs: any,
  autoUpdate?: boolean;
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
  const linkField = props.column.colDef["linkField"];
  const baseURL = props.column.colDef.baseURL;
  const linkValue = props.data && linkField ? props.data[linkField] : null;

  // Only render a link for real data rows
  if (linkValue && baseURL) {
    return (
      <a href={`${baseURL}/${linkValue}`} target="_blank" rel="noopener noreferrer">
        {props.value}
      </a>
    );
  }
  // For pivot/group/total rows, just render the value
  return <span>{props.value}</span>;
};


toastr.options = {
  positionClass: "toast-top-full-width",
  hideDuration: 300,
  timeOut: 3000,
}


// On Filter Headers Add right section for Quant AI form Handle full screen with chat session Can we lanuch custom_VoiceGPT to it? Import ...
function interpolateHexColor(minColor: string, maxColor: string, ratio: number): string {
  const parseHex = (hex: string) => [
    parseInt(hex.slice(1, 3), 16),
    parseInt(hex.slice(3, 5), 16),
    parseInt(hex.slice(5, 7), 16),
  ];
  const [r1, g1, b1] = parseHex(minColor);
  const [r2, g2, b2] = parseHex(maxColor);
  const r = Math.round(r1 + (r2 - r1) * ratio);
  const g = Math.round(g1 + (g2 - g1) * ratio);
  const b = Math.round(b1 + (b2 - b1) * ratio);
  return `rgb(${r}, ${g}, ${b})`;
}


const AgGrid = (props: Props) => {
const BtnCellRenderer = (props: any) => {
  const btnClickedHandler = () => {
    props.clicked(props.node.id)
  };
  if (!props || !props.node) return null;
  if (props.node.rowPinned === 'bottom') {
    return <span>{props.value}</span>;
  }

  // ✅ Original subtotalStyle — unchanged, used for all non-wave buttons
  const subtotalStyle =
    props.data && props.col_header && props.data[`${props.col_header}_cellStyle`]
      ? props.data[`${props.col_header}_cellStyle`]
      : props.cellStyle;

  // Detect wave format: "buy(4) $19,690" or "sell(3) $5,000"
  const waveMatch = typeof props.value === 'string'
    ? props.value.match(/^(buy|sell)\((\d+)\)\s*\$([0-9,.\-]+)/i)
    : null;

  if (waveMatch) {
    const action = waveMatch[1];
    const length = waveMatch[2];
    const amount = waveMatch[3];
    const amountNum = parseFloat(amount.replace(/,/g, ''));
    const actionDisplay = action.charAt(0).toUpperCase() + action.slice(1);
    const isBuy = action.toLowerCase().includes('buy');

    // ✅ Find max position value across ALL rows in this column
    let maxAmount = 0;
    if (props.api && props.colDef?.field) {
      props.api.forEachNode((node: any) => {
        if (node.data) {
          const val = node.data[props.colDef.field];
          if (typeof val === 'string') {
            const m = val.match(/^(?:buy|sell)\(\d+\)\s*\$([0-9,.\-]+)/i);
            if (m && m[1]) {
              const n = parseFloat(m[1].replace(/,/g, ''));
              if (!isNaN(n) && n > maxAmount) maxAmount = n;
            }
          }
        }
      });
    }

    const ratio = maxAmount > 0 ? Math.min(amountNum / maxAmount, 1) : 0;

// ✅ Get colors from kwargs.wave_color_rules or use defaults
const waveColorRules = kwargs.wave_color_rules || {
  buy: {
    textColor: '#0a6e1f',
    borderColor: '#0a9d25',
    bgColorMin: '#f3f3f0',
    bgColorMax: '#656560',
  },
  sell: {
    textColor: '#a00000',
    borderColor: '#ed370f',
    bgColorMin: '#f9f9f7',
    bgColorMax: '#474742',
  },
  position: {
    textColor: '#000000'
  }
};

const colorSet = isBuy ? waveColorRules.buy : waveColorRules.sell;

// ✅ Text color: from kwargs or fixed green/red based on action
const borderColor = colorSet.borderColor;

const textColorWave = colorSet.textColor;   // green/red for Wave line
const textColorPosition = waveColorRules.position?.textColor || '#121111cc';  // black for Position line

// ✅ Background: light blue → darker blue heat map
const bgColor = interpolateHexColor(
  colorSet.bgColorMin || 'rgb(161, 228, 139)', 
  colorSet.bgColorMax || 'rgb(201, 182, 31)', 
  ratio
);

    return (
      <button
        onClick={btnClickedHandler}
        style={{
          background: `radial-gradient(ellipse at center, #ffffff 65%, ${bgColor} 85%)`,
          border: "2px solid " + borderColor,
          borderRadius: "0",
          width: "100%",
          height: "100%",
          cursor: "pointer",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          lineHeight: "1.3",
          padding: "1px 2px",
          boxSizing: "border-box",
          outline: "none",
        }}
      >
        <div style={{ fontSize: "13px", whiteSpace: "nowrap" }}>
          <span style={{ fontWeight: "bold", color: textColorWave }}></span>
          <span style={{ fontWeight: "normal", color: textColorWave }}>{actionDisplay}({length})</span>
        </div>
        <div style={{ fontSize: "13px", whiteSpace: "nowrap" }}>
          <span style={{ fontWeight: "bold", color: textColorPosition }}>$: </span>
          <span style={{ fontWeight: "normal", color: textColorPosition }}>{amount}</span>
        </div>
      </button>
    );
  }

  // ✅ All other buttons — exactly as original
  return (
    <button
      onClick={btnClickedHandler}
      style={{
        background: "transparent",
        border: subtotalStyle?.border || "none",
        width: props.width ? props.width : "100%",
        color: subtotalStyle?.color || "inherit",
        ...subtotalStyle,
      }}
    >
      {props.col_header ? props.value : props.buttonName}
    </button>
  );
};

  function buildDetailGridOptions(detailGridOptions: any, level: number): any {
    const options = { ...detailGridOptions, masterDetail: true };

    options.getDetailRowData = (params: any) => {
      let nestedRows = [];
      if (Array.isArray(params.data.nestedRows)) {
        nestedRows = params.data.nestedRows;
      } else if (params.data.nestedRows) {
        nestedRows = [params.data.nestedRows];
      }
      params.successCallback(nestedRows.length ? nestedRows : []);
    };

    if (
      options.detailCellRendererParams &&
      options.detailCellRendererParams.detailGridOptions
    ) {
      options.detailCellRendererParams.detailGridOptions = buildDetailGridOptions(
        options.detailCellRendererParams.detailGridOptions,
        level + 1
      );
    }

    return options;
  }
  const getGridOptions = () => {
    let options = { ...grid_options };
    if (kwargs.nestedGridEnabled && kwargs.detailGridOptions) {
      options.masterDetail = true;
      options.detailCellRendererParams = {
        detailGridOptions: buildDetailGridOptions(kwargs.detailGridOptions, 1),
        getDetailRowData: (params: any) => {
          let nestedRows = [];
          if (Array.isArray(params.data.nestedRows)) {
            nestedRows = params.data.nestedRows;
          } else if (params.data.nestedRows) {
            nestedRows = [params.data.nestedRows];
          }
          params.successCallback(nestedRows.length ? nestedRows : []);
        },
      };
    } else {
      options.masterDetail = false;
      options.detailCellRendererParams = undefined;
    }
    return options;
  };


  const gridRef = useRef<AgGridReact>(null)
  const {
    username,
    api,
    api_update,
    api_ws = undefined,
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
  let { buttons, toggle_views, api_key, api_lastmod_key = null, columnOrder = [],
    refresh_success = null, filter_button = '' } = kwargs
  const [rowData, setRowData] = useState<any[]>([])
  const [modalShow, setModalshow] = useState(false)
  const [modalData, setModalData] = useState({})
  const [promptText, setPromptText] = useState("")
  const [viewId, setViewId] = useState(0)
  const [lastModified, setLastModified] = useState<string | null>(null);
  const [previousViewId, setpreviousViewId] = useState(89)
const [activeFilter, setActiveFilter] = useState<Record<string, string | null>>({});  const [selectedColumnSetKey, setSelectedColumnSetKey] = useState<string | null>(null);
  const [initialColumnState, setInitialColumnState] = useState<any>(null);
const [tickerSearchModalShow, setTickerSearchModalShow] = useState(false);
  const [selectedCellContent, setSelectedCellContent] = useState<string | null>(null);
  const onCellClicked = (event: any) => {
    if (event.value) {
      setSelectedCellContent(event.value); // Set the clicked cell's value
    }
  };


  useEffect(() => {
    if (!kwargs.api_ws) {
      log("⚠️  api_ws is undefined, WebSocket not started.");
      return;
    }

    log("🔌 Attempting WebSocket connection to:", kwargs.api_ws);

    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout;
    let heartbeatInterval: NodeJS.Timeout;
    let isIntentionallyClosed = false;
    let reconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 10;
    const HEARTBEAT_INTERVAL = 300000; // 5 minutes
    const RECONNECT_DELAY = 3000; // 3 seconds

    const connectWebSocket = () => {
      try {
        ws = new WebSocket(kwargs.api_ws);

        ws.onopen = () => {
          log("✅ WebSocket connected!");
          reconnectAttempts = 0;

          const handshake = {
            username: username,
            toggle_view_selection: toggle_views ? toggle_views[viewId] : 'queen',
            api_key: api_key,
            prod: prod,
          };

          log("📤 Sending handshake:", handshake);
          ws?.send(JSON.stringify(handshake));

          // // ✅ Start heartbeat
          startHeartbeat();
        };

        ws.onmessage = (event) => {
          log("📥 WebSocket message received");
          try {
            const data = JSON.parse(event.data);

            // Handle pong response
            if (data.type === 'pong') {
              log("💓 Heartbeat acknowledged");
              return;
            }

            // Handle connection confirmation
            if (data.type === 'connection_established') {
              log("Handshake confirmed:", data.message, prod);
              return;
            }

            // Handle array of updates (batch)
            if (Array.isArray(data) && data.length > 0) {
              const rowsToUpdate: any[] = [];
              const deltaFlashInfo: Record<string, Record<string, { direction: 'positive' | 'negative' }>> = {};

              data.forEach(({ row_id, updates }) => {
                const existingNode = gridRef.current?.api.getRowNode(row_id);
                if (existingNode && existingNode.data) {
                  // Start with existing data to preserve everything
                  const updatedRow = { ...existingNode.data };

                  // Track changes for flash animation
                  if (!deltaFlashInfo[row_id]) {
                    deltaFlashInfo[row_id] = {};
                  }

                  // Apply only the updates from WebSocket
                  Object.keys(updates).forEach(key => {
                    const oldValue = existingNode.data[key];
                    const newValue = updates[key];

                    // ✅ Only flash if enableCellChangeFlash is true AND agAnimateShowChangeCellRenderer is NOT used
                    const columnDef = gridRef.current?.api.getColumnDef(key);
                    const flashEnabled = columnDef?.enableCellChangeFlash === true;
                    const hasAgAnimate = columnDef?.cellRenderer === 'agAnimateShowChangeCellRenderer';

                    // Detect numeric changes for flash animation (only if custom flash is enabled and AG Grid animator not present)
                    if (flashEnabled && !hasAgAnimate) {
                      const oldNum = parseFloat(oldValue);
                      const newNum = parseFloat(newValue);

                      if (!isNaN(oldNum) && !isNaN(newNum) && oldNum !== newNum) {
                        deltaFlashInfo[row_id][key] = {
                          direction: newNum > oldNum ? 'positive' : 'negative'
                        };
                      }
                    }

                    updatedRow[key] = newValue;
                  });

                  // Ensure index is preserved
                  updatedRow[index] = row_id;

                  rowsToUpdate.push(updatedRow);
                } else {
                  log("⚠️  Row not found for update:", row_id);
                }
              });

              // ✅ Apply updates in batches for smoother visual effect
              if (rowsToUpdate.length > 0) {
                // First, apply the transaction to update the grid
                gridRef.current?.api.applyTransaction({
                  update: rowsToUpdate
                });

                // Then apply custom flash animations (only for columns with enableCellChangeFlash but no agAnimate)
                requestAnimationFrame(() => {
                  rowsToUpdate.forEach(row => {
                    const rowId = row[index];
                    if (deltaFlashInfo[rowId]) {
                      Object.keys(deltaFlashInfo[rowId]).forEach(field => {
                        const { direction } = deltaFlashInfo[rowId][field];

                        const cellElement = document.querySelector(
                          `.ag-row[row-id="${rowId}"] .ag-cell[col-id="${field}"]`
                        );

                        if (cellElement) {
                          cellElement.classList.remove('flash-positive', 'flash-negative');
                          void (cellElement as HTMLElement).offsetWidth;
                          cellElement.classList.add(`flash-${direction}`);

                          setTimeout(() => {
                            cellElement.classList.remove(`flash-${direction}`);
                          }, 1000);
                        }
                      });
                    }
                  });
                });

                log(`✅ Updated ${rowsToUpdate.length} rows at once`);

                if (gridRef.current?.api) {
                  calculateAndUpdateSubtotals(gridRef.current.api);
                }
              }
            }

          }
          catch (error) {
            console.error("❌ Error processing WebSocket message:", error);
          }
        };

        ws.onerror = (error) => {
          console.error("❌ WebSocket error:", error);
          stopHeartbeat();
        };

        ws.onclose = (event) => {
          log("🔌 WebSocket closed:", {
            code: event.code,
            reason: event.reason,
            wasClean: event.wasClean
          });

          stopHeartbeat();

          // ✅ Auto-reconnect
          if (!isIntentionallyClosed) {
            if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
              reconnectAttempts++;
              log(`🔄 Reconnect attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS} in ${RECONNECT_DELAY / 1000}s...`);

              reconnectTimeout = setTimeout(() => {
                log("🔄 Reconnecting WebSocket...");
                connectWebSocket();
              }, RECONNECT_DELAY);
            } else {
              console.error("❌ Max reconnection attempts reached. Please refresh the page.");
              toastr.error("WebSocket connection lost. Please refresh the page.");
            }
          }
        };
      } catch (error) {
        console.error("❌ Error creating WebSocket:", error);
        stopHeartbeat();
      }
    };

    // ✅ Heartbeat to keep connection alive
    const startHeartbeat = () => {
      stopHeartbeat();

      heartbeatInterval = setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
          log("💓 Sending heartbeat ping...");
          try {
            ws.send(JSON.stringify({ type: 'ping' }));
          } catch (error) {
            console.error("❌ Failed to send heartbeat:", error);
            stopHeartbeat();
          }
        } else {
          console.warn("⚠️  WebSocket not open during heartbeat");
          stopHeartbeat();

          if (!isIntentionallyClosed && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            log("🔄 Connection lost, attempting to reconnect...");
            connectWebSocket();
          }
        }
      }, HEARTBEAT_INTERVAL);
    };

    const stopHeartbeat = () => {
      if (heartbeatInterval) {
        clearInterval(heartbeatInterval);
        heartbeatInterval = undefined as any;
      }
    };

    // Initial connection
    connectWebSocket();

    // Cleanup
    return () => {
      log("🧹 Cleaning up WebSocket connection");
      isIntentionallyClosed = true;
      stopHeartbeat();
      clearTimeout(reconnectTimeout);
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [kwargs.api_ws, index, viewId, username, api_key]);

  const checkLastModified = async (): Promise<boolean> => {
    try {
      if (api_lastmod_key === null) {
        log("api key is null, returning false");
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
        if (res.data?.lastModified !== lastModified) {
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
      setpreviousViewId(currentViewId);
      return true;
    } else {
      return false;
    }
  };

  // BUTTONS, MOVE OUT OF USEEFFECT
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
          initialWidth: col_width,
          pinned: pinned,
          cellRenderer: BtnCellRenderer,
          suppressSizeToFit: true,
          // valueFormatter: otherKeys.valueFormatter ? otherKeys.valueFormatter : undefined,
          filterParams,
          cellRendererParams: {
            col_header,
            buttonName: button_name,
            borderColor: border_color,
            border: border,
            filterParams,
            cellStyle: button.cellStyle,
            // valueFormatter: button.valueFormatter,
            ...(button.cellRendererParams || {}),
            clicked: async function (row_index: any) {
              try {
                // const selectedRow = g_rowdata.find((row) => row[index] === row_index);
                const freshNode = gridRef.current?.api.getRowNode(row_index);
                if (!freshNode?.data) {
                  console.error("❌ Could not find fresh row data for:", row_index);
                  toastr.error("Could not load row data");
                  return;
                }
                const selectedRow = freshNode.data;
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
                    gridRef: gridRef,           // ✅ Pass grid reference
                    index: index,               // ✅ Pass index
                    prompt_message,
                    button_api: button_api,
                    username: username,
                    prod: prod,
                    selectedRow: selectedRow,   // ✅ Fresh data from grid
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
                    gridRef: gridRef,           // Pass grid reference
                    index: index,               // Pass index
                    prompt_message,
                    button_api: button_api,
                    username: username,
                    prod: prod,
                    selectedRow: selectedRow,   // Fresh data from grid
                    kwargs: kwargs,
                  });
                  setPromptText(selectedRow[prompt_field]);
                  setModalshow(true)
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

      // If view has changed, skip checkLastModified
      if (!hasViewChanged && refresh_sec && refresh_sec > 0) {
        const isLastModified = await checkLastModified();
        if (!isLastModified) {
          return false;
        }
      }

      log("fetching data...", api);
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


  useEffect(() => {
    // ✅ Only poll if WebSocket is NOT available
    if (!api_ws && refresh_sec && refresh_sec > 0) {
      log("📡 Starting polling (no WebSocket available)");
      const interval = setInterval(fetchAndSetData, refresh_sec * 1000)
      let timeout: NodeJS.Timeout
      if (refresh_cutoff_sec > 0) {
        timeout = setTimeout(() => {
          clearInterval(interval)
          log("⏹️ Polling stopped (cutoff reached)")
        }, refresh_cutoff_sec * 1000)
      }
      return () => {
        clearInterval(interval)
        if (timeout) clearTimeout(timeout)
      }
    } else if (api_ws) {
      log("🔌 WebSocket active, polling disabled");
    }
  }, [api_ws, refresh_sec, refresh_cutoff_sec, props, viewId])




  const autoSizeAll = useCallback((skipHeader: boolean) => {
    const allColumnIds: string[] = [];
    const columnApi = gridRef.current!.columnApi;

    columnApi.getColumns()!.forEach((column: any) => {
      const actualColDef = column.getColDef(); // Get actual column def from AG Grid

      // Only autosize columns that don't have an explicit width set
      if (!actualColDef.width && !actualColDef.initialWidth && !actualColDef.suppressSizeToFit) {
        allColumnIds.push(column.getId());
      }
    });

    columnApi.autoSizeColumns(allColumnIds, skipHeader);
  }, []);

  const sizeToFit = useCallback(() => {
    gridRef.current!.api.sizeColumnsToFit({
      defaultMinWidth: 100,
    })
  }, [])


  // Reusable function to calculate and update subtotals
  const calculateAndUpdateSubtotals = useCallback((api: any) => {
    if (!kwargs.subtotal_cols || kwargs.subtotal_cols.length === 0 || !api) return;

    let filteredRows: any[] = [];
    api.forEachNodeAfterFilterAndSort((node: any) => {
      if (node.data && !node.rowPinned) filteredRows.push(node.data);
    });

    let subtotal: any = { [index]: "Totals" };

    kwargs.subtotal_cols.forEach((col: string) => {
      const sum = filteredRows.reduce((sum, row) => {
        let val = row[col];
        const originalVal = val

        // Skip undefined, null, or empty string
        if (val === undefined || val === null || val === "") {
          return sum;
        }

        // Handle string values with special formatting
        if (typeof val === "string") {
          // ✅ Detect button format: "buy(4) $19,690" or "sell(3) $5,000"
          const buttonMatch = val.match(/(buy|sell)\(\d+\)\s*\$([0-9,.\-]+)/i);

          if (buttonMatch && buttonMatch[2]) {
            // Extract ONLY the dollar amount from button format
            val = buttonMatch[2].replace(/,/g, "");
          } else {
            // Standard currency/number formatting
            val = val.replace(/[$,]/g, "");

            // Handle percentage values
            if (val.includes("%")) {
              val = val.replace(/%/g, "");
            }

            // Remove any other non-numeric characters except decimal point and minus
            val = val.replace(/[^0-9.\-]/g, "");
          }
        }

        const num = Number(val);
        return sum + (isNaN(num) ? 0 : num);
      }, 0);

      // Check if invalid
      if (isNaN(sum) || !isFinite(sum)) {
        subtotal[col] = "";
        return;
      }

      // ✅ Check if column has a valueFormatter - if yes, store raw number, otherwise format
      const columnDef = api.getColumnDef(col);
      const hasFormatter = columnDef && (columnDef.valueFormatter || columnDef.type);

      if (hasFormatter) {
        // Store raw number - let column's valueFormatter handle formatting
        subtotal[col] = sum;
      } else {
        // No formatter - format with commas ourselves
        subtotal[col] = sum.toLocaleString('en-US');
      }
    });

    // ✅ Determine pin location from grid_options
    const hasPinnedTop = grid_options.pinnedTopRowData && grid_options.pinnedTopRowData.length > 0;
    const hasPinnedBottom = grid_options.pinnedBottomRowData && grid_options.pinnedBottomRowData.length > 0;

    // Update the pinned row at the correct location
    if (hasPinnedTop) {
      api.setPinnedTopRowData([subtotal]);
    } else if (hasPinnedBottom) {
      api.setPinnedBottomRowData([subtotal]);
    } else {
      // Default to bottom if not specified
      api.setPinnedBottomRowData([subtotal]);
    }
  }, [kwargs.subtotal_cols, index, grid_options]);

  const onGridReady = useCallback(async (params: GridReadyEvent) => {
    setTimeout(async () => {
      try {
        log("websocket api is", api_ws, kwargs.api_ws);
        const array = await fetchData();
        if (array === false) return;

        setRowData(array);
        g_rowdata = array;

        // ✅ Calculate subtotals if subtotal_cols is provided
        if (kwargs.subtotal_cols && kwargs.subtotal_cols.length > 0) {
          calculateAndUpdateSubtotals(params.api);
        }

        // Autosize all columns after data is set
        autoSizeAll(true);

        // Store initial column state
        if (params.columnApi) {
          setInitialColumnState(params.columnApi.getColumnState());
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
      // ✅ Always return a string
      return String(params.data[index]);
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

  const onCellValueChanged = useCallback(
    async (event: any) => {
      if (props.autoUpdate) {
        try {
          const updatedRow = event.data; // The updated row data
          log("Auto-updating row:", updatedRow);

          // Send the updated row to the API
          const response = await axios.post(api_update, {
            username: username,
            prod: prod,
            updated_row: updatedRow, // Send the updated row
            ...kwargs, // Include any additional parameters
          });

          if (response.status === 200) {
            toastr.success("Row updated successfully!");
          } else {
            toastr.error("Failed to update row.");
          }
        } catch (error) {
          if (error && typeof error === "object" && "message" in error) {
            toastr.error(`Error updating row: ${(error as any).message}`);
          } else {
            toastr.error(`Error updating row: ${String(error)}`);
          }
        }
      } else {
        // Store changes for manual update
        if (g_newRowData === null) g_newRowData = {};
        g_newRowData[event.data[index]] = event.data;
        log("Data after change is", g_newRowData);
      }
    },
    [props.autoUpdate, api_update, username, prod, kwargs, index]
  );


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

  const gridContainerRef = useRef(null);

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

    try {
      const background = params.data["color_row"] ?? undefined;
      const color = params.data["color_row_text"] ?? undefined;
      return { background, color };
    } catch (error) {
      console.error("Error accessing row style:", error);
      return undefined; // Return undefined when an error occurs
    }
  };


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

  const getUniqueColumnValues = (column: string, rowData: any[]) => {
    return Array.from(new Set(rowData.map(row => row[column]))).filter(
      v => v !== undefined && v !== null
    );
  };
  // let filter_button = "piece_name";

const filterButtons: string[] = Array.isArray(filter_button) ? filter_button : [];

const handleButtonFilter = (column: string, value: string | null) => {
  setActiveFilter(prev => ({ ...prev, [column]: value }));
  if (gridRef.current && gridRef.current.api) {
    const api = gridRef.current.api;
    if (value) {
      api.setFilterModel({ ...api.getFilterModel(), [column]: { filterType: "set", values: [value] } });
    } else {
      const model = api.getFilterModel();
      delete model[column];
      api.setFilterModel(model);
    }
  }
};






  return (


    <>

      {kwargs.show_cell_content && selectedCellContent && (
        <div
          style={{
            position: "absolute",
            top: "10px",
            right: "10px",
            background: "white",
            border: "1px solid #ddd",
            borderRadius: "8px",
            padding: "10px",
            boxShadow: "0 2px 6px rgba(0, 0, 0, 0.1)",
            zIndex: 1000,
            maxWidth: "300px", // Limit the width
            maxHeight: "200px", // Limit the height
            overflow: "auto", // Add scrollbars for overflow
            width: "fit-content",
          }}
        >
          <p style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
            {selectedCellContent}
          </p>
          <button
            onClick={() => setSelectedCellContent(null)}
            style={{
              background: "#3498db",
              color: "white",
              border: "none",
              borderRadius: "2px",
              padding: "3px 5px",
              cursor: "pointer",
            }}
          >
            <h5 style={{ fontSize: "8px", margin: "0 0 6px 0" }}>x</h5>
          </button>
        </div>
      )}

      {toggle_views && toggle_views.length > 0 && (
        <>
          <div
            style={{
              fontWeight: "bold",
              color: "#055A6E",
              marginBottom: "3px",
              fontSize: "14px",
            }}
          >
            {kwargs.toggle_header ? kwargs.toggle_header : ""}
          </div>
          {toggle_views.length < 20 ? (
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "10px",
                padding: "10px",
                marginBottom: "10px",
                justifyContent: "center",
              }}
            >
              {toggle_views.map((view: string, index: number) => (
                <button
                  key={index}
                  style={{
                    background: viewId === index
                      ? "linear-gradient(135deg, #dcffdfff 0%, #f1ffefff 100%)"
                      : "#ffffff",
                    color: viewId === index ? "#2f4137ff" : "#4a5568",
                    border: viewId === index ? "none" : "2px solid #e2e8f0",
                    borderRadius: "22px",
                    fontWeight: viewId === index ? "700" : "600",
                    fontSize: "14px",
                    padding: "10px 20px",
                    boxShadow: viewId === index
                      ? "0 4px 15px rgba(102, 126, 234, 0.4)"
                      : "0 2px 4px rgba(0,0,0,0.08)",
                    transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
                    cursor: "pointer",
                    transform: viewId === index ? "translateY(-1px)" : "translateY(0)",
                    opacity: loading ? 0.6 : 1,
                    pointerEvents: loading ? "none" : "auto",
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
                  style={{
                    ...buttonStyle,
                    background: viewId === index
                      ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                      : "#ffffff",
                    color: viewId === index ? "white" : "#4a5568",
                    border: viewId === index ? "none" : "2px solid #e2e8f0",
                    borderRadius: "20px",
                    fontWeight: viewId === index ? "700" : "600",
                    boxShadow: viewId === index
                      ? "0 4px 15px rgba(102, 126, 234, 0.4)"
                      : "0 2px 4px rgba(0,0,0,0.08)",
                    transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
                    cursor: "pointer",
                    transform: viewId === index ? "translateY(-1px)" : "translateY(0)",
                    opacity: loading ? 0.6 : 1,
                    pointerEvents: loading ? "none" : "auto",
                  }}
                  onClick={() => {
                    setViewId(index);
                    setpreviousViewId(viewId);
                  }}
                  disabled={loading}
                  onMouseEnter={(e) => {
                    if (viewId !== index && !loading) {
                      e.currentTarget.style.boxShadow = "0 4px 8px rgba(0,0,0,0.12)";
                      e.currentTarget.style.transform = "translateY(-2px)";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (viewId !== index && !loading) {
                      e.currentTarget.style.boxShadow = "0 2px 4px rgba(0,0,0,0.08)";
                      e.currentTarget.style.transform = "translateY(0)";
                    }
                  }}
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





      {kwargs.api_ozz && (
        <div style={{
marginBottom: "5px",
display: "flex",
justifyContent: "flex-end",
        }}>
          <Ozz
            username={username}
            kwargs={kwargs}
            api={api}
            prod={prod}
            onSendMessage={async (msg, history) => {
              if (!kwargs.api_ozz) {
                return `🧪 Test Mode: You said "${msg}". Configure kwargs.api_ozz to connect to your backend.`;
              }

              try {
                const res = await axios.post(kwargs.api_ozz, {
                  message: msg,
                  conversation_history: history,
                  client_user: username,
                  prod: kwargs.prod,
                  api_key: kwargs.api_key,
                });
                return res.data.content;
              } catch (error: any) {
                console.error("Ozz API error:", error);
                return `⚠️ API Error: ${error.message || "Could not reach Pollen API"}. Test response for: "${msg}"`;
              }
            }}
          />
        </div>
      )}

      {/* ── Ticker Search Button ───────────────────────────────────────── */}
      {kwargs.show_ticker_search_btn && (
        <div style={{ marginBottom: "5px", display: "flex", justifyContent: "flex-start" }}>
          <button
            onClick={() => setTickerSearchModalShow(true)}
            style={{
              background: "linear-gradient(135deg, #1b4a1aff 0%, #0f3314ff 100%)",
              color: "#fff",
              border: "none",
              borderRadius: "8px",
              padding: "7px 16px",
              fontWeight: 700,
              fontSize: "0.88rem",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.18)",
              transition: "opacity 0.15s",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.opacity = "0.85")}
            onMouseLeave={(e) => (e.currentTarget.style.opacity = "1")}
            title="Search & add a ticker to your chessboard"
          >
            Search Edit Portfolio Board
          </button>
        </div>
      )}


<TickerSearchModal
  isOpen={tickerSearchModalShow}
  closeModal={() => setTickerSearchModalShow(false)}
  username={username}
  prod={prod}
  kwargs={kwargs}
  api={api}
  toastr={toastr}
  chessboard={kwargs.chessboard}  // ✅ Add this line
  ticker_buying_powers={kwargs.ticker_buying_powers}  // ✅ Add this line
  cash_position={kwargs.cash_position}
  accountInfo={kwargs.accountInfo}

/>


      <MyModal
        isOpen={modalShow}
        closeModal={() => setModalshow(false)}
        modalData={{
          ...modalData,
          index: index,        // ✅ Pass index
          gridRef: gridRef     // ✅ Pass grid reference
        }}
        promptText={promptText}
        setPromptText={setPromptText}
        toastr={toastr}
      />
      <div
        ref={gridContainerRef}
        style={{ flexDirection: "row", height: "100%", width: "100%" }}
        id="myGrid"
      >


        <div className="d-flex justify-content-between align-items-center">
          {!kwargs['api_ws'] && (refresh_sec == undefined || refresh_sec == 0) && (
            <div style={{ display: "flex" }}>
              <div style={{ margin: "5px 5px 5px 2px" }}>
                <button
                  className="btn"
                  style={{
                    backgroundColor: button_color,
                    color: "white",
                    padding: "2px 5px", // Smaller padding
                    // fontSize: "12px", // Smaller font size
                    borderRadius: "4px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    minWidth: "50px", // Ensure width stays the same during loading
                  }}
                  onClick={onRefresh}
                  title="Refresh"
                  disabled={loading} // Disable button while loading
                >
                  {loading ? (
                    <div
                      style={{
                        width: "12px",
                        height: "12px",
                        border: "2px solid white",
                        borderTop: "2px solid transparent",
                        borderRadius: "50%",
                        animation: "spin 0.8s linear infinite",
                      }}
                    />
                  ) : (
                    <span style={{ fontSize: "25px", lineHeight: "1" }}>⟳</span>
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
              {!props.autoUpdate && (
                <div style={{ margin: "5px 5px 5px 2px" }}>
                  <button
                    className="btn"
                    style={{
                      backgroundColor: "green",
                      color: "white",
                      padding: "5px 8px",
                      fontSize: "12px",
                      borderRadius: "4px",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                    }}
                    onClick={onUpdate}
                    title="Update"
                  >
                    <span style={{ fontSize: "18px", lineHeight: "1" }}>↑</span>
                  </button>
                </div>
              )}
            </div>
          )}

        </div>

        <div
          className={grid_options.theme || "ag-theme-alpine-dark"}
          style={{
            width: "100%",
            height: kwargs["grid_height"] ? kwargs["grid_height"] : "100%",
          }}
        >

{/* Column Sets — own wrapper */}
{kwargs.column_sets && (
  <div style={{
    display: "flex",
    flexDirection: "column",
    marginBottom: 4,
    // border: "1.5px solid #e5eff6ff",
    // borderRadius: "8px",
    background: "transparent", //"#f3f4f5ff",
    overflow: "hidden",
  }}>
    <div style={{ display: "flex", alignItems: "center", flexWrap: "nowrap", overflowX: "auto", padding: "4px 6px", gap: "0" }}>
      <button
        onClick={() => {
          setSelectedColumnSetKey(null);
          setTimeout(() => {
            const columnApi = gridRef.current?.columnApi;
            if (columnApi && initialColumnState) {
              columnApi.applyColumnState({ state: initialColumnState, applyOrder: true });
            }
          }, 0);
        }}
        style={{
          background: "rgba(225, 246, 221, 1)", color: "black",
          border: "1.5px solid rgb(180, 210, 180)", borderRadius: "5px",
          fontWeight: "bold", fontSize: "12px", padding: "3px 8px",
          flexShrink: 0, whiteSpace: "nowrap", cursor: "pointer", transition: "all 0.15s",
        }}
        onMouseEnter={(e) => { e.currentTarget.style.boxShadow = "0 3px 10px rgba(100,180,100,0.3)"; e.currentTarget.style.transform = "translateY(-1px)"; }}
        onMouseLeave={(e) => { e.currentTarget.style.boxShadow = "none"; e.currentTarget.style.transform = "translateY(0)"; }}
      >
        Reset View
      </button>

<div style={{ width: "1.5px", alignSelf: "stretch", background: "#c8dcccff", margin: "0 6px", flexShrink: 0 }} />
      {Object.keys(kwargs.column_sets).map(key => (
        <button
          key={key}
          onClick={() => {
            const newKey = selectedColumnSetKey === key ? null : key;
            setSelectedColumnSetKey(newKey);
            setTimeout(() => {
              const columnApi = gridRef.current?.columnApi;
              if (!newKey) {
                if (columnApi && initialColumnState) columnApi.applyColumnState({ state: initialColumnState, applyOrder: true });
              } else {
                const columnsToShow = kwargs.column_sets[newKey];
                if (columnApi && Array.isArray(grid_options.columnDefs)) {
                  grid_options.columnDefs.forEach((col: any) => columnApi.setColumnVisible(col.field, false));
                  columnsToShow.forEach((field: string, idx: number) => { columnApi.setColumnVisible(field, true); columnApi.moveColumn(field, idx); });
                }
              }
            }, 0);
          }}
          style={{
            background: selectedColumnSetKey === key ? "linear-gradient(135deg, #7cea66ff 0%, #4ba262ff 100%)" : "#ffffff",
            color: selectedColumnSetKey === key ? "white" : "#4a5568",
            border: selectedColumnSetKey === key ? "1.5px solid #3a9050" : "1.5px solid #8dc789ff",
            borderRadius: "12px", fontWeight: selectedColumnSetKey === key ? "700" : "500",
            fontSize: "12px", padding: "3px 9px", marginRight: "4px", flexShrink: 0, whiteSpace: "nowrap",
            boxShadow: selectedColumnSetKey === key ? "0 2px 8px rgba(75,162,98,0.35)" : "none",
            transition: "all 0.15s ease", cursor: "pointer",
            transform: selectedColumnSetKey === key ? "translateY(-1px)" : "translateY(0)",
          }}
          onMouseEnter={(e) => { if (selectedColumnSetKey !== key) { e.currentTarget.style.borderColor = "#8aa4b8"; e.currentTarget.style.boxShadow = "0 2px 6px rgba(0,0,0,0.1)"; e.currentTarget.style.transform = "translateY(-1px)"; } }}
          onMouseLeave={(e) => { if (selectedColumnSetKey !== key) { e.currentTarget.style.borderColor = "#c8d0d8"; e.currentTarget.style.boxShadow = "none"; e.currentTarget.style.transform = "translateY(0)"; } }}
        >
          {key}
        </button>
      ))}
    </div>
  </div>
)}

{/* Filter Buttons — own wrapper */}
{filterButtons.length > 0 && (
  <div style={{
    display: "flex",
    flexDirection: "column",
    marginBottom: 6,
    border: "1.5px solid #e5eff6ff",
    borderRadius: "8px",
    background: "#f5f8f6ff",
    overflow: "visible",
  }}>
    {filterButtons.map((col, rowIdx) => (
      <div key={col} style={{
        display: "flex", alignItems: "center", flexWrap: "wrap", rowGap: "4px",
        padding: "4px 6px",
        borderTop: rowIdx > 0 ? "1.5px solid #c8d4dc" : "none",
      }}>

        {/* Column label */}
        <span style={{ fontSize: "9px", color: "#8a9bb0", fontWeight: "600", flexShrink: 0, marginRight: "6px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
          {col}
        </span>
        <div style={{ width: "1.5px", alignSelf: "stretch", background: "#c8d4dc", margin: "0 6px 0 0", flexShrink: 0 }} />

        {/* Clear this row's filter */}
        {kwargs['show_clear_all_filters'] && (
          <>
            <button
              onClick={() => {
                handleButtonFilter(col, null);
                if (gridRef.current && gridRef.current.api) {
                  const model = gridRef.current.api.getFilterModel();
                  delete model[col];
                  gridRef.current.api.setFilterModel(model);
                }
              }}
              style={{
                background: "rgba(183, 136, 129, 1)", color: "white",
                border: "1.5px solid rgba(150, 80, 70, 1)", borderRadius: "5px",
                fontWeight: "bold", fontSize: "10px", padding: "3px 8px",
                flexShrink: 0, whiteSpace: "nowrap", cursor: "pointer", transition: "all 0.15s",
              }}
              onMouseEnter={(e) => { e.currentTarget.style.boxShadow = "0 3px 10px rgba(239,83,80,0.4)"; e.currentTarget.style.transform = "translateY(-1px)"; }}
              onMouseLeave={(e) => { e.currentTarget.style.boxShadow = "none"; e.currentTarget.style.transform = "translateY(0)"; }}
            >
              Clear
            </button>
            <div style={{ width: "1.5px", alignSelf: "stretch", background: "#c8d4dc", margin: "0 6px", flexShrink: 0 }} />
          </>
        )}

        {/* Filter value buttons for this column */}
        {getUniqueColumnValues(col, rowData).map(val => (
          <button
            key={val}
            onClick={() => handleButtonFilter(col, val)}
            style={{
              background: activeFilter[col] === val ? "linear-gradient(135deg, #7cea66ff 0%, #4ba262ff 100%)" : "#ffffff",
              color: activeFilter[col] === val ? "white" : "#4a5568",
              border: activeFilter[col] === val ? "1.5px solid #3a9050" : "1.5px solid #c8d0d8",
              borderRadius: "12px", fontWeight: activeFilter[col] === val ? "700" : "500",
              fontSize: "11px", padding: "3px 9px", marginRight: "4px", whiteSpace: "nowrap",
              boxShadow: activeFilter[col] === val ? "0 2px 8px rgba(75,162,98,0.35)" : "none",
              transition: "all 0.15s ease", cursor: "pointer",
              transform: activeFilter[col] === val ? "translateY(-1px)" : "translateY(0)",
            }}
            onMouseEnter={(e) => { if (activeFilter[col] !== val) { e.currentTarget.style.borderColor = "#8aa4b8"; e.currentTarget.style.boxShadow = "0 2px 6px rgba(0,0,0,0.1)"; e.currentTarget.style.transform = "translateY(-1px)"; } }}
            onMouseLeave={(e) => { if (activeFilter[col] !== val) { e.currentTarget.style.borderColor = "#c8d0d8"; e.currentTarget.style.boxShadow = "none"; e.currentTarget.style.transform = "translateY(0)"; } }}
          >
            {val}
          </button>
        ))}
      </div>
    ))}
  </div>
)}

        
          
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
                    animation: "scroll-left 40s linear infinite",
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


          <AgGridReact
            ref={gridRef}
            rowData={rowData}
            getRowStyle={getRowStyle}
            headerHeight={30}
            rowHeight={30}
            onGridReady={onGridReady}
            onFilterChanged={() => {
              // ✅ Recalculate subtotals when filters change
              if (gridRef.current?.api && kwargs.subtotal_cols?.length > 0) {
                calculateAndUpdateSubtotals(gridRef.current.api);
              }
            }}
            autoGroupColumnDef={autoGroupColumnDef}
            animateRows={true}
            suppressAggFuncInHeader={true}
            getRowId={getRowId}
            gridOptions={getGridOptions()}
            onCellValueChanged={onCellValueChanged}
            columnTypes={columnTypes}
            sideBar={grid_options.sideBar === false ? false : sideBar}
            onCellClicked={onCellClicked} // Attach the handler here
          />
        </div>
      </div>
    </>
  );
}

export default AgGrid

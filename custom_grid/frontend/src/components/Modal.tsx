import React, { useEffect, useRef } from "react";
import ReactModal from "react-modal";
import "./modal.css";
import axios from "axios";
import { utcToZonedTime, format } from 'date-fns-tz';
import moment from "moment";

const formats = ["YYYY-MM-DDTHH:mm", "MM/DD/YYYYTHH:mm", "MM/DD/YYYY HH:mm", "YYYY-MM-DD HH:mm"];
const sliderRules = ["buying_power", "borrow_power"]
const sliderRules_stars = ["Day", "Week", "Month", "Quarter", "Quarters", "Year"];
const sliderRules_stars_margin = sliderRules_stars.map(rule => `${rule} Margin`);



// const modalStyle = {
//   content: {
//     top: "50%",
//     left: "50%",
//     right: "auto",
//     bottom: "auto",
//     marginRight: "-50%",
//     transform: "translate(-50%, -50%)",
//     backgroundColor: "yellow",
//     width: "95vw",           // Responsive width
//     maxWidth: "400px",       // Limit max width for desktop
//     minWidth: "280px",       // Minimum for mobile
//     padding: "16px",
//   },
// };

ReactModal.setAppElement("#root");
let isExecuting = false;

interface MyModalProps {
  isOpen: boolean;
  closeModal: () => void;
  modalData: any;
  promptText: any;
  setPromptText: (value: any) => void;
  toastr: any; // Define the toastr type if available
}

const MyModal: React.FC<MyModalProps> = ({
  isOpen,
  closeModal,
  modalData,
  promptText,
  setPromptText,
  toastr,
}) => {
  const [loading, setLoading] = React.useState(false); // Add loading state
  const { prompt_field, prompt_order_rules, selectedRow, selectedField, add_symbol_row_info, display_grid_column } = modalData;
  // console.log("modalData :>> ", display_grid_column, prompt_field); // workerbee handle in agagrid display_grid_column add var from mount
  const [showStarsSliders, setShowStarsSliders] = React.useState(false);
  const [showStarsMarginSliders, setShowStarsMarginSliders] = React.useState(false);
  const [showActiveOrders, setShowActiveOrders] = React.useState(false);
  const [showWaveData, setShowWaveData] = React.useState(true);
  const [showButtonColData, setShowButtonColData] = React.useState(true);
  const [sellQtys, setSellQtys] = React.useState<{ [key: number]: string }>({});
  const handleSellQtyChange = (idx: number, value: string) => {
    setSellQtys((prev) => ({ ...prev, [idx]: value }));
  };


  const [editableValues, setEditableValues] = React.useState<{ [col: string]: { [idx: number]: any } }>({});
  const editableCols = modalData.editableCols || [];
  const ordersToRender = (selectedRow && display_grid_column && Array.isArray(selectedRow[display_grid_column]))
    ? selectedRow[display_grid_column]
    : [];
  const dataCols = ordersToRender.length > 0 ? Object.keys(ordersToRender[0]) : [];
  const editableColHeaders = editableCols.map((col: { col_header: string }) => col.col_header);
  const allCols = Array.from(new Set([...editableColHeaders, ...dataCols]));

  const ref = useRef<HTMLButtonElement>(null);
  const selectRef = useRef<HTMLSelectElement>(null);



  const handleOkSecond = async () => {
    if (isExecuting) return;
    if (loading) return; // Prevent multiple clicks
    setLoading(true); // Show spinner
    isExecuting = true;
    try {
      // Merge editable values into each order
      const ordersToRender = display_grid_column && selectedRow && Array.isArray(selectedRow[display_grid_column])
        ? selectedRow[display_grid_column]
        : [];

      if (!ordersToRender || !Array.isArray(ordersToRender)) {
        toastr.error("No editable orders found for this action.");
        return;
      }

      const ordersWithEdits = ordersToRender.map((order: any, idx: number) => {
        let edits: any = {};
        editableCols.forEach((col: { col_header: string }) => {
          edits[col.col_header] = editableValues[col.col_header]?.[idx] ?? order[col.col_header] ?? ""; // Use nullish coalescing
        });
        return { ...order, ...edits };
      });


      const body = {
        username: modalData.username,
        prod: modalData.prod,
        selected_row: modalData.selectedRow,
        default_value: promptText,
        editable_orders: ordersWithEdits,
        ...modalData.kwargs,
      };
      const { data: res } = await axios.post(modalData.button_api, body);
      const { status, data, description } = res;
      if (status === "success") {
        if (data && data.message_type === "fade") {
          toastr.success(description, "Success");
        } else {
          alert("Success!\nDescription: " + description);
        }
      } else {
        if (data && data.message_type === "fade") {
          toastr.error(description, "Error");
        } else {
          alert("Error!\nDescription: " + description);
        }
      }
      if (data?.close_modal !== false) closeModal();
    } catch (error: any) {
      console.log("error :>> ", error);
      toastr.error(error.message);
    }
    setLoading(false); // Hide spinner
    isExecuting = false;
  };


  useEffect(() => {
    if (isOpen) setTimeout(() => ref.current?.focus(), 100);
  }, [isOpen]);

  useEffect(() => {
    setSellQtys({}); // Reset sellQtys to an empty object
  }, [isOpen, selectedRow]);


  useEffect(() => {
    if (!isOpen) {
      setEditableValues({});
      return;
    }

    console.log("🔄 Modal opening - fetching fresh data from grid");

    // ✅ Get fresh data directly from AG Grid
    const gridRef = modalData.gridRef;
    const index = modalData.index;
    const selectedRowFromModal = modalData.selectedRow; // ✅ Use modalData.selectedRow, not props
    const selectedRowId = selectedRowFromModal?.[index];

    if (!gridRef?.current?.api || !selectedRowId) {
      console.warn("⚠️  Missing gridRef or selectedRowId", {
        hasGridRef: !!gridRef?.current?.api,
        hasIndex: !!index,
        hasSelectedRow: !!selectedRowFromModal,
        selectedRowId
      });
      return;
    }

    // ✅ ALWAYS get the latest data from grid when modal opens
    const freshNode = gridRef.current.api.getRowNode(selectedRowId);

    if (!freshNode || !freshNode.data) {
      console.warn("⚠️  Row not found in grid:", selectedRowId);
      return;
    }

    const freshData = freshNode.data;
    const orders = freshData[display_grid_column];

    if (!Array.isArray(orders) || !editableCols) {
      console.warn("⚠️  Invalid orders data", {
        hasOrders: !!orders,
        isArray: Array.isArray(orders),
        hasEditableCols: !!editableCols,
        displayColumn: display_grid_column
      });
      setEditableValues({});
      return;
    }

    console.log("✅ Building editableValues from FRESH grid data:", {
      rowId: selectedRowId,
      orderCount: orders.length,
      firstOrderTakeProfit: orders[0]?.take_profit,
      allOrders: orders
    });

    // ✅ Build editableValues from fresh data
    const reset: any = {};
    editableCols.forEach(({ col_header }: { col_header: string }) => {
      reset[col_header] = {};
      orders.forEach((order: any, idx: number) => {
        reset[col_header][idx] = order[col_header] ?? "";
      });
    });

    console.log("✅ Setting editableValues:", reset);
    setEditableValues(reset);

    // ✅ Only depend on isOpen - refresh EVERY time modal opens
  }, [isOpen]);

  const isValidDate = (dateStr: string) => {
    return formats.some(format => moment(dateStr, format, true).isValid());
  };

  const formatToLocalDatetime = (dateStr: string) => {
    const date = moment(dateStr, formats, true).toDate();
    const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const zonedDate = utcToZonedTime(date, timeZone);
    return format(zonedDate, 'yyyy-MM-dd\'T\'HH:mm');
  };

  // Categorize fields by type
  const textFields = [];
  const booleanFields = [];
  const datetimeFields = [];
  const arrayFields = [];

  const filtered_prompt_order_rules = Array.isArray(prompt_order_rules) && promptText
    ? prompt_order_rules.filter((field) => field && (field in promptText))
    : [];

  if (prompt_order_rules) {
    for (const rule of prompt_order_rules) {
      const value = promptText[rule];
      if (Array.isArray(value)) {
        arrayFields.push(rule);
      } else if (typeof value === "boolean") {
        booleanFields.push(rule);
      } else if (isValidDate(value)) {
        datetimeFields.push(rule);
      } else {
        textFields.push(rule);
      }
    }
  }



  return (
    <ReactModal
      isOpen={isOpen}
      onRequestClose={closeModal}
      // style={modalStyle}
      ariaHideApp={false}
    >
      <div className="my-modal-content">
        {/* Modal Header */}
        <div className="modal-header px-3 d-flex justify-content-center align-items-center" style={{ position: "relative" }}>
          <h4 className="text-center m-0">{modalData.prompt_message}</h4>
          <span className="close" onClick={closeModal} style={{ position: "absolute", right: "20px" }}>
            &times;
          </span>

        </div>

        {/* Modal Body */}
        <div className="modal-body p-3">
          <div className="d-flex flex-column">
            {/* Boolean Fields Top Row */}
            {booleanFields.length > 0 && (
              <div
                className="d-flex flex-row justify-content-between mb-2"
                style={{
                  border: "1px solid #e0e0e0", // Light gray outline
                  borderRadius: "8px",
                  padding: "8px",
                  background: "#fafcff"
                }}
              >
                {booleanFields.map((rule: any, index: number) => (
                  <div className="d-flex flex-column align-items-center" key={index} style={{ marginRight: "8px" }}>
                    <label className="mb-0" style={{ minWidth: "100px", textAlign: "center", fontSize: "0.9rem" }}>
                      {rule}:
                    </label>
                    <input
                      type="checkbox"
                      checked={promptText[rule]}
                      onChange={(e) =>
                        setPromptText({
                          ...promptText,
                          [rule]: e.target.checked,
                        })
                      }
                      style={{ width: "16px", height: "16px", marginTop: "4px" }}
                    />
                  </div>
                ))}
              </div>
            )}

            {/* Add Symbol Row Info Column */}
            {add_symbol_row_info && Array.isArray(add_symbol_row_info) && (
              <div
                className="d-flex flex-wrap"
                style={{
                  flex: 1,
                  border: "1px solid #e0e0e0",
                  borderRadius: "8px",
                  padding: "8px",
                  background: "#fafcff",
                  marginBottom: "8px"
                }}
              >
                {add_symbol_row_info.map((col: string, idx: number) =>
                  selectedRow && selectedRow[col] !== undefined && (
                    <div
                      key={col}
                      style={{
                        flex: "1 1 30%",
                        minWidth: "120px",
                        marginBottom: "8px",
                        paddingRight: "12px"
                      }}
                    >
                      <b>{col}: </b>
                      {typeof selectedRow[col] === "number"
                        ? Number(selectedRow[col]).toLocaleString(undefined, { maximumFractionDigits: 2 })
                        : String(selectedRow[col])}
                    </div>
                  )
                )}
              </div>
            )}

            {/* Other Fields (Text, Datetime, Array Fields) */}
            <div className="d-flex flex-wrap" style={{ gap: "16px", marginBottom: "16px" }}>
              {/* Text Fields */}
              {textFields.length > 0 &&
                textFields.map((rule: any, index: number) => {
                  if (sliderRules_stars.includes(rule) || sliderRules_stars_margin.includes(rule)) return null;
                  const isSliderRule = sliderRules.includes(rule);

                  return (
                    <div
                      key={index}
                      className="d-flex flex-column"
                      style={{
                        flex: "1 1 calc(50% - 16px)", // Two columns per row
                        minWidth: "150px",
                      }}
                    >
                      <label
                        className="mb-1"
                        style={{
                          fontSize: "0.85rem",
                          fontWeight: "bold",
                          textTransform: "capitalize",
                        }}
                      >
                        {rule.replace(/_/g, " ")}:
                        {rule === "sell_amount" && (
                          <span
                            style={{ marginLeft: "4px", cursor: "pointer" }}
                            title="This amount will override sell_qty"
                          >
                            ❓
                          </span>
                        )}
                      </label>

                      {isSliderRule ? (
                        <>
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step=".01"
                            value={promptText[rule] || 0}
                            onChange={(e) =>
                              setPromptText({
                                ...promptText,
                                [rule]: Number(e.target.value),
                              })
                            }
                            style={{ width: "100%" }}
                          />
                          <span style={{ fontSize: "0.85rem", fontWeight: "bold", marginTop: "4px" }}>
                            {promptText[rule] || 0}
                          </span>
                        </>
                      ) : (
                        <input
                          type="text"
                          value={promptText[rule]}
                          onChange={(e) =>
                            setPromptText({
                              ...promptText,
                              [rule]: e.target.value,
                            })
                          }
                          style={{
                            width: "100%",
                            padding: "6px",
                            fontSize: "0.85rem",
                            border: "1px solid #ccc",
                            borderRadius: "4px",
                          }}
                        />
                      )}
                    </div>
                  );
                })}

              {/* Array Fields */}
              {arrayFields.length > 0 &&
                arrayFields.map((rule: any, index: number) => (
                  <div
                    key={index}
                    className="d-flex flex-column"
                    style={{
                      flex: "1 1 calc(50% - 16px)", // Two columns per row
                      minWidth: "150px",
                    }}
                  >
                    <label
                      className="mb-1"
                      style={{
                        fontSize: "0.85rem",
                        fontWeight: "bold",
                        textTransform: "capitalize",
                      }}
                    >
                      {rule.replace(/_/g, " ")}:
                    </label>
                    <select
                      value={promptText[rule][0]}
                      onChange={(e) =>
                        setPromptText({
                          ...promptText,
                          [rule]: [e.target.value],
                        })
                      }
                      style={{
                        width: "100%",
                        padding: "6px",
                        fontSize: "0.85rem",
                        border: "1px solid #ccc",
                        borderRadius: "4px",
                      }}
                    >
                      {promptText[rule].map((item: any, i: number) => (
                        <option key={i} value={item}>
                          {item}
                        </option>
                      ))}
                    </select>
                  </div>
                ))}

              {/* Datetime Fields */}
              {datetimeFields.length > 0 &&
                datetimeFields.map((rule: any, index: number) => (
                  <div
                    key={index}
                    className="d-flex flex-column"
                    style={{
                      flex: "1 1 calc(50% - 16px)", // Two columns per row
                      minWidth: "150px",
                    }}
                  >
                    <label
                      className="mb-1"
                      style={{
                        fontSize: "0.85rem",
                        fontWeight: "bold",
                        textTransform: "capitalize",
                      }}
                    >
                      {rule.replace(/_/g, " ")}:
                    </label>
                    <input
                      type="datetime-local"
                      value={promptText[rule] && formatToLocalDatetime(promptText[rule])}
                      onChange={(e) =>
                        setPromptText({
                          ...promptText,
                          [rule]: e.target.value,
                        })
                      }
                      style={{
                        width: "100%",
                        padding: "6px",
                        fontSize: "0.85rem",
                        border: "1px solid #ccc",
                        borderRadius: "4px",
                      }}
                    />
                  </div>
                ))}

              {/* Expander for sliderRules_stars */}
              {sliderRules_stars.some((rule: any) => prompt_order_rules?.includes(rule)) && (
                <div style={{ flex: "1 1 100%", marginTop: "16px" }}>
                  <div
                    style={{ cursor: "pointer", fontWeight: "bold", marginBottom: "4px" }}
                    onClick={() => setShowStarsSliders((prev) => !prev)}
                  >
                    {showStarsSliders ? "▼" : "►"} Advanced Allocation Options
                  </div>
                  {showStarsSliders && (
                    <div className="d-flex flex-wrap" style={{ gap: "16px" }}>
                      {sliderRules_stars.map((rule: any, index: number) =>
                        prompt_order_rules?.includes(rule) && promptText[rule] !== undefined && (
                          <div
                            key={index}
                            className="d-flex flex-column"
                            style={{
                              flex: "1 1 calc(50% - 16px)", // Two columns per row
                              minWidth: "150px",
                            }}
                          >
                            <label
                              className="mb-1"
                              style={{
                                fontSize: "0.85rem",
                                fontWeight: "bold",
                                textTransform: "capitalize",
                              }}
                            >
                              {rule.replace(/_/g, " ")}:
                            </label>
                            <input
                              type="range"
                              min="0"
                              max="1"
                              step=".01"
                              value={promptText[rule] || 0}
                              onChange={(e) =>
                                setPromptText({
                                  ...promptText,
                                  [rule]: Number(e.target.value),
                                })
                              }
                              style={{ width: "100%" }}
                            />
                            <span style={{ fontSize: "0.85rem", fontWeight: "bold", marginTop: "4px" }}>
                              {promptText[rule] || 0}
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Expander for sliderRules_stars_margin */}
              {sliderRules_stars_margin.some((rule: any) => prompt_order_rules?.includes(rule)) && (
                <div style={{ flex: "1 1 100%", marginTop: "16px" }}>
                  <div
                    style={{ cursor: "pointer", fontWeight: "bold", marginBottom: "4px" }}
                    onClick={() => setShowStarsMarginSliders((prev) => !prev)}
                  >
                    {showStarsMarginSliders ? "▼" : "►"} Advanced Margin Allocation Options
                  </div>
                  {showStarsMarginSliders && (
                    <div className="d-flex flex-wrap" style={{ gap: "16px" }}>
                      {sliderRules_stars_margin.map((rule: any, index: number) =>
                        prompt_order_rules?.includes(rule) && promptText[rule] !== undefined && (
                          <div
                            key={index}
                            className="d-flex flex-column"
                            style={{
                              flex: "1 1 calc(50% - 16px)", // Two columns per row
                              minWidth: "150px",
                            }}
                          >
                            <label
                              className="mb-1"
                              style={{
                                fontSize: "0.85rem",
                                fontWeight: "bold",
                                textTransform: "capitalize",
                              }}
                            >
                              {rule.replace(/_/g, " ")}:
                            </label>
                            <input
                              type="range"
                              min="0"
                              max="1"
                              step=".01"
                              value={promptText[rule] || 0}
                              onChange={(e) =>
                                setPromptText({
                                  ...promptText,
                                  [rule]: Number(e.target.value),
                                })
                              }
                              style={{ width: "100%" }}
                            />
                            <span style={{ fontSize: "0.85rem", fontWeight: "bold", marginTop: "4px" }}>
                              {promptText[rule] || 0}
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Display Grid Column Table */}
            {display_grid_column &&
              selectedRow &&
              Array.isArray(selectedRow[display_grid_column]) &&
              selectedRow[display_grid_column].length > 0 && (
                <div style={{ margin: "16px 0" }}>
                  <div
                    style={{ cursor: "pointer", fontWeight: "bold", marginBottom: "4px" }}
                    onClick={() => setShowButtonColData((prev: boolean) => !prev)}
                  >
                    <span style={{ marginRight: "8px" }}>
                      {showButtonColData ? "▼" : "►"}
                    </span>
                    <button
                      type="button"
                      className="btn btn-link p-0"
                      style={{ fontWeight: "bold", textDecoration: "underline", color: "#007bff", background: "none", border: "none", cursor: "pointer" }}
                      onClick={() => setShowButtonColData((prev: boolean) => !prev)}
                    >
                      {display_grid_column}
                    </button>
                  </div>
                  {showButtonColData && (() => {
                    const ordersToRender = selectedRow[display_grid_column];
                    return (
                      <div style={{ overflowX: "auto" }}>
                        <table className="table table-bordered table-sm" style={{ fontSize: "0.6rem" }}>
                          <thead>
                            <tr>
                              {allCols.map((col) => {
                                const editableCol = editableCols.find(
                                  (ec: { col_header: string }) => ec.col_header === col
                                );

                                return (
                                  <th
                                    key={col}
                                    style={{
                                      whiteSpace: "normal",
                                      wordWrap: "break-word",
                                      backgroundColor: "#fafcff", // Light background
                                      color: "black", // Black text
                                      textAlign: "center", // Center align text
                                    }}
                                  >
                                    <div style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
                                      {/* Use display_name if available, otherwise fallback to col */}
                                      {editableCol?.display_name || col.replace(/_/g, " ")}
                                      {editableCol?.info && (
                                        <span
                                          style={{
                                            marginLeft: "4px",
                                            cursor: "pointer",
                                            color: "#007bff",
                                            fontSize: "0.8rem",
                                          }}
                                          title={editableCol.info} // Tooltip text from the "info" key
                                        >
                                          ❓
                                        </span>
                                      )}
                                    </div>
                                  </th>
                                );
                              })}
                            </tr>
                          </thead>
                          <tbody>
                            {ordersToRender.map((order: any, idx: number) => (
                              <tr key={idx}>
                                {allCols.map((col) => {
                                  const editableCol = editableCols.find((ec: { col_header: string; }) => ec.col_header === col);
                                  // WORKERBEE Create func to handle column logic / updates sell qty ex below
                                  if (col === "sell_qty") {
                                    // Handle sell_qty column logic
                                    return (
                                      <td key={col}>
                                        <input
                                          type="number"
                                          min={0}
                                          max={order.qty_available} // Limit to qty_available
                                          value={editableValues[col]?.[idx] || ""}
                                          onChange={(e) => {
                                            let value = e.target.value;
                                            if (value === "") {
                                              setEditableValues((prev) => ({
                                                ...prev,
                                                [col]: { ...prev[col], [idx]: "" },
                                              }));
                                              return;
                                            }
                                            let num = Number(value);
                                            if (num < 0) num = 0; // Ensure no negative values
                                            if (
                                              order.qty_available !== undefined &&
                                              num > order.qty_available
                                            )
                                              num = order.qty_available; // Limit to max qty_available

                                            setEditableValues((prev) => ({
                                              ...prev,
                                              [col]: { ...prev[col], [idx]: num },
                                            }));

                                            // Update the promptText with the updated sell_qty
                                            const updatedOrders = ordersToRender.map(
                                              (ord: any, i: number) => ({
                                                ...ord,
                                                sell_qty:
                                                  i === idx
                                                    ? String(num)
                                                    : editableValues[col]?.[i] || "",
                                              })
                                            );
                                            setPromptText({
                                              ...promptText,
                                              active_orders_with_qty: updatedOrders,
                                            });
                                          }}
                                          style={{ width: "80px", fontSize: "0.8rem" }}
                                        />
                                      </td>
                                    );
                                  } else if (editableCol) {

                                    if (editableCol.dtype === "list") {
                                      // Render dropdown for dtype: "list"
                                      const options = editableCol.values || []; // Use editable dictionary for dropdown options
                                      return (
                                        <td key={col}>
                                          <select
                                            value={editableValues[col]?.[idx] || ""}
                                            onChange={(e) => {
                                              const value = e.target.value;
                                              setEditableValues((prev) => ({
                                                ...prev,
                                                [col]: { ...prev[col], [idx]: value },
                                              }));
                                            }}
                                            style={{ width: "100%", fontSize: "0.8rem", padding: "4px", minWidth: "80px", }}
                                          >
                                            <option value="" disabled>
                                              Select...
                                            </option>
                                            {options.map((option: string, i: number) => (
                                              <option key={i} value={option}>
                                                {option}
                                              </option>
                                            ))}
                                          </select>
                                        </td>
                                      );
                                    }


                                    // Render input for editable column
                                    else if (editableCol.dtype === "checkbox") {
                                      return (
                                        <td key={col}>
                                          <input
                                            type="checkbox"
                                            checked={!!editableValues[col]?.[idx]}
                                            onChange={e => {
                                              const value = e.target.checked;
                                              setEditableValues(prev => ({
                                                ...prev,
                                                [col]: { ...prev[col], [idx]: value }
                                              }));
                                            }}
                                          />
                                        </td>
                                      );
                                    } else if (editableCol.dtype === "number") {
                                      return (
                                        <td key={col}>
                                          <input
                                            type="number"
                                            value={editableValues[col]?.[idx] || ""}
                                            onChange={e => {
                                              const value = e.target.value;
                                              setEditableValues(prev => ({
                                                ...prev,
                                                [col]: { ...prev[col], [idx]: value }
                                              }));
                                            }}
                                            style={{ width: "80px", fontSize: "0.8rem" }}
                                          />
                                        </td>
                                      );
                                    } else if (editableCol.dtype === "datetime") {
                                      return (
                                        <td key={col}>
                                          <input
                                            type="datetime-local"
                                            value={editableValues[col]?.[idx] || ""}
                                            onChange={e => {
                                              const value = e.target.value;
                                              setEditableValues(prev => ({
                                                ...prev,
                                                [col]: { ...prev[col], [idx]: value }
                                              }));
                                            }}
                                            style={{ width: "140px", fontSize: "0.8rem" }}
                                          />
                                        </td>
                                      );
                                    } else {
                                      // text
                                      return (
                                        <td key={col}>
                                          <input
                                            type="text"
                                            value={editableValues[col]?.[idx] || ""}
                                            onChange={e => {
                                              const value = e.target.value;
                                              setEditableValues(prev => ({
                                                ...prev,
                                                [col]: { ...prev[col], [idx]: value }
                                              }));
                                            }}
                                            style={{ width: "80px", fontSize: "0.8rem" }}
                                          />
                                        </td>
                                      );
                                    }
                                  } else {
                                    // Render plain text for non-editable columns
                                    return (
                                      <td key={col}>
                                        {order && order[col] !== undefined
                                          ? typeof order[col] === "number"
                                            ? Number(order[col]).toLocaleString(undefined, { maximumFractionDigits: 2 })
                                            : String(order[col])
                                          : ""}
                                      </td>
                                    );
                                  }
                                })}
                              </tr>
                            ))}
                          </tbody>
                          <tfoot>
                            <tr>
                              {allCols.map((col) => {
                                try {
                                  // Only sum numeric columns
                                  const sum = ordersToRender.reduce((acc: number, order: any) => {
                                    const val = order[col];
                                    return typeof val === "number" && !isNaN(val) ? acc + val : acc;
                                  }, 0);
                                  // Show subtotal only if at least one value was numeric
                                  const hasNumeric = ordersToRender.some((order: any) => typeof order[col] === "number" && !isNaN(order[col]));
                                  return (
                                    <td key={col} style={{ fontWeight: "bold", background: "#f7f7f7" }}>
                                      {hasNumeric ? sum.toLocaleString(undefined, { maximumFractionDigits: 2 }) : ""}
                                    </td>
                                  );
                                } catch (e) {
                                  return <td key={col}></td>;
                                }
                              })}
                            </tr>
                          </tfoot>
                        </table>
                      </div>
                    );
                  })()}
                </div>
              )}
          </div>
        </div>


        {/* Modal Footer */}
        <div className="modal-footer d-flex justify-content-center" style={{ position: "sticky", bottom: 0, }}>
          <button type="button" className="btn btn-primary mx-2"
            onClick={handleOkSecond}
            ref={ref}>
            {loading ? (
              <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            ) : (
              "Ok"
            )}
          </button>
          <button type="button" className="btn btn-secondary mx-2" onClick={closeModal}>
            Cancel
          </button>
        </div>
      </div>
    </ReactModal>
  );

};

export default MyModal;

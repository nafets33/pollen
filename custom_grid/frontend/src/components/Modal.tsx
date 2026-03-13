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


// 12-step gradients for green and red
const greenGradient = [
  "#f1f8e9", "#e6f9e9", "#d0f5d6", "#c8e6c9", "#bff0c7", "#a5d6a7",
  "#80df97", "#81c784", "#4caf50", "#43a047", "#388e3c", "#1b5e20"
];
const redGradient = [
  "#ffebee", "#fdecec", "#ffcdd2", "#f8c6c6", "#ef9a9a", "#f09494",
  "#e57373", "#f44336", "#e06363", "#c62828", "#b71c1c", "#c23d3d"
];

function getTrinityColor(val: number) {
  // Clamp between -100 and 100, but max color at 75
  const capped = Math.max(-75, Math.min(75, val));
  const arr = capped >= 0 ? greenGradient : redGradient;
  // Map -75..75 to 0..11
  const idx = Math.round(Math.abs(capped) / 75 * (arr.length - 1));
  return arr[idx];
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
  const { prompt_field, prompt_order_rules, selectedRow, selectedField, add_symbol_row_info } = modalData;

  // console.log("modalData :>> ", activeDisplayColumn, prompt_field); // workerbee handle in agagrid activeDisplayColumn add var from mount
  const [showStarsSliders, setShowStarsSliders] = React.useState(false);
  const [showStarsMarginSliders, setShowStarsMarginSliders] = React.useState(false);

  const [showButtonColData, setShowButtonColData] = React.useState(true);
  const [sellQtys, setSellQtys] = React.useState<{ [key: number]: string }>({});
  const handleSellQtyChange = (idx: number, value: string) => {
    setSellQtys((prev) => ({ ...prev, [idx]: value }));
  };



  const [editableValues, setEditableValues] = React.useState<{ [col: string]: { [idx: number]: any } }>({});
  const [selectedDisplayColumn, setSelectedDisplayColumn] = React.useState<string>("");

  // ✅ Memoize to prevent new array on every render
  const editableColsDict = React.useMemo(() => modalData.editableCols || {}, [modalData.editableCols]);
  const displayColumnOptions = React.useMemo(() => Object.keys(editableColsDict), [editableColsDict]);

  // ✅ Use selected column or first available key
  const activeDisplayColumn = selectedDisplayColumn || displayColumnOptions[0] || "";

  // ✅ Get editableCols for the active column
  const editableCols = React.useMemo(() => editableColsDict[activeDisplayColumn] || [], [editableColsDict, activeDisplayColumn]);

  const ordersToRender = React.useMemo(() =>
    (selectedRow && activeDisplayColumn && Array.isArray(selectedRow[activeDisplayColumn]))
      ? selectedRow[activeDisplayColumn]
      : []
    , [selectedRow, activeDisplayColumn]);

  const dataCols = React.useMemo(
    () => ordersToRender.length > 0 ? Object.keys(ordersToRender[0]) : [],
    [ordersToRender]
  );
  const editableColHeaders = React.useMemo(
    () => editableCols.map((col: { col_header: string }) => col.col_header),
    [editableCols]
  );
  const allCols = React.useMemo(
    () => Array.from(new Set([...editableColHeaders, ...dataCols])),
    [editableColHeaders, dataCols]
  );

  const ref = useRef<HTMLButtonElement>(null);
  // const selectRef = useRef<HTMLSelectElement>(null);



  const handleOkSecond = async () => {
    if (isExecuting) return;
    if (loading) return; // Prevent multiple clicks
    setLoading(true); // Show spinner
    isExecuting = true;
    try {
      // Merge editable values into each order
      const ordersToRender = activeDisplayColumn && selectedRow && Array.isArray(selectedRow[activeDisplayColumn])
        ? selectedRow[activeDisplayColumn]
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
        selected_data_type: activeDisplayColumn,
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
      setSelectedDisplayColumn("");
      return;
    }

    if (!modalData.editableCols || Object.keys(modalData.editableCols).length === 0) {
      console.warn("⚠️ editableCols not ready yet");
      return;
    }

    if (displayColumnOptions.length > 0 && !selectedDisplayColumn) {
      setSelectedDisplayColumn(displayColumnOptions[0]);
    }

    if (!activeDisplayColumn) {
      console.warn("⚠️ No active display column");
      return;
    }

    // ✅ selectedRow is already fresh — was fetched from grid in Aggrid.tsx before setModalData
    const orders = selectedRow?.[activeDisplayColumn];

    if (!Array.isArray(orders) || editableCols.length === 0) {
      console.warn("⚠️ Invalid orders data", {
        hasOrders: !!orders,
        isArray: Array.isArray(orders),
        hasEditableCols: editableCols.length > 0,
        displayColumn: activeDisplayColumn,
      });
      setEditableValues({});
      return;
    }

    const reset: any = {};
    editableCols.forEach(({ col_header }: { col_header: string }) => {
      reset[col_header] = {};
      orders.forEach((order: any, idx: number) => {
        reset[col_header][idx] = order[col_header] ?? "";
      });
    });

    setEditableValues(reset);

  }, [isOpen, activeDisplayColumn]);

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
      style={{
        overlay: {
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'rgba(0, 0, 0, 0.4)',
          zIndex: 1000,
        },
        content: {
          overflow: 'visible',
          padding: 0,
          inset: 'auto',
          position: 'relative',
          border: 'none',
          background: 'transparent',
        }
      }}
      ariaHideApp={false}
    >
      <div className="my-modal-content">
        {/* Modal Header */}
        <div className="modal-header px-3 d-flex justify-content-center align-items-center" style={{ position: "relative" }}>
          <h4 className="text-center m-0">
            {Object.keys(selectedRow || {}).some(col => col.toLowerCase().includes("symbol")) && selectedRow?.symbol && (
              <span style={{ color: "#2f8d24ff", marginRight: 8 }}>{selectedRow.symbol} {": "}</span>
            )}
            {modalData.prompt_message}
          </h4>
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



            {/* Display Grid Column Toggle & Table */}
            {displayColumnOptions.length > 0 && (
              <div style={{ marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                <label style={{ fontWeight: "bold", fontSize: "0.9rem", marginRight: "4px" }}>
                  {/* Select Data: */}
                </label>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                  {displayColumnOptions.map((col: string) => {
                    const isActive = (selectedDisplayColumn || displayColumnOptions[0]) === col;
                    return (
                      <button
                        key={col}
                        type="button"
                        onClick={() => setSelectedDisplayColumn(col)}
                        style={{
                          padding: "5px 14px",
                          fontSize: "0.85rem",
                          fontWeight: isActive ? "bold" : "normal",
                          border: `2px solid ${isActive ? "#007bff" : "#ccc"}`,
                          borderRadius: "20px",
                          background: isActive ? "#007bff" : "#fff",
                          color: isActive ? "#fff" : "#555",
                          cursor: "pointer",
                          transition: "all 0.15s ease",
                          whiteSpace: "nowrap",
                        }}
                      >
                        {col.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {/* ✅ UPDATED: Check activeDisplayColumn instead of activeDisplayColumn */}
            {selectedRow &&
              Array.isArray(selectedRow[activeDisplayColumn]) &&
              selectedRow[activeDisplayColumn].length > 0 && (
                <div>
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
                      {/* {activeDisplayColumn} ({selectedRow[activeDisplayColumn].length} rows) */}
                    </button>
                  </div>

                  {showButtonColData && (() => {
                    // const ordersToRender = selectedRow[activeDisplayColumn];

                    // Helper function to calculate cumulative left position for pinned columns
                    const getPinnedColumnLeftPosition = (colIndex: number): number => {
                      let leftOffset = 0;
                      for (let i = 0; i < colIndex; i++) {
                        const col = allCols[i];
                        const editableCol = editableCols.find((ec: { col_header: string }) => ec.col_header === col);
                        if (editableCol?.pinned) {
                          // Use the column's width or default based on input type
                          const colWidth = editableCol.width || (editableCol.dtype === "datetime" ? 140 : 100);
                          leftOffset += colWidth;
                        }
                      }
                      return leftOffset;
                    };

                    // Helper function for conditional coloring
                    const getCellBackgroundColor = (col: string, idx: number, order: any) => {
                      const editableCol = editableCols.find((ec: { col_header: string }) => ec.col_header === col);
                      if (!editableCol) return "white";

                      if (editableCol.backgroundColor) {
                        return editableCol.backgroundColor;
                      }

                      if (editableCol.conditionalColor) {
                        const cond = editableCol.conditionalColor;
                        const cellValue = editableValues[col]?.[idx] ?? order[col];
                        const compareValue = cond.compare_to ? order[cond.compare_to] : cond.value;

                        // Handle 'in' operator for checking if value is in a list
                        if (cond.operator === "in") {
                          const valueList = Array.isArray(compareValue) ? compareValue : [compareValue];
                          return valueList.includes(cellValue) ? cond.trueColor : cond.falseColor;
                        }

                        // ✅ Handle '!in' operator (not in list)
                        if (cond.operator === "!in") {
                          const valueList = Array.isArray(compareValue) ? compareValue : [compareValue];
                          return !valueList.includes(cellValue) ? cond.trueColor : cond.falseColor;
                        }

                        // Existing string operations
                        if (cond.operator === "contains") {
                          return String(cellValue).toLowerCase().includes(String(compareValue).toLowerCase())
                            ? cond.trueColor : cond.falseColor;
                        }

                        if (cond.operator === "!contains") {
                          return !String(cellValue).toLowerCase().includes(String(compareValue).toLowerCase())
                            ? cond.trueColor : cond.falseColor;
                        }
                        if (cond.operator === "startsWith") {
                          return String(cellValue).toLowerCase().startsWith(String(compareValue).toLowerCase())
                            ? cond.trueColor : cond.falseColor;
                        }

                        // Existing numeric comparisons
                        if (cond.operator === ">=" && cellValue >= compareValue) return cond.trueColor;
                        if (cond.operator === ">" && cellValue > compareValue) return cond.trueColor;
                        if (cond.operator === "<" && cellValue < compareValue) return cond.trueColor;
                        if (cond.operator === "<=" && cellValue <= compareValue) return cond.trueColor;
                        if (cond.operator === "==" && cellValue == compareValue) return cond.trueColor;
                        return cond.falseColor;
                      }

                      return "white";
                    };

                    return (
                      <div style={{
                        maxHeight: "400px",
                        overflowY: "auto",
                        overflowX: "auto",
                        border: "1px solid #ddd",
                      }}>
                        <table className="table table-bordered table-sm" style={{ fontSize: "0.6rem" }}>
                          <thead>
                            <tr>
                              {allCols.map((col, colIndex) => {
                                const editableCol = editableCols.find(
                                  (ec: { col_header: string }) => ec.col_header === col
                                );
                                const colWidth = editableCol?.width || (editableCol?.dtype === "datetime" ? 140 : 100);

                                return (
                                  <th
                                    key={col}
                                    style={{
                                      whiteSpace: "normal",
                                      wordWrap: "break-word",
                                      backgroundColor: editableCol?.backgroundColor || "#fafcff",
                                      color: "black",
                                      textAlign: "center",
                                      position: "sticky",
                                      top: -1,
                                      paddingTop: "1px",
                                      left: editableCol?.pinned ? `${getPinnedColumnLeftPosition(colIndex)}px` : "auto",
                                      zIndex: editableCol?.pinned ? 20 : 15,
                                      minWidth: `${colWidth}px`,
                                    }}
                                  >
                                    <div style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
                                      {editableCol?.display_name || col.replace(/_/g, " ")}
                                      {editableCol?.info && (
                                        <span
                                          style={{
                                            marginLeft: "4px",
                                            cursor: "pointer",
                                            color: "#007bff",
                                            fontSize: "0.8rem",
                                          }}
                                          title={editableCol.info}
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
                                {allCols.map((col, colIndex) => {
                                  const editableCol = editableCols.find((ec: { col_header: string; }) => ec.col_header === col);
                                  const colWidth = editableCol?.width || (editableCol?.dtype === "datetime" ? 140 : 100);

                                  // WORKERBEE Create func to handle column logic / updates sell qty ex below
                                  if (col === "sell_qty") {
                                    return (
                                      <td
                                        key={col}
                                        style={{
                                          backgroundColor: getCellBackgroundColor(col, idx, order),
                                          position: editableCol?.pinned ? "sticky" : "relative",
                                          left: editableCol?.pinned ? `${getPinnedColumnLeftPosition(colIndex)}px` : "auto",
                                          zIndex: editableCol?.pinned ? 5 : 1,
                                          minWidth: `${colWidth}px`,
                                        }}
                                      >
                                        <input
                                          type="number"
                                          min={0}
                                          max={order.qty_available}
                                          value={editableValues[col]?.[idx] || ""}
                                          placeholder={order.qty_available ? `${order.qty_available} available` : ""}
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
                                            if (num < 0) num = 0;
                                            if (order.qty_available !== undefined && num > order.qty_available)
                                              num = order.qty_available;

                                            setEditableValues((prev) => ({
                                              ...prev,
                                              [col]: { ...prev[col], [idx]: num },
                                            }));

                                            const updatedOrders = ordersToRender.map(
                                              (ord: any, i: number) => ({
                                                ...ord,
                                                sell_qty: i === idx ? String(num) : editableValues[col]?.[i] || "",
                                              })
                                            );
                                            setPromptText({
                                              ...promptText,
                                              active_orders_with_qty: updatedOrders,
                                            });
                                          }}
                                          style={{ width: "100%", fontSize: "0.8rem" }}
                                        />
                                      </td>
                                    );
                                  } else if (editableCol) {
                                    if (editableCol.dtype === "list") {
                                      const options = editableCol.values || [];
                                      return (
                                        <td
                                          key={col}
                                          style={{
                                            backgroundColor: getCellBackgroundColor(col, idx, order),
                                            position: editableCol.pinned ? "sticky" : "relative",
                                            left: editableCol.pinned ? `${getPinnedColumnLeftPosition(colIndex)}px` : "auto",
                                            zIndex: editableCol.pinned ? 5 : 1,
                                            minWidth: `${colWidth}px`,
                                          }}
                                        >
                                          <select
                                            value={editableValues[col]?.[idx] || ""}
                                            onChange={(e) => {
                                              const value = e.target.value;
                                              setEditableValues((prev) => ({
                                                ...prev,
                                                [col]: { ...prev[col], [idx]: value },
                                              }));
                                            }}
                                            style={{ width: "100%", fontSize: "0.8rem", padding: "4px" }}
                                          >
                                            <option value="" disabled>Select...</option>
                                            {options.map((option: string, i: number) => (
                                              <option key={i} value={option}>{option}</option>
                                            ))}
                                          </select>
                                        </td>
                                      );
                                    } else if (editableCol.dtype === "checkbox") {
                                      return (
                                        <td
                                          key={col}
                                          style={{
                                            backgroundColor: getCellBackgroundColor(col, idx, order),
                                            position: editableCol.pinned ? "sticky" : "relative",
                                            left: editableCol.pinned ? `${getPinnedColumnLeftPosition(colIndex)}px` : "auto",
                                            zIndex: editableCol.pinned ? 5 : 1,
                                            minWidth: `${colWidth}px`,
                                          }}
                                        >
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
                                    } else if (editableCol.dtype === "number" || editableCol.dtype === "float" || editableCol.dtype === "int") {
                                      return (
                                        <td
                                          key={col}
                                          style={{
                                            backgroundColor: getCellBackgroundColor(col, idx, order),
                                            position: editableCol.pinned ? "sticky" : "relative",
                                            left: editableCol.pinned ? `${getPinnedColumnLeftPosition(colIndex)}px` : "auto",
                                            zIndex: editableCol.pinned ? 5 : 1,
                                            minWidth: `${colWidth}px`,
                                          }}
                                        >
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
                                            style={{ width: "100%", fontSize: "0.8rem" }}
                                          />
                                        </td>
                                      );
                                    } else if (editableCol.dtype === "datetime") {
                                      return (
                                        <td
                                          key={col}
                                          style={{
                                            backgroundColor: getCellBackgroundColor(col, idx, order),
                                            position: editableCol.pinned ? "sticky" : "relative",
                                            left: editableCol.pinned ? `${getPinnedColumnLeftPosition(colIndex)}px` : "auto",
                                            zIndex: editableCol.pinned ? 5 : 1,
                                            minWidth: `${colWidth}px`,
                                          }}
                                        >
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
                                            style={{ width: "100%", fontSize: "0.8rem" }}
                                          />
                                        </td>
                                      );
                                    } else {
                                      // text or str
                                      return (
                                        <td
                                          key={col}
                                          style={{
                                            backgroundColor: getCellBackgroundColor(col, idx, order),
                                            position: editableCol.pinned ? "sticky" : "relative",
                                            left: editableCol.pinned ? `${getPinnedColumnLeftPosition(colIndex)}px` : "auto",
                                            zIndex: editableCol.pinned ? 5 : 1,
                                            minWidth: `${colWidth}px`,
                                          }}
                                        >
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
                                            style={{ width: "100%", fontSize: "0.8rem" }}
                                          />
                                        </td>
                                      );
                                    }
                                  } else {
                                    // Render plain text for non-editable columns
                                    return (
                                      <td key={col} style={{ minWidth: `${colWidth}px` }}>
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
                                  const sum = ordersToRender.reduce((acc: number, order: any) => {
                                    const val = order[col];
                                    return typeof val === "number" && !isNaN(val) ? acc + val : acc;
                                  }, 0);
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




            {/* Add Symbol Row Info Column */}
            {add_symbol_row_info && Array.isArray(add_symbol_row_info) && (() => {
              const trinityKeys = ['trinity_w_L', 'trinity_w_15', 'trinity_w_30', 'trinity_w_54'];
              const trinityPresent = add_symbol_row_info.filter((col: string) => trinityKeys.includes(col) && selectedRow?.[col] !== undefined);
              const regularCols = add_symbol_row_info.filter((col: string) => !trinityKeys.includes(col));


              return (
                <div style={{ marginBottom: "4px" }}>

                  {/* Trinity Display */}
                  {trinityPresent.length > 0 && (
                    <div style={{ display: "flex", gap: "8px", marginBottom: "4px" }}>
                      {[
                        { key: 'trinity_w_L', label: 'Trinity Avg Weight', main: true },
                        { key: 'trinity_w_15', label: '1Day - 1Week' },
                        { key: 'trinity_w_30', label: '1Month - 3Month' },
                        { key: 'trinity_w_54', label: '6Month - 1Year' },
                      ].filter(({ key }) => selectedRow?.[key] !== undefined).map(({ key, label, main }) => {
                        const val = Number(selectedRow[key]);
                        const bgColor = getTrinityColor(val);
                        return (
                          <div
                            key={key}
                            style={{
                              flex: main ? "1.5" : "1.1",
                              display: "flex",
                              flexDirection: "column",
                              alignItems: "center",
                              justifyContent: "center",
                              borderRadius: main ? "10px" : "6px",
                              padding: main ? "8px 12px 6px" : "4px 4px 3px",
                              background: bgColor,
                              border: `1px solid #222`,
                              boxShadow: main ? "0 1px 8px rgba(166, 196, 190, 0.19)" : "0 1px 4px rgba(0,0,0,0.05)",
                              minWidth: main ? "90px" : "65px",
                            }}
                          >
                            <div
                              style={{
                                fontSize: main ? "1.6rem" : "1.1rem",
                                fontWeight: main ? "900" : "700",
                                lineHeight: 1.1,
                                color: "#222", // dark text
                                letterSpacing: main ? "-1px" : "0px",
                                filter: "none",
                              }}
                            >
                              {val > 0 ? "+" : ""}
                              {val.toFixed(1)}%
                            </div>
                            <div
                              style={{
                                fontSize: main ? "0.68rem" : "0.62rem",
                                color: "#222", // dark text
                                textTransform: "uppercase",
                                letterSpacing: main ? "2.3px" : "1.3px",
                                marginTop: "3px",
                                textAlign: "center",
                              }}
                            >
                              {label}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {/* Regular add_symbol_row_info cols */}
                  {regularCols.length > 0 && (
                    <div
                      className="d-flex flex-wrap"
                      style={{
                        border: "1px solid #e0e0e0",
                        borderRadius: "10px",
                        padding: "12px 10px 8px",
                        background: "linear-gradient(90deg, #fafcff 80%, #f3f6fa 100%)",
                        boxShadow: "0 1px 6px rgba(206, 188, 188, 0.06)",
                        gap: "12px",
                      }}
                    >
                      {regularCols.map((col: string) =>
                        selectedRow && selectedRow[col] !== undefined && (
                          <div
                            key={col}
                            style={{
                              flex: "1 1 32%",
                              minWidth: "140px",
                              marginBottom: "10px",
                              padding: "10px 14px 8px 10px",
                              background: "#fff",
                              borderRadius: "8px",
                              boxShadow: "0 1px 4px rgba(0,0,0,0.04)",
                              display: "flex",
                              alignItems: "center",
                              gap: "8px",
                            }}
                          >
                            <span style={{
                              fontWeight: 700,
                              color: "#222",
                              fontSize: "1.05rem",
                              marginRight: "6px",
                              textTransform: "capitalize",
                              letterSpacing: "0.5px",
                            }}>
                              {col.replace(/_/g, " ")}:
                            </span>
                            <span style={{
                              fontWeight: 500,
                              color: "#222",
                              fontSize: "1rem",
                            }}>
                              {typeof selectedRow[col] === "number"
                                ? Number(selectedRow[col]).toLocaleString(undefined, { maximumFractionDigits: 2 })
                                : String(selectedRow[col])}
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  )}

                </div>
              );
            })()}


            {/* {sliderRules_stars.some(rule => prompt_order_rules?.includes(rule)) && (
  <h3 style={{ marginBottom: "16px", textAlign: "center" }}>
    Symbol Budget Allocation
  </h3>
)} */}
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
                        flex: "1 1 40%",
                        minWidth: "120px",
                        marginBottom: "4px",
                        padding: "2px 0",
                      }}
                    >
                      <label
                        className="mb-1"
                        style={{
                          fontSize: "0.8rem",
                          fontWeight: "bold",
                          textTransform: "capitalize",
                          marginBottom: "2px",
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





          </div>
        </div>


        {/* Modal Footer */}
        <div className="modal-footer d-flex justify-content-center" style={{
          position: "sticky",
          bottom: 0,
          backgroundColor: "#fff", // ✅ Add solid background
          zIndex: 20, // ✅ Higher than table content
          boxShadow: "0 -2px 10px rgba(0,0,0,0.1)", // ✅ Optional: adds subtle shadow above
          padding: "12px" // ✅ Ensure padding
        }}>
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

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


const modalStyle = {
  content: {
    top: "50%",
    left: "50%",
    right: "auto",
    bottom: "auto",
    marginRight: "-50%",
    transform: "translate(-50%, -50%)",
    backgroundColor: "yellow",
  },
};

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
  const { prompt_field, prompt_order_rules, selectedRow, selectedField } = modalData;
  // console.log("modalData :>> ", selectedRow);
  const [showStarsSliders, setShowStarsSliders] = React.useState(false);
  const [showStarsMarginSliders, setShowStarsMarginSliders] = React.useState(false);
  
  const ref = useRef<HTMLButtonElement>(null);
  const selectRef = useRef<HTMLSelectElement>(null);

  const handleOk = async () => {
    if (isExecuting) return;
    isExecuting = true;
    try {
      const { data: res } = await axios.post(modalData.button_api, {
        username: modalData.username,
        prod: modalData.prod,
        selected_row: modalData.selectedRow,
        default_value: promptText,
        ...modalData.kwargs,
      });
      const { status, data, description } = res;
      console.log("res :>> ", res);
      if (status === "success") {
        data.message_type === "fade"
          ? toastr.success(description, "Success")
          : alert("Success!\nDescription: " + description);
      } else {
        data.message_type === "fade"
          ? toastr.error(description, "Error")
          : alert("Error!\nDescription: " + description);
      }
      if (data?.close_modal != false) closeModal();
    } catch (error: any) {
      console.log("error :>> ", error);
      toastr.error(error.message);
    }
    isExecuting = false;
  };

  const handleOkSecond = async () => {
    if (isExecuting) return;
    isExecuting = true;
    try {
      const body = {
        username: modalData.username,
        prod: modalData.prod,
        selected_row: modalData.selectedRow,
        default_value: promptText,
        ...modalData.kwargs,
      };
      console.log("body :>> ", body);
      const { data: res } = await axios.post(modalData.button_api, body);
      const { status, data, description } = res;
      if (status === "success") {
        data.message_type === "fade"
          ? toastr.success(description, "Success")
          : alert("Success!\nDescription: " + description);
      } else {
        data.message_type === "fade"
          ? toastr.error(description, "Error")
          : alert("Error!\nDescription: " + description);
      }
      if (data?.close_modal != false) closeModal();
    } catch (error: any) {
      console.log("error :>> ", error);
      toastr.error(error.message);
    }
    isExecuting = false;
  };

  const handleOkOnArray = async () => {
    console.log("selectRef.current.value :>> ", selectRef.current?.value);
    if (isExecuting) return;
    isExecuting = true;
    try {
      const body = {
        username: modalData.username,
        prod: modalData.prod,
        selected_row: modalData.selectedRow,
        default_value: selectRef.current?.value,
        ...modalData.kwargs,
      };
      console.log("body :>> ", body);
      const { data: res } = await axios.post(modalData.button_api, body);
      const { status, data, description } = res;
      console.log("res :>> ", res);
      if (status === "success") {
        data.message_type === "fade"
          ? toastr.success(description, "Success")
          : alert("Success!\nDescription: " + description);
      } else {
        data.message_type === "fade"
          ? toastr.error(description, "Error")
          : alert("Error!\nDescription: " + description);
      }
      if (data?.close_modal != false) closeModal();
    } catch (error: any) {
      console.log("error :>> ", error);
      toastr.error(error.message);
    }
    isExecuting = false;
  };

  useEffect(() => {
    if (isOpen) setTimeout(() => ref.current?.focus(), 100);
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
    <div className="my-modal" style={{ display: isOpen ? "block" : "none" }}>
      <div className="my-modal-content">
        {/* Modal Header */}
        <div className="modal-header px-3 d-flex justify-content-center align-items-center">
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
              <div className="d-flex flex-row justify-content-between mb-2">
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


            {/* Other Fields (Text, Datetime, Array Fields) */}
            <div className="d-flex flex-row justify-content-between">
              {/* Text Fields Column */}
              {textFields.length > 0 && (
                <div className="d-flex flex-column" style={{ flex: 1, marginRight: "8px" }}>
                  {textFields.map((rule: any, index: number) => {

                  // Skip rendering if the rule is in the sliderRules_stars list
                  if (sliderRules_stars.includes(rule)) return null;
                  if (sliderRules_stars_margin.includes(rule)) return null;

                  const isSliderRule = sliderRules.includes(rule);

                  return (
                    <div className="d-flex flex-column align-items-start mb-1" key={index}>
                    <label className="mb-0" style={{ fontSize: "0.9rem" }}>
                      {rule}:
                      {rule === "sell_amount" && (
                      <span
                        style={{ marginLeft: "4px", cursor: "pointer" }}
                        title="This amount will override sell_qty"
                      >
                        ❓
                      </span>
                      )}
                    </label>
                    {/* Render the slider for rules that are in sliderRules but not in sliderRules_stars */}
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
                      <span style={{ fontSize: "0.9rem", fontWeight: "bold", marginTop: "4px" }}>
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
                      style={{ flex: 1, width: "100%", padding: "4px", fontSize: "0.9rem" }}
                      />
                    )}
                    </div>
                  );
                  })}
                </div>
              )}


              {/* Array Fields Column */}
              {arrayFields.length > 0 && (
                <div className="d-flex flex-column" style={{ flex: 1 }}>
                  {arrayFields.map((rule: any, index: number) => (
                    <div className="d-flex flex-column align-items-start mb-1" key={index}>
                      <label className="mb-0" style={{ fontSize: "0.9rem" }}>
                        {rule}:
                      </label>
                      <select
                        value={promptText[rule][0]}
                        onChange={(e) =>
                          setPromptText({
                            ...promptText,
                            [rule]: [e.target.value],
                          })
                        }
                        style={{ flex: 1, width: "100%", padding: "4px", fontSize: "0.9rem" }}
                      >
                        {promptText[rule].map((item: any, i: number) => (
                          <option key={i} value={item}>
                            {item}
                          </option>
                        ))}
                      </select>
                    </div>
                  ))}
                </div>
              )}

              {/* Expander for sliderRules_stars */}
              {sliderRules_stars.some((rule: any) => prompt_order_rules?.includes(rule)) && (
                <div style={{ flex: 1, marginRight: "8px" }}>
                  <div
                    style={{ cursor: "pointer", fontWeight: "bold", marginBottom: "4px" }}
                    onClick={() => setShowStarsSliders((prev) => !prev)}
                  >
                    {showStarsSliders ? "▼" : "►"} Advanced Allocation Options
                  </div>
                  {showStarsSliders && (
                    <div>
                      {sliderRules_stars.map((rule: any, index: number) =>
                        prompt_order_rules?.includes(rule) && promptText[rule] !== undefined && (
                          <div className="d-flex flex-column align-items-start mb-1" key={index}>
                            <label className="mb-0" style={{ fontSize: "0.9rem" }}>
                              {rule}:
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
                            <span style={{ fontSize: "0.9rem", fontWeight: "bold", marginTop: "4px" }}>
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
                <div style={{ flex: 1, marginRight: "8px" }}>
                  <div
                    style={{ cursor: "pointer", fontWeight: "bold", marginBottom: "4px" }}
                    onClick={() => setShowStarsMarginSliders((prev) => !prev)}
                  >
                    {showStarsMarginSliders ? "▼" : "►"} Advanced Margin Allocation Options
                  </div>
                  {showStarsMarginSliders && (
                    <div>
                      {sliderRules_stars_margin.map((rule: any, index: number) =>
                        prompt_order_rules?.includes(rule) && promptText[rule] !== undefined && (
                          <div className="d-flex flex-column align-items-start mb-1" key={index}>
                            <label className="mb-0" style={{ fontSize: "0.9rem" }}>
                              {rule}:
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
                            <span style={{ fontSize: "0.9rem", fontWeight: "bold", marginTop: "4px" }}>
                              {promptText[rule] || 0}
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  )}
                </div>
              )}
  
              {/* Datetime Fields Column */}
              {datetimeFields.length > 0 && (
                <div className="d-flex flex-column" style={{ flex: 1, marginRight: "8px" }}>
                  {datetimeFields.map((rule: any, index: number) => (
                    <div className="d-flex flex-column align-items-start mb-1" key={index}>
                      <label className="mb-0" style={{ fontSize: "0.9rem" }}>
                        {rule}:
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
                        style={{ flex: 1, width: "100%", padding: "4px", fontSize: "0.9rem" }}
                      />
                    </div>
                  ))}
                </div>
              )}
  

            </div>
          </div>
        </div>

        {selectedRow && selectedRow.current_ask !== undefined && (
          <div>
            <b>current_ask: </b>
            {Number(selectedRow.current_ask).toLocaleString(undefined, { maximumFractionDigits: 2 })}

          </div>
        )}

        {selectedRow && selectedRow.ticker_total_budget !== undefined && (
          <div>
            <b>Total Budget:$ </b>
            {Number(selectedRow.ticker_total_budget).toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </div>
        )}

        {selectedRow && selectedRow.star_buys_at_play !== undefined && (
          <div>
            <b>Currently Long:$ </b>
            {Number(selectedRow.star_buys_at_play).toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </div>
        )}

        {selectedRow && selectedRow.ticker_remaining_budget !== undefined && (
          <div>
            <b>Remaining Budget:$ </b>
            {Number(selectedRow.ticker_remaining_budget).toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </div>
        )}


        {/* Modal Footer */}
        <div className="modal-footer d-flex justify-content-center">
          <button type="button" className="btn btn-primary mx-2" onClick={handleOkSecond} ref={ref}>
            Ok
          </button>
          <button type="button" className="btn btn-secondary mx-2" onClick={closeModal}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
  
};

export default MyModal;

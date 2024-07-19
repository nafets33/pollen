import React, { useEffect, useRef } from "react"
import ReactModal from "react-modal"
import "./modal.css"
import axios from "axios"
import {utcToZonedTime, format} from 'date-fns-tz';
import moment from "moment";

const formats = ["YYYY-MM-DDTHH:mm", "MM/DD/YYYYTHH:mm", "MM/DD/YYYY HH:mm", "YYYY-MM-DD HH:mm"];

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
}
ReactModal.setAppElement("#root")
let isExecuting = false

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
  const { prompt_field, prompt_order_rules, selectedRow, selectedField } =
    modalData

  const ref = useRef<HTMLButtonElement>(null);
  const selectRef = useRef<HTMLSelectElement>(null);

  const handleOk = async () => {
    if (isExecuting) return
    isExecuting = true
    try {
      const { data: res } = await axios.post(modalData.button_api, {
        username: modalData.username,
        prod: modalData.prod,
        selected_row: modalData.selectedRow,
        default_value: promptText,
        ...modalData.kwargs,
      })
      const { status, data, description } = res
      console.log("res :>> ", res)
      if (status === "success") {
        data.message_type === "fade"
          ? toastr.success(description, "Success")
          : alert("Success!\nDescription: " + description)
      } else {
        data.message_type === "fade"
          ? toastr.error(description, "Error")
          : alert("Error!\nDescription: " + description)
      }
      if (data?.close_modal != false) closeModal()
    } catch (error: any) {
      console.log("error :>> ", error)
      toastr.error(error.message)
    }
    isExecuting = false
  }

  const handleOkSecond = async () => {
    if (isExecuting) return
    isExecuting = true
    try {
      const formattedSellDate = format(new Date(promptText.sell_date), 'MM/dd/yyyy\'T\'HH:mm');

      const body = {
        username: modalData.username,
        prod: modalData.prod,
        selected_row: modalData.selectedRow,
        default_value: {
          ...promptText,
          sell_date: formattedSellDate
        },
        ...modalData.kwargs,
      }
      console.log("body :>> ", body)
      const { data: res } = await axios.post(modalData.button_api, body)
      const { status, data, description } = res
      if (status === "success") {
        data.message_type === "fade"
          ? toastr.success(description, "Success")
          : alert("Success!\nDescription: " + description)
      } else {
        data.message_type === "fade"
          ? toastr.error(description, "Error")
          : alert("Error!\nDescription: " + description)
      }
      if (data?.close_modal != false) closeModal()
    } catch (error: any) {
      console.log("error :>> ", error)
      toastr.error(error.message)
    }
    isExecuting = false
  }

  const handleOkOnArray = async () => {
    console.log("selectRef.current.value :>> ", selectRef.current?.value)
    if (isExecuting) return
    isExecuting = true
    try {
      const body = {
        username: modalData.username,
        prod: modalData.prod,
        selected_row: modalData.selectedRow,
        default_value: selectRef.current?.value,
        ...modalData.kwargs,
      }
      console.log("body :>> ", body)
      const { data: res } = await axios.post(modalData.button_api, body)
      const { status, data, description } = res
      console.log("res :>> ", res)
      if (status === "success") {
        data.message_type === "fade"
          ? toastr.success(description, "Success")
          : alert("Success!\nDescription: " + description)
      } else {
        data.message_type === "fade"
          ? toastr.error(description, "Error")
          : alert("Error!\nDescription: " + description)
      }
      if (data?.close_modal != false) closeModal()
    } catch (error: any) {
      console.log("error :>> ", error)
      toastr.error(error.message)
    }
    isExecuting = false
  }

  useEffect(() => {
    if (isOpen) setTimeout(() => ref.current?.focus(), 100)
  }, [isOpen]);

  const isValidDate = (dateStr: string) => {
    return formats.some(format => moment(dateStr, format, true).isValid());
  };

  const formatToLocalDatetime = (dateStr: string) => {
    const date = new Date(dateStr);
    const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const zonedDate = utcToZonedTime(date, timeZone);
    return format(zonedDate, 'yyyy-MM-dd\'T\'HH:mm');
  };

  if (Array.isArray(selectedField))
    return (
      <div className="my-modal" style={{ ...modalStyle.content, display: isOpen ? "block" : "none" }}>
        <div className="my-modal-content">
          <div className="modal-header px-4">
            <h4>{modalData.prompt_message}</h4>
            <span className="close" onClick={closeModal}>
              &times;
            </span>
          </div>
          <div className="modal-body p-2">
            <label className="px-1">{prompt_field} </label>
            <select
              name="cars"
              id="cars"
              defaultValue={selectedField[0]}
              ref={selectRef}
            >
              {selectedField.map((item) => (
                <option value={item}>{item}</option>
              ))}
            </select>
          </div>
          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleOkOnArray}
              ref={ref}
            >
              Ok
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={closeModal}
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    )


  if (prompt_order_rules) {
    // console.log(typeof promptText[rule]); // Check the type of promptText[rule]
    // console.log(promptText[rule]); // Inspect the value of promptText[rule]
    // Initialize arrays for each datatype
    return (
      <div className="my-modal" style={{ display: isOpen ? "block" : "none" }}>
        <div className="my-modal-content">
          <div className="modal-header px-4">
            <h4>{modalData.prompt_message}</h4>
            <span className="close" onClick={closeModal}>
              &times;
            </span>
          </div>
          <div className="modal-body p-2">
            <div className="d-flex flex-column">
              {prompt_order_rules.map((rule: any, index: number) => (
                <div className="d-flex flex-row justify-content-end" key={index}>
                  <label className="d-flex flex-row">
                    {rule + ": "}
                    {typeof promptText[rule] === "boolean" ? (
                      <input
                        type="checkbox"
                        checked={promptText[rule]}
                        onChange={(e) =>
                          setPromptText({
                            ...promptText,
                            [rule]: e.target.checked,
                          })
                        }
                      />
                    ) : Array.isArray(promptText[rule]) ? (
                      <select
                        value={promptText[rule][0]} // Assuming the first option is selected by default
                        onChange={(e) =>
                          setPromptText({
                            ...promptText,
                            [rule]: [e.target.value],
                          })
                        }
                      >
                        {promptText[rule].map((item: any, i: number) => (
                          <option key={i} value={item}>
                            {item}
                          </option>
                        ))}
                      </select>
                    ) : isValidDate(promptText[rule]) ? (
                      <input
                        type="datetime-local"
                        value={promptText[rule] && formatToLocalDatetime(promptText[rule])}
                        onChange={(e) =>
                          setPromptText({
                            ...promptText,
                            [rule]: e.target.value,
                          })
                        }
                      />
                    ) : (
                      <input
                        type={promptText[rule] && !isValidDate(promptText[rule]) ? 'text' : 'datetime-local'}
                        value={promptText[rule]}
                        onChange={(e) =>
                          setPromptText({
                            ...promptText,
                            [rule]: e.target.value,
                          })
                        }
                      />
                    )}
                  </label>
                  {isValidDate(promptText[rule])}
                </div>
              ))}
            </div>
          </div>
          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleOkSecond}
              ref={ref}
            >
              Ok
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={closeModal}
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
}

export default MyModal;

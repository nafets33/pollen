import React, { useEffect, useRef, useState } from "react"
import ReactModal from "react-modal"
import "./modal.css"
import axios from "axios"

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

const MyModal = ({
  isOpen,
  closeModal,
  modalData,
  promptText,
  setPromptText,
  toastr,
}) => {
  const { prompt_field, prompt_order_rules, selectedRow, selectedField } =
    modalData

  const ref = useRef()
  const selectRef = useRef()

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
      if (status == "success") {
        data.message_type == "fade"
          ? toastr.success(description, "Success")
          : alert("Success!\nDescription: " + description)
      } else {
        data.message_type == "fade"
          ? toastr.error(description, "Error")
          : alert("Error!\nDescription: " + description)
      }
      if (data?.close_modal != false) closeModal()
    } catch (error) {
      console.log("error :>> ", error)
      toastr.error(error.message)
    }
    isExecuting = false
  }

  const handleOkSecond = async () => {
    if (isExecuting) return
    isExecuting = true
    try {
      const body = {
        username: modalData.username,
        prod: modalData.prod,
        selected_row: modalData.selectedRow,
        default_value: promptText,
        ...modalData.kwargs,
      }
      console.log("body :>> ", body)
      const { data: res } = await axios.post(modalData.button_api, body)
      const { status, data, description } = res
      if (status == "success") {
        data.message_type == "fade"
          ? toastr.success(description, "Success")
          : alert("Success!\nDescription: " + description)
      } else {
        data.message_type == "fade"
          ? toastr.error(description, "Error")
          : alert("Error!\nDescription: " + description)
      }
      if (data?.close_modal != false) closeModal()
    } catch (error) {
      console.log("error :>> ", error)
      toastr.error(error.message)
    }
    isExecuting = false
  }

  const handleOkOnArray = async () => {
    console.log("selectRef.current.value :>> ", selectRef.current.value)
    if (isExecuting) return
    isExecuting = true
    try {
      const body = {
        username: modalData.username,
        prod: modalData.prod,
        selected_row: modalData.selectedRow,
        default_value: selectRef.current.value,
        ...modalData.kwargs,
      }
      console.log("body :>> ", body)
      const { data: res } = await axios.post(modalData.button_api, body)
      const { status, data, description } = res
      console.log("res :>> ", res)
      if (status == "success") {
        data.message_type == "fade"
          ? toastr.success(description, "Success")
          : alert("Success!\nDescription: " + description)
      } else {
        data.message_type == "fade"
          ? toastr.error(description, "Error")
          : alert("Error!\nDescription: " + description)
      }
      if (data?.close_modal != false) closeModal()
    } catch (error) {
      console.log("error :>> ", error)
      toastr.error(error.message)
    }
    isExecuting = false
  }

  useEffect(() => {
    if (isOpen) setTimeout(() => ref.current.focus(), 100)
  }, [isOpen])

  if (Array.isArray(selectedField))
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

  if (prompt_order_rules)
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
            {prompt_order_rules.map((rule, index) => {
              if (typeof promptText[rule] == "boolean")
                return (
                  <div
                    className="d-flex flex-row justify-content-end"
                    key={index}
                  >
                    <label className="d-flex flex-row">
                      {rule + ":  "}
                      <div className="px-2" style={{ width: "193px" }}>
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
                      </div>
                    </label>
                  </div>
                )
              return (
                <div
                  className="d-flex flex-row justify-content-end"
                  key={index}
                >
                  <label>
                    {rule + ":  "}
                    <input
                      type="text"
                      value={promptText[rule]}
                      onChange={(e) =>
                        setPromptText({ ...promptText, [rule]: e.target.value })
                      }
                    />
                  </label>
                </div>
              )
            })}
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
    )

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
          <textarea
            className="form-control"
            rows={4}
            cols={50}
            type="text"
            value={promptText}
            placeholder="Please input text"
            onChange={(e) => setPromptText(e.target.value)}
          />
        </div>
        <div className="modal-footer">
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleOk}
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
}

export default MyModal

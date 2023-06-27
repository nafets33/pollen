import React from "react"
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

const MyModal = ({
  isOpen,
  closeModal,
  modalData,
  promptText,
  setPromptText,
  toastr,
}) => {
  const handleOk = async () => {
    try {
      const res = await axios.post(modalData.button_api, {
        username: modalData.username,
        prod: modalData.prod,
        selected_row: modalData.selectedRow,
        default_value: promptText,
        ...modalData.kwargs,
      })
      toastr.success("Success")
      closeModal()
    } catch (error) {
      alert(`${error}`)
    }
  }
  return (
    // <ReactModal
    //   isOpen={isOpen}
    //   onAfterOpen={afterOpenModal}
    //   onRequestClose={closeModal}
    //   style={modalStyle}
    //   contentLabel="Example Modal"
    // >
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
          <button type="button" className="btn btn-primary" onClick={handleOk}>
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
    // </ReactModal>
  )
}

export default MyModal

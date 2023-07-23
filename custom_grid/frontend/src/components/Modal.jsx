import React, { useEffect, useRef, useState } from 'react'
import ReactModal from 'react-modal'
import './modal.css'
import axios from 'axios'
import { order_rules_default } from '../utils/order_rules'

const modalStyle = {
  content: {
    top: '50%',
    left: '50%',
    right: 'auto',
    bottom: 'auto',
    marginRight: '-50%',
    transform: 'translate(-50%, -50%)',
    backgroundColor: 'yellow',
  },
}
ReactModal.setAppElement('#root')

const MyModal = ({
  isOpen,
  closeModal,
  modalData,
  promptText,
  setPromptText,
  toastr,
}) => {
  const { prompt_field, prompt_order_rules, selectedRow } = modalData

  const ref = useRef()

  const handleOk = async () => {
    try {
      const res = await axios.post(modalData.button_api, {
        username: modalData.username,
        prod: modalData.prod,
        selected_row: modalData.selectedRow,
        default_value: promptText,
        ...modalData.kwargs,
      })
      toastr.success('Success')
      closeModal()
    } catch (error) {
      alert(`${error}`)
    }
  }

  const handleOkSecond = async () => {
    try {
      console.log('promptText :>> ', promptText)
      const res = await axios.post(modalData.button_api, {
        username: modalData.username,
        prod: modalData.prod,
        selected_row: modalData.selectedRow,
        default_value: promptText,
        ...modalData.kwargs,
      })
      toastr.success('Success')
      closeModal()
    } catch (error) {
      alert(`${error}`)
    }
  }

  useEffect(() => {
    if (isOpen) setTimeout(() => ref.current.focus(), 100)
  }, [isOpen])

  if (prompt_field === 'order_rules')
    return (
      <div className='my-modal' style={{ display: isOpen ? 'block' : 'none' }}>
        <div className='my-modal-content'>
          <div className='modal-header px-4'>
            <h4>{modalData.prompt_message}</h4>
            <span className='close' onClick={closeModal}>
              &times;
            </span>
          </div>
          <div className='modal-body p-2'>
            {prompt_order_rules.map((rule, index) => {
              if (typeof promptText[rule] == 'boolean')
                return (
                  <div
                    className='d-flex flex-row justify-content-end'
                    key={index}
                  >
                    <label className='d-flex flex-row'>
                      {rule + ':  '}
                      <div className='px-2' style={{ width: '193px' }}>
                        <input
                          type='checkbox'
                          checked={promptText[rule]}
                          onChange={e =>
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
                  className='d-flex flex-row justify-content-end'
                  key={index}
                >
                  <label>
                    {rule + ':  '}
                    <input
                      type='text'
                      value={promptText[rule]}
                      onChange={e =>
                        setPromptText({ ...promptText, [rule]: e.target.value })
                      }
                    />
                  </label>
                </div>
              )
            })}
          </div>
          <div className='modal-footer'>
            <button
              type='button'
              className='btn btn-primary'
              onClick={handleOkSecond}
              ref={ref}
            >
              Ok
            </button>
            <button
              type='button'
              className='btn btn-secondary'
              onClick={closeModal}
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    )

  return (
    <div className='my-modal' style={{ display: isOpen ? 'block' : 'none' }}>
      <div className='my-modal-content'>
        <div className='modal-header px-4'>
          <h4>{modalData.prompt_message}</h4>
          <span className='close' onClick={closeModal}>
            &times;
          </span>
        </div>
        <div className='modal-body p-2'>
          <textarea
            className='form-control'
            rows={4}
            cols={50}
            type='text'
            value={promptText}
            placeholder='Please input text'
            onChange={e => setPromptText(e.target.value)}
          />
        </div>
        <div className='modal-footer'>
          <button
            type='button'
            className='btn btn-primary'
            onClick={handleOk}
            ref={ref}
          >
            Ok
          </button>
          <button
            type='button'
            className='btn btn-secondary'
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

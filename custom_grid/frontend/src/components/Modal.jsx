import React from 'react'
import ReactModal from 'react-modal';


const modalStyle = {
    content: {
        top: '50%',
        left: '50%',
        right: 'auto',
        bottom: 'auto',
        marginRight: '-50%',
        transform: 'translate(-50%, -50%)',
    },
};
ReactModal.setAppElement('#root');

const MyModal = ({ children, ...rest }) => {
    const { isOpen, afterOpenModal, closeModal, } = rest;
    return (
        <ReactModal
            isOpen={isOpen}
            onAfterOpen={afterOpenModal}
            onRequestClose={closeModal}
            style={modalStyle}
            contentLabel="Example Modal"
        >
            My Modal
            {children}
        </ReactModal>
    )
}

export default MyModal;
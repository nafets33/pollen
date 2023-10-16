import React, { useState, useEffect, FC } from "react"
import axios from "axios"
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib"
import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition"

const imageUrls = {
  hoots: "/hoots.png",
  hootsAndHootie: "/hootsAndhootie.png",
}

const CustomVoiceGPT = (props) => {
  const { api, kwargs = {} } = props
  const [imageSrc, setImageSrc] = useState(imageUrls.hoots)
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
  } = useSpeechRecognition()

  useEffect(() => Streamlit.setFrameHeight())

  useEffect(() => {}, [props])

  if (!browserSupportsSpeechRecognition) {
    return <span>Browser does not support speech recognition.</span>
  }

  return (
    <>
      <span>
        <img src={imageSrc} height={100} />
      </span>
      <div>
        <p>Microphone: {listening ? "on" : "off"}</p>
        <button onClick={SpeechRecognition.startListening}>Start</button>
        <button onClick={SpeechRecognition.stopListening}>Stop</button>
        <button onClick={resetTranscript}>Reset</button>
        <p>{transcript}</p>
      </div>
    </>
  )
}

export default CustomVoiceGPT

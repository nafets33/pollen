import React, { useState, useEffect } from "react"
import { useSpeechRecognition } from "react-speech-recognition"

let timer

const Dictaphone = ({
  commands,
  myFunc,
  listenAfterRelpy,
  noResponseTime = 1,
  show_conversation = true,
}) => {
  const [transcribing, setTranscribing] = useState(true)
  const [clearTranscriptOnListen, setClearTranscriptOnListen] = useState(true)
  const toggleTranscribing = () => setTranscribing(!transcribing)
  const toggleClearTranscriptOnListen = () =>
    setClearTranscriptOnListen(!clearTranscriptOnListen)
  const {
    transcript,
    interimTranscript,
    finalTranscript,
    resetTranscript,
    listening,
    browserSupportsSpeechRecognition,
    isMicrophoneAvailable,
  } = useSpeechRecognition({ transcribing, clearTranscriptOnListen })
  const [prevScript, setPrevScript] = useState("")

  useEffect(() => {
    // console.log(
    //   "Got interim result:",
    //   interimTranscript.length,
    //   interimTranscript
    // )
    // setPrevScript(interimTranscript)
    // if (interimTranscript === "") {
    //   console.log("prevScript :>> ", prevScript)
    // }
  }, [interimTranscript])

  useEffect(() => {
    if (finalTranscript != "") {
      console.log("Got final result:", finalTranscript)
      timer && clearTimeout(timer)
      timer = setTimeout(() => {
        setPrevScript(finalTranscript)
        // keyword trigger
        for (let i = 0; i < commands.length; i++) {
          const { keywords, api_body } = commands[i]
          for (let j = 0; j < keywords.length; j++) {
            const keyword = new RegExp(keywords[j], "i")
            const isKeywordFound = finalTranscript.search(keyword) != -1

            if (isKeywordFound) {
              myFunc(finalTranscript, commands[i], 1)
              resetTranscript()
              return
            }
          }
        }
        if (listenAfterRelpy) {
          myFunc(finalTranscript, { api_body: { keyword: "" } }, 3)
          resetTranscript()
          return
        }
        //waiting for keyword
        console.log("waiting for keyword")
        resetTranscript()
      }, noResponseTime * 1000)
    }
    if (finalTranscript != "" && !listenAfterRelpy) {
      setPrevScript(finalTranscript)
      resetTranscript()
    }
  }, [finalTranscript, listenAfterRelpy, commands])

  if (!browserSupportsSpeechRecognition) {
    return <span>No browser support</span>
  }

  if (!isMicrophoneAvailable) {
    return <span>Please allow access to the microphone</span>
  }

  return (
    <>
      {show_conversation && (
        <div style={{ display: "flex", flexDirection: "column" }}>
          <span>you said: {prevScript}</span>
          <span>listening: {listening ? "on" : "off"}</span>
          <span>
            clearTranscriptOnListen: {clearTranscriptOnListen ? "on" : "off"}
          </span>
        </div>
      )}
    </>
  )
}

export default Dictaphone

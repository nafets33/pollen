import React, { useState, useEffect, FC, memo, useMemo } from "react"
import axios from "axios"
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib"
import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition"
import Dictaphone from "./Dictaphone"

const imageUrls = {
  hoots: "/hoots.png",
  hootsAndHootie: "/hootsAndhootie.png",
}

const CustomVoiceGPT = (props) => {
  const { api, kwargs = {} } = props
  const [imageSrc, setImageSrc] = useState(kwargs.self_image)
  const [message, setMessage] = useState("")
  console.log("kwargs :>> ", kwargs)
  const commands = useMemo(() => {
    return kwargs["commands"].map((command) => ({
      command: command["keywords"],
      callback: async ({command:text}) => {
        setMessage(`You said ${text}, (${command["api_body"]["keyword"]})`)
        setImageSrc(command["image_on_listen"])
        try {
          console.log("api call on listen...", command)
          await axios.post(api, command["api_body"])
        } catch (error) {
          console.log("api call on listen failded!")
        }
      },
    }))
  }, [kwargs.commands])
  // const commands = [
  //   {
  //     command: "I would like to order *",
  //     callback: (food) => setMessage(`Your order is for: ${food}`),
  //     matchInterim: true,
  //   },
  //   {
  //     command: "The weather is :condition today",
  //     callback: (condition) => setMessage(`Today, the weather is ${condition}`),
  //   },
  //   {
  //     command: ["Hey foots", "Hey foods"],
  //     callback: ({ command }) => setMessage(`Hi there! You said: "${command}"`),
  //     matchInterim: true,
  //   },
  //   {
  //     command: "Beijing",
  //     callback: (command, spokenPhrase, similarityRatio) =>
  //       setMessage(
  //         `${command} and ${spokenPhrase} are ${similarityRatio * 100}% similar`
  //       ),
  //     // If the spokenPhrase is "Benji", the message would be "Beijing and Benji are 40% similar"
  //     isFuzzyMatch: true,
  //     fuzzyMatchingThreshold: 0.2,
  //   },
  //   {
  //     command: ["eat", "sleep", "leave"],
  //     callback: (command) => setMessage(`Best matching command: ${command}`),
  //     isFuzzyMatch: true,
  //     fuzzyMatchingThreshold: 0.2,
  //     bestMatchOnly: true,
  //   },
  //   {
  //     command: "clear",
  //     callback: ({ resetTranscript }) => resetTranscript(),
  //     matchInterim: true,
  //   },
  // ]

  const listenContinuously = () =>
    SpeechRecognition.startListening({
      continuous: true,
      language: "en-GB",
    })
  const listenContinuouslyInChinese = () =>
    SpeechRecognition.startListening({
      continuous: true,
      language: "zh-CN",
    })
  const listenOnce = () =>
    SpeechRecognition.startListening({ continuous: false })

  useEffect(() => Streamlit.setFrameHeight())

  useEffect(() => {}, [props])

  return (
    <>
      <span>
        <img src={imageSrc} height={100} />
        {message}
        <Dictaphone commands={commands} />
      </span>
      <div>
        {/* <button onClick={listenOnce}>Listen Once</button> */}
        <button onClick={listenContinuously}>Listen continuously</button>
        {/* <button onClick={listenContinuouslyInChinese}></button> */}
        {/* <button onClick={SpeechRecognition.stopListening}>Stop</button> */}
      </div>
    </>
  )
}

export default CustomVoiceGPT

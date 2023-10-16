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
import Dictaphone from "./Dictaphone"

const imageUrls = {
  hoots: "/hoots.png",
  hootsAndHootie: "/hootsAndhootie.png",
}

const CustomVoiceGPT = (props) => {
  const { api, kwargs = {} } = props
  const [imageSrc, setImageSrc] = useState(imageUrls.hoots)
  const [message, setMessage] = useState("")
  const commands = [
    {
      command: "I would like to order *",
      callback: (food) => setMessage(`Your order is for: ${food}`),
      matchInterim: true,
    },
    {
      command: "The weather is :condition today",
      callback: (condition) => setMessage(`Today, the weather is ${condition}`),
    },
    {
      command: ["Hello", "Hi"],
      callback: ({ command }) => setMessage(`Hi there! You said: "${command}"`),
      matchInterim: true,
    },
    {
      command: "Beijing",
      callback: (command, spokenPhrase, similarityRatio) =>
        setMessage(
          `${command} and ${spokenPhrase} are ${similarityRatio * 100}% similar`
        ),
      // If the spokenPhrase is "Benji", the message would be "Beijing and Benji are 40% similar"
      isFuzzyMatch: true,
      fuzzyMatchingThreshold: 0.2,
    },
    {
      command: ["eat", "sleep", "leave"],
      callback: (command) => setMessage(`Best matching command: ${command}`),
      isFuzzyMatch: true,
      fuzzyMatchingThreshold: 0.2,
      bestMatchOnly: true,
    },
    {
      command: "clear",
      callback: ({ resetTranscript }) => resetTranscript(),
      matchInterim: true,
    },
  ]

  useEffect(() => Streamlit.setFrameHeight())

  useEffect(() => {}, [props])

  return (
    <>
      <span>
        <img src={imageSrc} height={100} />
        <Dictaphone commands={commands} />
      </span>
    </>
  )
}

export default CustomVoiceGPT

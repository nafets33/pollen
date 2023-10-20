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

let timer = null
let g_anwers = []

const CustomVoiceGPT = (props) => {
  const { api, kwargs = {} } = props
  const [imageSrc, setImageSrc] = useState(kwargs.self_image)
  const [message, setMessage] = useState("")
  const [answers, setAnswers] = useState([])

  const testFunc = async () => {
    const audio = new Audio("./test_audio.mp3s")
    console.log(audio.play())
    const response = await axios.post(
      "http://192.168.143.97:8000/api/data/voiceGPT",
      {
        api_key: "sdf",
        text: "text",
        self_image: "something",
      }
    )
    console.log("response :>> ", response)
  }

  const commands = useMemo(() => {
    return kwargs["commands"].map((command) => ({
      command: command["keywords"],
      callback: (ret) => {
        const myFunc = async () => {
          console.log("ret :>> ", ret)
          setMessage(` (${command["api_body"]["keyword"]}) ${ret},`)
          const text = [
            ...g_anwers,
            { user: command["api_body"]["keyword"] + ret },
          ]
          setAnswers([...text])
          try {
            console.log("api call on listen...", command)
            const body = {
              api_key: "api_key",
              text: text,
              self_image: imageSrc,
            }
            const { data } = await axios.post(api, body)
            console.log("data :>> ", data)
            data.self_image && setImageSrc(data.self_image)
            setAnswers(data.text)
            g_anwers = [...data.text]
            if (data.audio_path) {
              const audio = new Audio(data.audio_path)
              audio.play()
            }
          } catch (error) {
            // console.log("api call on listen failded!")
          }
        }
        timer && clearTimeout(timer)
        timer = setTimeout(myFunc, 1000)
      },
      matchInterim: true,
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
      <div>
        <img src={imageSrc} height={100} />
        <Dictaphone commands={commands} />
        <button onClick={listenContinuously}>Listen continuously</button>
        <div> You: {message}</div>
        {answers.map((answer, idx) => (
          <div key={idx}>
            <div>-user: {answer.user}</div>
            <div>-resp: {answer.resp ? answer.resp : "thinking..."}</div>
          </div>
        ))}
      </div>
      <div>
        {/* <button onClick={listenOnce}>Listen Once</button> */}
        {/* <button onClick={listenContinuouslyInChinese}></button> */}
        {/* <button onClick={SpeechRecognition.stopListening}>Stop</button> */}
        {/* <button onClick={testFunc}>test</button> */}
      </div>
    </>
  )
}

export default CustomVoiceGPT

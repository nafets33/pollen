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
import * as faceapi from "@vladmandic/face-api"

const imageUrls = {
  hoots: "/hoots.png",
  hootsAndHootie: "/hootsAndhootie.png",
}

let timer = null
let g_anwers = []
let firstFace = false

const CustomVoiceGPT = (props) => {
  const { api, kwargs = {} } = props
  const { height, width, show_conversation, text_input, no_response_time } =
    kwargs
  const [imageSrc, setImageSrc] = useState(kwargs.self_image)
  const [message, setMessage] = useState("")
  const [answers, setAnswers] = useState([])
  const [listenAfterRelpy, setListenAfterReply] = useState(false)
  const [modelsLoaded, setModelsLoaded] = React.useState(false)
  const [captureVideo, setCaptureVideo] = React.useState(false)

  const videoRef = React.useRef()
  const videoHeight = 480
  const videoWidth = 640
  const canvasRef = React.useRef()

  React.useEffect(() => {
    const loadModels = async () => {
      const MODEL_URL = process.env.PUBLIC_URL + "/models"

      Promise.all([
        faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
        faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
        faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL),
        faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL),
      ]).then(setModelsLoaded(true))
    }
    loadModels()
  }, [])

  const startVideo = () => {
    setCaptureVideo(true)
    navigator.mediaDevices
      .getUserMedia({ video: { width: 300 } })
      .then((stream) => {
        let video = videoRef.current
        video.srcObject = stream
        video.play()
      })
      .catch((err) => {
        console.error("error:", err)
      })
  }

  const handleVideoOnPlay = () => {
    setInterval(async () => {
      if (canvasRef && canvasRef.current) {
        canvasRef.current.innerHTML = faceapi.createCanvasFromMedia(
          videoRef.current
        )
        const displaySize = {
          width: videoWidth,
          height: videoHeight,
        }

        faceapi.matchDimensions(canvasRef.current, displaySize)

        const detections = await faceapi
          .detectAllFaces(
            videoRef.current,
            new faceapi.TinyFaceDetectorOptions()
          )
          .withFaceLandmarks()
          .withFaceExpressions()

        const resizedDetections = faceapi.resizeResults(detections, displaySize)
        console.log("resizedDetections :>> ", resizedDetections)
        if (resizedDetections.length > 0 && !firstFace) {
          firstFace = true
          if (kwargs.hello_audio) {
            const audio = new Audio(kwargs.hello_audio)
            audio.play()
          }
        }
        canvasRef &&
          canvasRef.current &&
          canvasRef.current
            .getContext("2d")
            .clearRect(0, 0, videoWidth, videoHeight)
        canvasRef &&
          canvasRef.current &&
          faceapi.draw.drawDetections(canvasRef.current, resizedDetections)
        canvasRef &&
          canvasRef.current &&
          faceapi.draw.drawFaceLandmarks(canvasRef.current, resizedDetections)
        canvasRef &&
          canvasRef.current &&
          faceapi.draw.drawFaceExpressions(canvasRef.current, resizedDetections)
      }
    }, 300)
  }

  const closeWebcam = () => {
    videoRef.current.pause()
    videoRef.current.srcObject.getTracks()[0].stop()
    setCaptureVideo(false)
  }
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

  const myFunc = async (ret, command) => {
    console.log("ret :>> ", ret)
    setMessage(` (${command["api_body"]["keyword"]}) ${ret},`)
    const text = [...g_anwers, { user: command["api_body"]["keyword"] + ret }]
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
      data["self_image"] && setImageSrc(data["self_image"])
      data["listen_after_reply"] &&
        setListenAfterReply(data["listen_after_reply"])
      setAnswers(data["text"])
      g_anwers = [...data["text"]]
      if (data["audio_path"]) {
        const audio = new Audio(data["audio_path"])
        audio.play()
      }
    } catch (error) {
      // console.log("api call on listen failded!")
    }
  }
  const commands = useMemo(() => {
    return kwargs["commands"].map((command) => ({
      command: command["keywords"],
      callback: (ret) => {
        timer && clearTimeout(timer)
        timer = setTimeout(() => myFunc(ret, command), 1000)
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
        <img src={imageSrc} height={height || 100} width={width || 100} />
        <Dictaphone
          commands={commands}
          myFunc={myFunc}
          listenAfterRelpy={listenAfterRelpy}
          noResponseTime={no_response_time}
          show_conversation={show_conversation}
        />
        <button onClick={listenContinuously}>Listen continuously</button>
        {show_conversation === true && (
          <>
            <div> You: {message}</div>
            {answers.map((answer, idx) => (
              <div key={idx}>
                <div>-user: {answer.user}</div>
                <div>-resp: {answer.resp ? answer.resp : "thinking..."}</div>
              </div>
            ))}
          </>
        )}
      </div>
      <div>
        {/* <button onClick={listenOnce}>Listen Once</button> */}
        {/* <button onClick={listenContinuouslyInChinese}></button> */}
        {/* <button onClick={SpeechRecognition.stopListening}>Stop</button> */}
        {/* <button onClick={testFunc}>test</button> */}
      </div>
      <div>
        <div style={{ textAlign: "center", padding: "10px" }}>
          {captureVideo && modelsLoaded ? (
            <button
              onClick={closeWebcam}
              style={{
                cursor: "pointer",
                backgroundColor: "green",
                color: "white",
                padding: "15px",
                fontSize: "25px",
                border: "none",
                borderRadius: "10px",
              }}
            >
              Close Webcam
            </button>
          ) : (
            <button
              onClick={startVideo}
              style={{
                cursor: "pointer",
                backgroundColor: "green",
                color: "white",
                padding: "15px",
                fontSize: "25px",
                border: "none",
                borderRadius: "10px",
              }}
            >
              Open Webcam
            </button>
          )}
        </div>
        {captureVideo ? (
          modelsLoaded ? (
            <div>
              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                  padding: "10px",
                }}
              >
                <video
                  ref={videoRef}
                  height={videoHeight}
                  width={videoWidth}
                  onPlay={handleVideoOnPlay}
                  style={{ borderRadius: "10px" }}
                />
                <canvas ref={canvasRef} style={{ position: "absolute" }} />
              </div>
            </div>
          ) : (
            <div>loading...</div>
          )
        ) : (
          <></>
        )}
      </div>
    </>
  )
}

export default CustomVoiceGPT

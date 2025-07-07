import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
// import { Streamlit } from "streamlit-component-lib";
import SpeechRecognition from "react-speech-recognition";
import Dictaphone from "./Dictaphone";
import MediaDisplay from "./MediaDisplay";
import './spinner.css';
import ReactMarkdown from 'react-markdown';

// import Dictaphone_ss from "./Dictaphone_ss";
// import * as faceapi from "@vladmandic/face-api";
// import DOMPurify from 'dompurify';

let timer = null;
let faceTimer = null;
let g_anwers = [];
let firstFace = false;

const CustomVoiceGPT = (props) => {
  const { api, kwargs = {} } = props;
  const {
    commands,
    height,
    width,
    show_video,
    input_text,
    no_response_time,
    face_recon,
    api_key,
    refresh_ask,
    self_image,
    api_audio,
    client_user,
    force_db_root,
    before_trigger,
    agent_actions,
  } = kwargs;
  const [imageSrc, setImageSrc] = useState(kwargs.self_image);
  const [imageSrc_name, setImageSrc_name] = useState(kwargs.self_image);

  const [message, setMessage] = useState("");
  const [answers, setAnswers] = useState([]);
  const [listenAfterReply, setListenAfterReply] = useState(false);

  const [modelsLoaded, setModelsLoaded] = useState(false);
  const [captureVideo, setCaptureVideo] = useState(false);
  const [textString, setTextString] = useState("");
  const [apiInProgress, setApiInProgress] = useState(false); // Added state for API in progress
  const [speaking, setSpeakingInProgress] = useState(false); // Added state for API in progresslistening
  const [listening, setlistening] = useState(false); // Added state for API in progress

  const [show_conversation, setshow_conversation] = useState(true); // Added state for API in progress
  

  const [listenButton, setlistenButton] = useState(false); // Added state for API in progress
  const [session_listen, setsession_listen] = useState(false);
  const [convo_button, setconvo_button] = useState(false); // Added state for API in progress

  const [before_trigger_vars, before_trigger_] = useState(kwargs.before_trigger); 
  const faceData = useRef([]);
  const faceTriggered = useRef(false);
  const videoRef = useRef();
  const videoHeight = 480;
  const videoWidth = 640;
  const canvasRef = useRef();
  const audioRef = useRef(null);
  

  const [UserUsedChatWindow, setUserUsedChatWindow] = useState(false);
  const [buttonName, setButtonName] = useState("Click and Ask");
  const [buttonName_listen, setButtonName_listen] = useState("Listening");

  const [showImage, setShowImage] = useState(false); // Step 1: Define showImage state
  const [selectedActions, setSelectedActions] = useState([]);

  

  const toggleShowImage = () => { // Step 2: Create toggle function
    setShowImage((prevShowImage) => !prevShowImage);
  };

  const [windowWidth, setWindowWidth] = useState(0); // Initial value

    // Create a reusable function for getting the window width
    const updateWindowWidth = () => {
      if (typeof window !== 'undefined') {
          setWindowWidth(window.innerWidth);
      }
  };

  // Call the function on component mount to set the initial window width
  useEffect(() => {
      updateWindowWidth();
  }, []);

  useEffect(() => {
    if (self_image) {
      // Fetch the image data from the API endpoint
      fetchImageData(self_image);
    }
  }, [self_image]);

  const fetchImageData = async (imageUrl) => {
    try {
      const response = await axios.get(`${api_audio}${imageUrl}`, {
        responseType: 'blob', // Set responseType to 'blob' to handle file response
      });
      const objectUrl = URL.createObjectURL(response.data); // Use a different variable name here
      setImageSrc(objectUrl);
      setImageSrc_name(imageUrl)
    } catch (error) {
      console.error('Error fetching image data:', error);
    }
  };



  const stopListening = () => {
    setlistening(false);
    SpeechRecognition.stopListening();
    console.log("Stopping Listening, isListening=", listening)
  }

  const listenContinuously = () =>{
    setlistening(true)
    SpeechRecognition.startListening({
      continuous: true,
      language: "en-GB",
    })

}


const convo_mode = () => {
  console.log("listening?", listening);
  if (!listening) {
    console.log("Starting to listen...");
    setconvo_button(true)
    listenContinuously();
  } else {
    console.log("Stopping listening...");
    setconvo_button(false)
    stopListening();
  }
};

useEffect(() => {
  if (listening) {
    console.log("Listening has started");
  } else {
    console.log("Listening has stopped");
  }
}, [listening]);


  const listenSession = () =>{
    if (session_listen) {
    setsession_listen(false)
  }
  else{
    setsession_listen(true)
  }
    }

  // useEffect(() => {
  //   const loadModels = async () => {
  //     const MODEL_URL = process.env.PUBLIC_URL + "/models";

  //     Promise.all([
  //       faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
  //       faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
  //       faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL),
  //       faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL),
  //       faceapi.nets.ageGenderNet.loadFromUri(MODEL_URL),
  //     ]).then(() => setModelsLoaded(true));
  //   };
  //   loadModels();
  //   const interval = setInterval(() => {
  //     // console.log("faceData.current :>> ", faceData.current);
  //   }, 3000);
  //   return () => clearInterval(interval);
  // }, []);


  const handleInputText = (event) => {
    // Update the state with the input text
    setTextString(event.target.value);
  
    // Set a variable to indicate that the user used the chat window
    setUserUsedChatWindow(true);
  };

  const handleOnKeyDown = (e) => {
    if (e.key === "Enter") {
      console.log("textString :>> ", textString);
      myFunc(textString, { api_body: { keyword: "" } }, 4);
      setTextString("");
    }
  };

  // const startVideo = () => {
  //   setCaptureVideo(true);
  //   navigator.mediaDevices
  //     .getUserMedia({ video: { width: 300 } })
  //     .then((stream) => {
  //       let video = videoRef.current;
  //       video.srcObject = stream;
  //       video.play();
  //     })
  //     .catch((err) => {
  //       console.error("error:", err);
  //     });
  // };

  // const handleVideoOnPlay = () => {
  //   setInterval(async () => {
  //     if (canvasRef && canvasRef.current) {
  //       canvasRef.current.innerHTML = faceapi.createCanvasFromMedia(
  //         videoRef.current
  //       );
  //       const displaySize = {
  //         width: videoWidth,
  //         height: videoHeight,
  //       };

  //       faceapi.matchDimensions(canvasRef.current, displaySize);

  //       const detections = await faceapi
  //         .detectAllFaces(
  //           videoRef.current,
  //           new faceapi.TinyFaceDetectorOptions()
  //         )
  //         .withFaceLandmarks()
  //         .withFaceExpressions();

  //       const resizedDetections = faceapi.resizeResults(detections, displaySize);

  //       if (resizedDetections.length > 0) {
  //         faceData.current = resizedDetections;
  //         if (!faceTriggered.current && face_recon) {
  //           myFunc("", { api_body: { keyword: "" } }, 2);
  //           faceTriggered.current = true;
  //         }
  //       } else {
  //         faceTimer && clearTimeout(faceTimer);
  //         setTimeout(() => {
  //           faceData.current = [];
  //         }, 1000);
  //       }

  //       if (resizedDetections.length > 0 && !firstFace) {
  //         firstFace = true;
  //         if (kwargs.hello_audio) {
  //           const audio = new Audio(kwargs.hello_audio);
  //           audio.play();
  //         }
  //       }

  //       canvasRef &&
  //         canvasRef.current &&
  //         canvasRef.current
  //           .getContext("2d")
  //           .clearRect(0, 0, videoWidth, videoHeight);
  //       canvasRef &&
  //         canvasRef.current &&
  //         faceapi.draw.drawDetections(canvasRef.current, resizedDetections);
  //       canvasRef &&
  //         canvasRef.current &&
  //         faceapi.draw.drawFaceLandmarks(canvasRef.current, resizedDetections);
  //       canvasRef &&
  //         canvasRef.current &&
  //         faceapi.draw.drawFaceExpressions(
  //           canvasRef.current,
  //           resizedDetections
  //         );
  //     }
  //   }, 300);
  // };

  // const closeWebcam = () => {
  //   videoRef.current.pause();
  //   videoRef.current.srcObject.getTracks()[0].stop();
  //   setCaptureVideo(false);
  // };

  const click_listenButton = () => {
    setlistenButton(true)
    if (!listening) {
      listenContinuously()
    }
    setButtonName("Please Speak")
    console.log("listening button listen click");
    console.log(listenButton);
  };


  const myFunc = async (ret, command, type) => {
    setMessage(` (${command["api_body"]["keyword"]}) ${ret},`);
    const text = [...g_anwers, { user: ret }];
    setAnswers([...text]);
    try {
      console.log("api call on listen...", command);
      setApiInProgress(true); // Set API in progress to true
      stopListening()

      const body = {
        tigger_type: type,
        api_key: api_key,
        text: text,
        self_image: imageSrc_name,
        face_data: faceData.current,
        refresh_ask: refresh_ask,
        client_user: client_user,
        force_db_root:force_db_root,
        session_listen:session_listen,
        before_trigger_vars:before_trigger_vars,
        selected_actions: selectedActions,
      };
      console.log("api");
      const { data } = await axios.post(api, body);
      console.log("data :>> ", data, body);
      if (data["self_image"] && data["self_image"] !== imageSrc_name) {
        fetchImageData(data["self_image"]); // Fetch image data if it's different
      }
      setAnswers(data["text"]);
      g_anwers = [...data["text"]];
      
      if (audioRef.current) {
        audioRef.current.pause(); // Pause existing playback if any
      }

      if (data["audio_path"]) {
        const apiUrlWithFileName = `${api_audio}${data["audio_path"]}`;
        audioRef.current = new Audio(apiUrlWithFileName);
    
        try {
            await audioRef.current.play();
            
            // Set state to indicate speaking in progress
            setSpeakingInProgress(true);
            setButtonName_listen("Speaking");
    
            // Await playback completion
            await new Promise((resolve) => {
                audioRef.current.onended = () => {
                    console.log("Audio playback finished.");
                    resolve();
                };
            });
    
        } catch (error) {
            console.error("Audio playback error:", error);
        } finally {
            // Cleanup or reset after playback
            audioRef.current = null;
            setSpeakingInProgress(false);
            setButtonName_listen("Listen");
        }
    }

      setButtonName("Click and Ask")
      setButtonName_listen("Listening")
      setSpeakingInProgress(false)
      setApiInProgress(false)

      
      setListenAfterReply(data["listen_after_reply"]);
      console.log("listen after reply", data["listen_after_reply"], listenAfterReply);



      if (data["page_direct"] !== false && data["page_direct"] !== null) {
        console.log("api has page direct", data["page_direct"]);
        // window.location.reload();
        window.location.href = data["page_direct"];
      }

      if (UserUsedChatWindow) {
        setUserUsedChatWindow(false)
      }
      else if (listenAfterReply==true) {
        console.log("API END HIT listenAfterReply==TRUE")
        setButtonName_listen("Awaiting your Answer please speak")
      }
      else if (listenButton) {
      setlistenButton(false)
      }
      else if (convo_button){
        console.log("convo mode")
        listenContinuously()
      }

      
    } catch (error) {
      console.log("api call on listen failed!", error);
      setApiInProgress(false); // Set API in progress to false on error
      setlistenButton(false)
    }

    updateWindowWidth();
    console.log("ReSize Window")
  };
  
  const background_color_chat = refresh_ask?.color_dict?.background_color_chat || 'transparent';
  const splitImage = self_image.split('.')[0]; // Split by dot
  const placeholder = `Chat with ${splitImage}`;
  console.log("session_listen", session_listen)


  return (
    <>

      <div className="p-2">
        <div style={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
          {/* Image or video section */}
          <div>
            {/* Media Display */}
            <MediaDisplay
              showImage={showImage}
              imageSrc={imageSrc}
              largeHeight={100}   // Customize as needed
              largeWidth={100}    // Customize as needed
              smallHeight={40}    // Customize as needed
              smallWidth={40}     // Customize as needed
            />
          </div>
  
          {/* Chat window, taking full width if no image is shown */}
          <div style={{ flex: showImage ? 1 : '100%', overflowY: 'auto', maxHeight: '350px' }}>
            {show_conversation && (
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  maxHeight: '350px',
                  height: '350px',
                  overflowY: 'auto',
                  border: '1px solid #ccc',
                  padding: '10px',
                }}
              >
                {answers.map((answer, idx) => (
                  <div
                    key={idx}
                    className="chat-message-container"
                    style={{
                      marginBottom: '5px',
                      padding: '5px',
                      borderRadius: '4px',
                      border: '1px solid #ccc',
                      boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                    }}
                  >
                    <div
                      className="chat-user"
                      style={{
                        backgroundColor: '#e4eafe',
                        textAlign: 'right',
                        marginLeft: 'auto',
                        padding: '5px',
                      }}
                    >
                      {client_user}: <span>{answer.user}</span>
                    </div>
                    <div
                      className="chat-response-container"
                      style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        backgroundColor: background_color_chat,
                        padding: '10px',
                      }}
                    >
                      {imageSrc && (
                        <div className="chat-image" style={{ marginRight: '10px' }}>
                          <img src={imageSrc} alt="response" style={{ width: '50px' }} />
                        </div>
                      )}
              <div
                className="chat-response-text"
                style={{ flex: 1, wordBreak: 'break-word' }}
              >
                {answer.resp
                  ? <span dangerouslySetInnerHTML={{ __html: answer.resp }} />
                  : <span className="spinner" />}
              </div>
            </div>
          </div>
        ))}
      </div>
    )}
  </div>
</div>

        {/* Input text section */}
        {input_text && (
          <>
          <hr style={{ margin: '3px 0' }} />
            <div className="form-group">
              <input
                className="form-control"
                type="text"
                placeholder={placeholder}
                value={textString}
                onChange={handleInputText}
                onKeyDown={handleOnKeyDown}
              />

            </div>
            <hr style={{ margin: '3px 0' }} />
          </>
        )}


      {/* Buttons with indicators under each */}
      <div style={{ display: 'flex', marginTop: '3px' }}>
        {/* Button 1 with Listen Indicator */}
        <div style={{ flex: 1, textAlign: 'center' }}>
          <button
            style={{
              fontSize: '12px',
              padding: '5px',
              margin: '5px 0',
              backgroundColor: listenButton ? '#478728': "rgb(196, 230, 252)",
              color: 'black',
              border: '1px solid #2980b9',
              borderRadius: '4px',
              cursor: 'pointer',
              width: '89%',
            }}
            onClick={click_listenButton}
          >
            {buttonName}
          </button>

        </div>

        {/* Button 2 with Conversational Mode Indicator */}
        <div style={{ flex: 1, textAlign: 'center' }}>
          <button
            style={{
              fontSize: '12px',
              padding: '5px',
              margin: '5px 0',
              backgroundColor: convo_button ? "rgb(87, 188, 100)": "rgb(196, 230, 252)",
              color: 'black',
              border: '1px solid #2980b9',
              borderRadius: '4px',
              cursor: 'pointer',
              width: '89%',
            }}
            onClick={convo_mode}
          >
            {convo_button ? "End Conversation" : "Start Conversation"}
          </button>
          
          {listening && (
                          <div
                            style={{
                              width: '89%',
                              height: '10px',
                              backgroundImage: 'linear-gradient(90deg, green, transparent 50%, green)',
                              animation: 'flashLine 1s infinite',
                              marginTop: '5px',
                            }}
                          >
                            <div style={{ fontSize: '12px', color: 'black' }}>{buttonName_listen}</div>
                          </div>
                        )}

          {speaking && (
            <div
              style={{
                // width: '89%',
                height: '10px',
                background: 'linear-gradient(to right, blue, transparent, purple)',
                animation: 'waveAnimation 1s infinite',
                marginTop: '5px',
                borderRadius: '10px',
              }}
            >
              <div style={{ fontSize: '12px', color: 'black' }}>Speaking</div>
            
            </div>
          )}
        </div>

        {/* Button 3 with Session Started Indicator */}

        <div style={{ flex: 1, textAlign: 'center' }}>
          <button
            style={{
              fontSize: '12px',
              padding: '5px',
              margin: '5px 0',
              backgroundColor: session_listen ? "rgb(250, 234, 131)": "rgb(196, 230, 252)",
              color: 'black',
              border: '1px solid #2980b9',
              borderRadius: '1px',
              cursor: 'pointer',
              width: '89%',
            }}
            onClick={listenSession}
          >
            {session_listen ? "Stop Session" : "Start Session"}
          </button>
          {session_listen && (
            <div
              style={{
                width: '89%',
                height: '10px',
                backgroundImage: 'linear-gradient(90deg, orange, transparent 50%, orange)',
                animation: 'flashLine 1s infinite',
                marginTop: '5px',
              }}
            >
              <div style={{ fontSize: '12px', color: 'black' }}>Session Started</div>
            </div>
          )}
        </div>

      </div>

    {/* Agent Actions Horizontal Button-Style Multi-Select */}
    {Array.isArray(agent_actions) && agent_actions.length > 0 && (
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          marginTop: '8px',
          gap: '6px',
        }}
      >
        {agent_actions.map((action, idx) => {
          const selected = selectedActions.includes(action);
          return (
            <button
              key={idx}
              onClick={() => {
                if (selected) {
                  setSelectedActions(selectedActions.filter((a) => a !== action));
                } else {
                  setSelectedActions([...selectedActions, action]);
                }
              }}
              style={{
                fontSize: '12px',
                padding: '5px 10px',
                backgroundColor: selected ? '#1abc9c' : '#ecf0f1',
                color: selected ? 'white' : 'black',
                border: '1px solid #bdc3c7',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              {action}
            </button>
          );
        })}
      </div>
    )}


        {/* Dictaphone component */}
        <div className="p-2" style={{ marginBottom: '15px' }}>
          <Dictaphone
            commands={commands}
            myFunc={myFunc}
            listenAfterReply={listenAfterReply}
            no_response_time={no_response_time}
            apiInProgress={apiInProgress}
            listenButton={listenButton}
            session_listen={session_listen}
            listening={listening}
          />
        </div>
  

      </div>



    </>
  );
}

export default CustomVoiceGPT;

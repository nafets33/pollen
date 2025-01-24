import React, { useState, useEffect } from "react";
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

const Dictaphone = ({
  commands,
  myFunc,
  listenAfterReply = false,
  no_response_time = 3,
  apiInProgress = false,
  listenButton = false,
  session_listen = false,
}) => {
  const {
    finalTranscript,
    interimTranscript,
    resetTranscript,
    listening,
    browserSupportsSpeechRecognition,
    isMicrophoneAvailable,
  } = useSpeechRecognition();
  
  const [show_transcript, setShowTranscript] = useState(true);

  const showTranscript_func = () => setShowTranscript((prev) => !prev);
  const clearTranscript_func = () => resetTranscript();

  useEffect(() => {
    if (finalTranscript !== "") {
      console.log("Got final result:", finalTranscript);
      console.log("Listening?", listening);
      console.log("listenAfterReply:", listenAfterReply);

      // Clear the previous script if a keyword is found or if the transcript exceeds limits
      if (session_listen && finalTranscript.split(" ").length > 500000) {
        console.log("Transcript exceeds X words");
        for (let i = 0; i < commands.length; i++) {
          myFunc(finalTranscript, commands[i], 6);
        }
        resetTranscript();
        return;
      }

      if (!session_listen && finalTranscript.split(" ").length > 10000) {
        console.log("Transcript exceeds 10000 words. Clearing.");
        resetTranscript();
        return;
      }

      // Clear any existing timers to prevent multiple triggers
      const timer = setTimeout(() => {
        // Check if user is still speaking
        if (interimTranscript) {
          console.log("User is still speaking, resetting timer...");
          return; // Reset timer and do not trigger API
        }

        // Proceed to check for keywords
        for (let i = 0; i < commands.length; i++) {
          const { keywords, api_body } = commands[i];
          for (let j = 0; j < keywords.length; j++) {
            const keyword = new RegExp(keywords[j], "i");
            const isKeywordFound = finalTranscript.search(keyword) !== -1;

            if ((isKeywordFound || listenAfterReply || listenButton) && !apiInProgress) {
              if (listenAfterReply) {
                myFunc(finalTranscript, { api_body: { keyword: "" } }, 3);
              } else if (isKeywordFound) {
                myFunc(finalTranscript, commands[i], 1);
              } else if (listenButton) {
                myFunc(finalTranscript, commands[i], 5);
              }
              resetTranscript();
              return;
            }
          }
        }
        console.log("Waiting for a keyword");
      }, no_response_time * 1000);

      return () => clearTimeout(timer); // Clear the timer on component unmount or when useEffect runs again
    }
  }, [finalTranscript, interimTranscript, listening, listenAfterReply, commands, no_response_time, resetTranscript, apiInProgress, listenButton]);

  if (!browserSupportsSpeechRecognition) {
    return <span>No browser support</span>;
  }

  if (!isMicrophoneAvailable) {
    return <span>Please allow access to the microphone</span>;
  }

  return (
    <>
      {show_transcript && (
        <div style={{ display: "flex", flexDirection: "column", maxHeight: "250px", height: '250px', overflowY: "auto", border: "1px solid #ccc", padding: "10px" }}>
          <span>You said: {finalTranscript || interimTranscript}</span>
          <span>Listening: {listening ? "on" : "off"}</span>
        </div>
      )}
      <button onClick={showTranscript_func} style={{ marginTop: "10px" }}>
        {show_transcript ? "Hide Transcript" : "Show Transcript"}
      </button>
      <button onClick={clearTranscript_func} style={{ marginTop: "10px" }}>
        Clear Transcript
      </button>
    </>
  );
};

export default Dictaphone;

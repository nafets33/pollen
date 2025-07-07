import React, { useState, useEffect, useRef } from "react";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";

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

  const [editableTranscript, setEditableTranscript] = useState(""); // State for editable transcript
  const [show_transcript, setShowTranscript] = useState(true);

  const showTranscript_func = () => setShowTranscript((prev) => !prev);
  const clearTranscript_func = () => {
    resetTranscript();
    setEditableTranscript(""); // Clear editable transcript
  };
  const textareaRef = useRef(null);
  const cursorPosRef = useRef(null);
  // Logic to process transcript based on session_listen
  const processTranscript = () => {
    if (finalTranscript !== "") {
      // console.log("Listening?", listening);
      // console.log("listenAfterReply:", listenAfterReply);
      // console.log("session_listen:", session_listen);
      // console.log("apiInProgress:", apiInProgress);
  
      if (listenButton) {
      // When session_listen is false and not using listenButton, just append
      myFunc(finalTranscript, { api_body: {} }, 5);
      setEditableTranscript((prev) => `${prev} ${finalTranscript}`.trim());
      resetTranscript();
      setEditableTranscript("");
      return;
      }


      if (session_listen) {
        // Check for keywords only when session_listen is true
        let keywordFound = false;
        for (let i = 0; i < commands.length; i++) {
          const { keywords, api_body } = commands[i];
          for (let j = 0; j < keywords.length; j++) {
            const keyword = new RegExp(keywords[j], "i");
            const isKeywordFound = finalTranscript.search(keyword) !== -1;
  
            if (isKeywordFound && !apiInProgress) {
              console.log(`Keyword found: ${keywords[j]}`);
              myFunc(finalTranscript, commands[i], 1);
              resetTranscript(); // Reset transcript after processing keyword
              setEditableTranscript(""); // Clear editable transcript state
              keywordFound = true;
              return;
            }
          }
        }
  
        if (!keywordFound) {
          // Append transcript if no keyword is found
          setEditableTranscript((prev) => `${prev} ${finalTranscript}`.trim());
          resetTranscript(); // Clear finalTranscript after appending
        }
      } else {
        // When session_listen is false, focus on capturing speech-to-text
        if (textareaRef.current) {
          cursorPosRef.current = textareaRef.current.selectionStart;
        }

        console.log("Recording speech-to-text without keyword triggers");
        setEditableTranscript((prev) => `${prev} ${finalTranscript}`.trim());
        resetTranscript(); // Clear finalTranscript after appending
      }
    }
  };

  // Use processTranscript in useEffect to handle updates
  useEffect(() => {
    processTranscript();
  }, [finalTranscript]);

  const handleTranscriptChange = (e) => {
    setEditableTranscript(e.target.value); // Update editable transcript based on user input
  };

  useEffect(() => {
    if (textareaRef.current && cursorPosRef.current !== null) {
      textareaRef.current.selectionStart = cursorPosRef.current;
      textareaRef.current.selectionEnd = cursorPosRef.current;
      cursorPosRef.current = null;
    }
    }, [editableTranscript]);


  if (!browserSupportsSpeechRecognition) {
    return <span>No browser support</span>;
  }

  if (!isMicrophoneAvailable) {
    return <span>Please allow access to the microphone</span>;
  }

  return (
    <>
      <div style={{ display: "flex", gap: "10px", marginBottom: "10px" }}>
        <button
          onClick={() => {
            myFunc(editableTranscript, { api_body: {} }, 5);
            resetTranscript();
            setEditableTranscript("");
          }}
          style={{
            backgroundColor: "rgb(196, 230, 252)",
            color: "black",
            border: "none",
            padding: "10px 20px",
            borderRadius: "5px",
            cursor: "pointer",
          }}
        >
          Send Transcript
        </button>
        <button
          onClick={showTranscript_func}
          style={{
            backgroundColor: "white",
            color: "grey",
            border: "none",
            padding: "10px 20px",
            borderRadius: "5px",
            cursor: "pointer",
          }}
        >
          {show_transcript ? "Hide Transcript" : "Show Transcript"}
        </button>
        <button
          onClick={clearTranscript_func}
          style={{
            backgroundColor: "white",
            color: "grey",
            border: "none",
            padding: "10px 20px",
            borderRadius: "5px",
            cursor: "pointer",
          }}
        >
          Clear Transcript
        </button>
      </div>
      {show_transcript && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            maxHeight: "800px",
            height: "550px",
            overflowY: "auto",
            border: "1px solid #ccc",
            padding: "10px",
          }}
        >
          <span>
            <strong>Listening:</strong> {listening ? "on" : "off"}
          </span>
          <span>
            <strong>Transcript:</strong>
          </span>
      {/* Live preview of interim transcript */}
        {interimTranscript && (
          <div style={{ color: "#888", fontStyle: "italic", marginBottom: "8px" }}>
            {interimTranscript}
          </div>
        )}
          <textarea
            ref={textareaRef}
            value={editableTranscript}
            onChange={handleTranscriptChange}
            style={{
              backgroundColor: "rgb(238, 242, 245)",
              color: "black",
              width: "100%",
              height: "550px",
              border: "1px solid #ccc",
              padding: "5px",
              resize: "none",
            }}
          />
        </div>
      )}
    </>
  );
};

export default Dictaphone;
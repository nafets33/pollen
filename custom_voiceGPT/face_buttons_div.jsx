<div>
{face_recon && (
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
)}
{captureVideo ? (
  modelsLoaded ? (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          padding: "10px",
          position: show_video ? "" : "absolute",
          opacity: show_video ? 1 : 0.3,
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

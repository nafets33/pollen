import React, { useEffect, useState } from "react"
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib"
import VoiceGPT from "./VoiceGPT.jsx"

const Main = (props: ComponentProps) => {
  const { api, kwargs } = props.args
  useEffect(() => Streamlit.setFrameHeight())
  return (
    <>
      <VoiceGPT api={api} kwargs={kwargs} />
    </>
  )
}

export default withStreamlitConnection(Main)

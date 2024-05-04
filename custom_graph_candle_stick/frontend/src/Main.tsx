import React, { useEffect, useState } from "react"
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib"
import CandlestickChart from "./CandleStick.jsx"

const Main = (props: ComponentProps) => {
  const { api, kwargs } = props.args
  useEffect(() => Streamlit.setFrameHeight())
  return (
    <>
      <CandlestickChart kwargs={kwargs} />
    </>
  )
}

export default withStreamlitConnection(Main)

import React, { useState, useEffect, FC } from "react"
import axios from "axios"
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib"

type Props = {
  api: string
  text_size?: number
  refresh_sec?: number
  refresh_cutoff_sec?: number
  text_option?: any
  kwargs: any
}

const defaultProps: Props = {
  api: "",
  kwargs: {},
}

const imageUrls = {
  hoots: "/hoots.png",
  hootsAndHootie: "/hootsAndhootie.png",
}

const CustomText: FC<Props> = (props: Props = defaultProps) => {
  const { api, kwargs = {} } = props
  const [imageSrc, setImageSrc] = useState(imageUrls.hoots)
  useEffect(() => Streamlit.setFrameHeight())

  useEffect(() => {}, [props])

  return (
    <span>
      <img src={imageSrc} height={100} />
    </span>
  )
}

export default CustomText

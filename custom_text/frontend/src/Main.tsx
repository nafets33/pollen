import React, { useEffect, useState } from "react";
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib";
import CustomText from "./CustomText";

const Main = (props: ComponentProps) => {
  const { api, text_size, refresh_sec, refresh_cutoff_sec, text_option } = props.args;

  useEffect(() => Streamlit.setFrameHeight());

  return (
    <>
      <CustomText
        api={api}
        text_size={text_size}
        refresh_sec={refresh_sec}
        refresh_cutoff_sec={refresh_cutoff_sec}
        text_option={text_option}
      />
    </>
  );
};

export default withStreamlitConnection(Main);

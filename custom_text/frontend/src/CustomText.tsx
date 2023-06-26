import React, { useState, useEffect, FC } from 'react';
import axios from "axios"
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib";

type Props = {
  api: string,
  text_size?: number,
  refresh_sec?: number,
  refresh_cutoff_sec?: number,
  text_option?: any,
  kwargs: any,
}

const defaultProps: Props = {
  api: "",
  text_size: 10,
  refresh_sec: 1,
  refresh_cutoff_sec: 0,
  kwargs: {},
}

const CustomText: FC<Props> = (props: Props = defaultProps) => {
  const { api, text_size = 10, refresh_sec = 1, refresh_cutoff_sec = 0, text_option = {}, kwargs = {} } = props;
  const [rowData, setRowData] = useState("");
  useEffect(() => Streamlit.setFrameHeight());

  useEffect(() => {
    console.log(props);
    const fetchData = async () => {
      console.log('AAAAAAAAAAAAAAAAAAA :>> ', kwargs);

      axios.post(api, {...kwargs}).then((response) => {
        setRowData(response.data);
      });
    };

    fetchData();
    const interval = setInterval(fetchData, refresh_sec * 1000);
    let timeout: NodeJS.Timeout;
    if (refresh_cutoff_sec > 0) {
      console.log(refresh_cutoff_sec);
      timeout = setTimeout(() => {
        clearInterval(interval);
        console.log("Fetching data ended, refresh rate:", text_option);
      }, refresh_cutoff_sec * 1000);
    }
    console.log("rendered==========", text_option);
    return () => {
      clearInterval(interval);
      if (timeout) clearTimeout(timeout);
    }
  }, [props]);

  return (
    <span
      style={{
        fontSize: text_size,
        backgroundColor: text_option?.background_color,
        color: text_option?.text_color,
        fontStyle: text_option?.font_style
      }}
    >
      {rowData}
    </span>
  );
};

export default CustomText;

import React, { useEffect, useState } from "react";
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib";
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import Aggrid from "./Aggrid";

const Main = (props: ComponentProps) => {

  const { username, api, refresh_sec, refresh_cutoff_sec, gridoption_build, prod } = props.args;

  useEffect(() => Streamlit.setFrameHeight());
  // Add a label and pass min/max variables to the baseui Slider
  return (
    <>
      <Aggrid
        username={username}
        api={api}
        refresh_sec={refresh_sec}
        refresh_cutoff_sec={refresh_cutoff_sec}
        gridoption_build={gridoption_build}
        prod={prod}
      />
    </>
  );
};

export default withStreamlitConnection(Main);

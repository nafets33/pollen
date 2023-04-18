import React, { useEffect, useState } from "react";
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib";
import { Slider } from "baseui/slider";
import { setTimeout } from "timers";
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import axios from "axios";
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

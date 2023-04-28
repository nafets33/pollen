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
  const { api_url, button_name } = props.args;
  console.log(props);
  return (
    <div >
      <Aggrid
        username={username}
        api={api}
        refresh_sec={refresh_sec}
        refresh_cutoff_sec={refresh_cutoff_sec}
        gridoption_build={gridoption_build}
        prod={prod}
        api_url={api_url}
        button_name={button_name}
      />
    </div>
  );
};

export default withStreamlitConnection(Main);

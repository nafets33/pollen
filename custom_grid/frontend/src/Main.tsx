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

  const { username, api, api_update, refresh_sec, refresh_cutoff_sec, gridoption_build, prod } = props.args;
  const { api_url, button_name, grid_options, kwargs } = props.args;
  const { index } = grid_options;
  console.log("AAAAAAAA", grid_options.columnDefs);
  return (
    <div >
      <Aggrid
        username={username}
        api={api}
        api_update={api_update}
        refresh_sec={refresh_sec}
        refresh_cutoff_sec={refresh_cutoff_sec}
        gridoption_build={gridoption_build}
        prod={prod}
        api_url={api_url}
        button_name={button_name}
        grid_options={grid_options}
        index={index}
        kwargs={kwargs}
      />
    </div>
  );
};

export default withStreamlitConnection(Main);

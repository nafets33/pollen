import React, { useEffect, useState } from 'react'
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from 'streamlit-component-lib'
import 'ag-grid-community/styles/ag-grid.css'
// import 'ag-grid-community/styles/ag-theme-alpine.css';
import 'ag-grid-community/styles/ag-theme-balham.css'
import Aggrid from './Aggrid'

const Main = (props: ComponentProps) => {
  const {
    username,
    api,
    api_update,
    refresh_sec,
    refresh_cutoff_sec,
    gridoption_build,
    enable_JsCode,
    prod,
    autoUpdate = false,
  } = props.args
  const { grid_options, kwargs = {} } = props.args
  const { index, theme } = grid_options
  // console.log('GridOptions', grid_options)
  return (
    <div>
      <Aggrid
        username={username}
        api={api}
        api_update={api_update}
        refresh_sec={refresh_sec}
        refresh_cutoff_sec={refresh_cutoff_sec}
        gridoption_build={gridoption_build}
        prod={prod}
        grid_options={grid_options}
        index={index}
        kwargs={kwargs} 
        enable_JsCode={enable_JsCode}      
        autoUpdate={autoUpdate}
      />
    </div>
  )
}

export default withStreamlitConnection(Main)

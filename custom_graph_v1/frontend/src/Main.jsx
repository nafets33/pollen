import React, { Component } from "react"
import CanvasJSReact from "@canvasjs/react-charts"
import moment from "moment"

import toastr from "toastr"
import "toastr/build/toastr.min.css"

import axios from "axios"

import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib"


var CanvasJSChart = CanvasJSReact.CanvasJSChart
var CanvasJS = CanvasJSReact.CanvasJS
const dataPoints = [[], [], [], [], [], [], [], [], [], []]

toastr.options = {
  positionClass: "toast-top-full-width",
  hideDuration: 300,
  timeOut: 3000,
}

class App extends Component {
  constructor(props) {
    super(props)

    this.state = {
      viewId: 0
    }


    this.state = {
      viewId: 0
    }

    this.updateChart = this.updateChart.bind(this)
    this.toggleDataSeries = this.toggleDataSeries.bind(this)
  }
  componentDidMount() {
    const { kwargs } = this.props.args
    const { y_axis, api, y_max, refresh_sec, graph_height } = kwargs
    Streamlit.setFrameHeight()
    this.updateChart()
    if (refresh_sec) setInterval(this.updateChart, refresh_sec * 1000)
  }
  componentDidUpdate(prevState) {
    if (prevState.viewId !== this.state.viewId) {
      this.updateChart()
    }
  }
  componentDidUpdate(prevState) {
    if (prevState.viewId !== this.state.viewId) {
      this.updateChart()
    }
  }
  toggleDataSeries(e) {
    if (typeof e.dataSeries.visible === "undefined" || e.dataSeries.visible) {
      e.dataSeries.visible = false
    } else {
      e.dataSeries.visible = true
    }
    this.chart.render()
  }
  async fetchGraphData() {
    const { kwargs } = this.props.args
    const { y_axis, api, y_max, refresh_sec, toggles } = kwargs;
    const { viewId } = this.state;
    const res = await axios.post(api, { ...kwargs, toggles_selection: toggles ? toggles[viewId] : "none" })
    console.log(
      "toggles[viewId],viewId :>> ",
      toggles[viewId],
      viewId
    )
    console.log(
      "toggles[viewId],viewId :>> ",
      toggles[viewId],
      viewId
    )
    return JSON.parse(res.data)
  }
  async updateChart() {
    const { kwargs } = this.props.args
    const { x_axis, y_axis, api, y_max, refresh_sec, refresh_button, theme_options } = kwargs
    try {
      const data = await this.fetchGraphData()
      const newSeries = []
      y_axis.map((axis, y_index) => {
        return (newSeries[y_index] = data.map((row, index) => {
          return {
            x: index, // Use index as x value instead of datetime
            y: row[axis["field"]],
            timeStamp: row[x_axis["field"]] // Store timestamp for each data point
          }
        }))
      })
  
      while (dataPoints[0].length) {
        y_axis.map((item, index) => {
          dataPoints[index].pop()
        })
      }
  
      y_axis.map((item, index) => {
        dataPoints[index].push(...newSeries[index])
        this.chart.options.data[index].legendText =
          item["name"] + newSeries[index].pop().y
      })
  
      // Update x-axis label formatter to display actual timestamps
      this.chart.options.axisX.labelFormatter = function (e) {
        const dataPoint = dataPoints[0][e.value];
        return moment(dataPoint.timeStamp).format("MM/DD/YY hh");
      };
  
      this.chart.render()
      refresh_button && !refresh_sec && toastr.success(`Success!`)
    } catch (error) {
      refresh_button &&
        !refresh_sec &&
        toastr.error(`Fetch Error: ${error.message}`)
    }
  }
  render() {
    console.log(this.props, 'kwargs');
    const colorSet = []
    const { kwargs } = this.props.args;
    console.log(this.props);
    const {viewId} = this.state;
    console.log(kwargs);
    const { y_axis, api, y_max, refresh_sec, theme_options, refresh_button, toggles } =
      kwargs
    const dataY = y_axis.map((item, index) => {
      colorSet.push(item["color"])
      return {
        type: "spline",
        xValueFormatString: "#.##0 ",
        yValueFormatString: "#.##0",
        showInLegend: theme_options["showInLegend"],
        name: item["name"],
        dataPoints: dataPoints[index],
        // lineColor: item['color'] ? item['color'] : ''
      }
    })
    CanvasJS.addColorSet("greenShades", colorSet)
    const options = {
      colorSet: "greenShades",
      backgroundColor: theme_options["backgroundColor"]
        ? theme_options["backgroundColor"]
        : "white",
      zoomEnabled: true,
      title: {
        text: theme_options["main_title"] ? theme_options["main_title"] : "",
      },
      axisX: {
        title: theme_options["x_axis_title"]
          ? theme_options["x_axis_title"]
          : "",
        labelFormatter: (e) => moment(e.value).format("MM/DD/YY hh"),
        labelFontSize: 12,
      },
      axisY: {
        suffix: "",
        maximum: y_max ? y_max : null,
        gridColor: theme_options["grid_color"]
          ? theme_options["grid_color"]
          : "",
      },
      toolTip: {
        shared: true,
        contentFormatter: function (e) {
          let content = "";
    
          // Format the x-axis time and add it to the tooltip content
          const formattedXValue = moment(e.entries[0].dataPoint.timeStamp).format("MM/DD/YY HH:mm");
          content += `<strong>Date</strong>: ${formattedXValue}<br/>`;
    
          // Loop through other data points (excluding the x-axis time) and add them to the tooltip content
          for (let i = 1; i < e.entries.length; i++) {
            const entry = e.entries[i];
            const dataSeries = entry.dataSeries;
            const dataPoint = entry.dataPoint;
            const color = dataSeries.color ? dataSeries.color : dataSeries.options.color;
            content += `<strong style="color: ${color}">${dataSeries.name}</strong>: ${dataPoint.y}<br/>`;
          }
    
          return content;
        }
      },
      legend: {
        cursor: "pointer",
        verticalAlign: "top",
        fontSize: 18,
        fontColor: "dimGrey",
        itemclick: this.toggleDataSeries,
      },
      data: dataY,
      height: kwargs.graph_height ? kwargs.graph_height : 400,
    }
    return (
      <div>
        {refresh_button && !refresh_sec && (
          <div style={{ display: "flex" }}>
            <div style={{ margin: "10px 10px 10px 2px" }}>
              <button className="btn btn-warning" onClick={this.updateChart}>
                Refresh
              </button>
            </div>
          </div>
        )}
        <CanvasJSChart options={options} onRef={(ref) => (this.chart = ref)} />
        <div className="d-flex flex-row gap-6">
            {toggles?.map((view, index) => (
              <span className="">
                <button
                  className={`btn ${
                    viewId == index ? "btn-danger" : "btn-secondary"
                  }`}
                  onClick={() => this.setState({ viewId: index })}
                >
                  {view}
                </button>
              </span>
            ))}
          </div>
      </div>
    )
  }
}

export default withStreamlitConnection(App)
import React, { Component } from 'react';
import CanvasJSReact from '@canvasjs/react-charts';

import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib";

import toastr from 'toastr';
import 'toastr/build/toastr.min.css';

import axios from 'axios';

var CanvasJSChart = CanvasJSReact.CanvasJSChart;
var CanvasJS = CanvasJSReact.CanvasJS;
const dataPoints = [[], [], [], [], [], [], [], [], [], []];

toastr.options = {
  positionClass: 'toast-top-full-width',
  hideDuration: 300,
  timeOut: 3000,
};

class App extends Component {

  constructor(props) {
    super(props);
    this.updateChart = this.updateChart.bind(this);
    this.toggleDataSeries = this.toggleDataSeries.bind(this);
  }
  componentDidMount() {
    const { kwargs } = this.props.args;
    const { y_axis, api, y_max, refresh_sec,graph_height } = kwargs;
    Streamlit.setFrameHeight();
    this.updateChart();
    if (refresh_sec)
      setInterval(this.updateChart, refresh_sec * 1000);
  }
  toggleDataSeries(e) {
    if (typeof (e.dataSeries.visible) === "undefined" || e.dataSeries.visible) {
      e.dataSeries.visible = false;
    }
    else {
      e.dataSeries.visible = true;
    }
    this.chart.render();
  }
  async fetchGraphData() {
    const { kwargs } = this.props.args;
    const { y_axis, api, y_max, refresh_sec } = kwargs;
    const res = await axios.post(api, { ...kwargs });
    return JSON.parse(res.data);
  }
  async updateChart() {
    const { kwargs } = this.props.args;
    const { x_axis, y_axis, api, y_max, refresh_sec, refresh_button } = kwargs;
    try {
      const data = await this.fetchGraphData();
      const newSeries = [];
      y_axis.map((axis, index) => {
        return newSeries[index] = data.map((row, index) => {
          return {
            x: row[x_axis['field']],
            y: row[axis['field']],
          }
        })
      })

      while (dataPoints[0].length) {
        y_axis.map((item, index) => {
          dataPoints[index].pop();
        })
      }
      console.log('fetchGraphData', dataPoints);
      y_axis.map((item, index) => {
        dataPoints[index].push(...newSeries[index]);
        this.chart.options.data[index].legendText = item['name'] + newSeries[index].pop().y;
      })
      this.chart.render();
      refresh_button && !refresh_sec && toastr.success(`Success!`);
    } catch (error) {
      refresh_button && !refresh_sec && toastr.error(`Fetch Error: ${error.message}`);
    }
  }


  render() {



    const colorSet = []
    const { kwargs } = this.props.args;
    const { y_axis, api, y_max, refresh_sec, theme_options, refresh_button } = kwargs;
    const dataY = y_axis.map((item, index) => {
      colorSet.push(item['color']);
      return {
        type: "spline",
        xValueFormatString: "#.##0 ",
        yValueFormatString: "#.##0",
        showInLegend: true,
        name: item['name'],
        dataPoints: dataPoints[index],
        // lineColor: item['color'] ? item['color'] : ''
      }
    })
    CanvasJS.addColorSet("greenShades", colorSet);
    const options = {
      colorSet: 'greenShades',
      backgroundColor: theme_options['backgroundColor'] ? theme_options['backgroundColor'] : 'white',
      zoomEnabled: true,
      title: {
        text: theme_options['main_title'] ? theme_options['main_title'] : ''
      },
      axisX: {
        title: theme_options['x_axis_title'] ? theme_options['x_axis_title'] : '',
        labelFormatter: (e) => e.value
      },
      axisY: {
        suffix: "",
        maximum: y_max ? y_max : null,
        gridColor: theme_options['grid_color'] ? theme_options['grid_color'] : '',
      },
      toolTip: {
        shared: true
      },
      legend: {
        cursor: "pointer",
        verticalAlign: "top",
        fontSize: 18,
        fontColor: "dimGrey",
        itemclick: this.toggleDataSeries
      },
      data: dataY,
      height:kwargs.graph_height?kwargs.graph_height:400
    }
    return (
      <div>
        {
          (refresh_button) && !refresh_sec &&
          <div style={{ display: 'flex' }}>
            <div style={{ margin: "10px 10px 10px 2px" }}>
              <button className='btn btn-warning' onClick={this.updateChart}>Refresh</button>
            </div>
          </div>
        }
        <CanvasJSChart
          options={options}
          onRef={ref => this.chart = ref}
        />
      </div>
    );
  }
}

export default withStreamlitConnection(App);

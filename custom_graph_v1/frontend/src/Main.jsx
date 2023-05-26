import React, { Component } from 'react';
import CanvasJSReact from '@canvasjs/react-charts';

import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib";

import axios from 'axios';
//var CanvasJSReact = require('@canvasjs/react-charts');

var CanvasJS = CanvasJSReact.CanvasJS;
var CanvasJSChart = CanvasJSReact.CanvasJSChart;
var dataPoints1 = [];
var dataPoints2 = [];
var updateInterval = 2000;
//initial values
var yValue1 = 408;
var yValue2 = 350;
var xValue = 5;
class App extends Component {

  constructor(props) {
    super(props);
    this.updateChart = this.updateChart.bind(this);
    this.toggleDataSeries = this.toggleDataSeries.bind(this);
  }
  componentDidMount() {
    const { kwargs } = this.props.args;
    const { y_axis, api, y_max, refresh_sec } = kwargs;
    Streamlit.setFrameHeight();
    this.updateChart(20);
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
    const res = await axios.post(api, {
      ...kwargs
    });
    return JSON.parse(res.data);
  }
  async updateChart(count) {
    const { kwargs } = this.props.args;
    const { y_axis, api, y_max, refresh_sec } = kwargs;
    const data = await this.fetchGraphData();
    const newSeriesOne = data.map((item, index) => {
      return {
        x: item.est_timestamp,
        y: item.close,
      }
    })
    const newSeriesTwo = data.map((item, index) => {
      return {
        x: item.est_timestamp,
        y: item.vwap,
      }
    })
    // dataPoints1 =newSeriesOne;
    // dataPoints2= newSeriesOne;
    // count = count || 1;
    // var deltaY1, deltaY2;
    // for (var i = 0; i < count; i++) {
    //   xValue += 2;
    //   deltaY1 = 5 + Math.random() * (-5 - 5);
    //   deltaY2 = 5 + Math.random() * (-5 - 5);
    //   yValue1 = Math.floor(Math.random() * (408 - 400 + 1) + 400);
    //   yValue2 = Math.floor(Math.random() * (350 - 340 + 1) + 340);
    //   console.log('datapoints pushing');
    //   dataPoints1.push({
    //     x: xValue,
    //     y: yValue1
    //   });
    //   dataPoints2.push({
    //     x: xValue,
    //     y: yValue2
    //   });
    // }
    // dataPoints1=[]
    while (dataPoints1.length) {
      dataPoints1.pop()
      dataPoints2.pop()
    }
    dataPoints1.push(...newSeriesOne);
    dataPoints2.push(...newSeriesTwo);
    // dataPoints1.splice(0,10)
    // dataPoints1=newSeriesOne
    console.log('fetchGraphData', dataPoints1, newSeriesOne);
    this.chart.options.data[0].legendText = "close -  " + newSeriesOne.pop().y + "";
    this.chart.options.data[1].legendText = "vwap - " + newSeriesOne.pop().y + "";
    this.chart.render();
  }
  render() {
    const { kwargs } = this.props.args;
    const { y_axis, api, y_max, refresh_sec } = kwargs;
    const options = {
      zoomEnabled: true,
      theme: "light1",
      title: {
        text: "Close/Vwap"
      },
      axisX: {
        title: "chart updates every 2 secs"
      },
      axisY: {
        suffix: "",
        maximum: y_max,
        // interval:1,
        gridColor: 'white',
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
      data: [
        {
          type: "spline",
          xValueFormatString: "#,##0 ",
          yValueFormatString: "#,##0",
          showInLegend: true,
          name: "close:",
          dataPoints: dataPoints1
        },
        {
          type: "spline",
          xValueFormatString: "#,##0 seconds",
          yValueFormatString: "#,##0",
          showInLegend: true,
          name: "vwap:",
          dataPoints: dataPoints2
        }
      ]
    }
    return (
      <div>
        <CanvasJSChart options={options}
          onRef={ref => this.chart = ref}
        />
        {/*You can get reference to the chart instance as shown above using onRef. This allows you to access all chart properties and methods*/}
      </div>
    );
  }
}

export default withStreamlitConnection(App);

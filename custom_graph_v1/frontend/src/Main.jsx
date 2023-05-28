import React, { Component } from 'react';
import CanvasJSReact from '@canvasjs/react-charts';

import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib";

import axios from 'axios';

var CanvasJSChart = CanvasJSReact.CanvasJSChart;
const dataPoints = [[], [], [], [], [], [], [], [], [], []];

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
    this.updateChart();
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
    const { x_axis, y_axis, api, y_max, refresh_sec } = kwargs;
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
  }

  render() {
    const { kwargs } = this.props.args;
    const { y_axis, api, y_max, refresh_sec } = kwargs;
    const dataY = y_axis.map((item, index) => {
      return {
        type: "spline",
        xValueFormatString: "#.##0 ",
        yValueFormatString: "#.##0",
        showInLegend: true,
        name: item['name'],
        dataPoints: dataPoints[index],
      }
    })
    const options = {
      zoomEnabled: true,
      theme: "light1",
      title: {
        text: "Title is required?"
      },
      axisX: {
        title: "THIS IS A-AXIS TITLE",
        labelFormatter: (e) => e.value
      },
      axisY: {
        suffix: "",
        maximum: y_max ? y_max : null,
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
      data: dataY
    }
    return (
      <div>
        <CanvasJSChart
          options={options}
          onRef={ref => this.chart = ref}
        />
      </div >
    );
  }
}

export default withStreamlitConnection(App);

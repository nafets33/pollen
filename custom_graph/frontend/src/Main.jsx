import React, { useEffect, useState } from "react";
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib";
import ReactApexCharts from 'react-apexcharts'
import ApexCharts from 'apexcharts'
import axios from "axios";

var _seed = 42;
Math.random = function () {
  _seed = _seed * 16807 % 2147483647;
  return (_seed - 1) / 2147483646;
};

var lastDate = 0;
var data = [];
var TICKINTERVAL = 86400000
let XAXISRANGE = 777600000
function getDayWiseTimeSeries(baseval, count, yrange) {
  var i = 0;
  while (i < count) {
    var x = baseval;
    var y = Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min;

    data.push({
      x, y
    });
    lastDate = baseval
    baseval += TICKINTERVAL;
    i++;
  }
}

getDayWiseTimeSeries(new Date('11 Feb 2017 GMT').getTime(), 10, {
  min: 10,
  max: 90
})

function getNewSeries(baseval, yrange) {
  var newDate = baseval + TICKINTERVAL;
  lastDate = newDate

  for (var i = 0; i < data.length - 10; i++) {
    // IMPORTANT
    // we reset the x and y of the data which is out of drawing area
    // to prevent memory leaks
    data[i].x = newDate - XAXISRANGE - TICKINTERVAL
    data[i].y = 0
  }

  data.push({
    x: newDate,
    y: Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min
  })
  // console.log('getNewSeries', data);
}



const Main = (props) => {

  const { kwargs } = props.args;
  const [series, setSeries] = useState([]);
  const [options, setOptions] = useState({});


  useEffect(() => Streamlit.setFrameHeight())
  const getGraphData = async () => {
      console.log("SSSSSSSSSSSSS", kwargs);
      const res = await axios.post("http://localhost:8000/api/data/symbol_graph", {
      ...kwargs
    });
    return JSON.parse(res.data);
    console.log("postres", res.data);
  }
  useEffect(() => {
    const interval = setInterval(async () => {
      const dfData = await getGraphData();
      const serie1 = dfData.map((row) => row.close);
      const serie2 = dfData.map((row) => row.vwap);
      ApexCharts.exec('realtime', 'updateSeries', [{
        name: "Session Duration",
        data: serie1
      },
      {
        name: "Page Views",
        data: serie2
      },
      ])
    }, 1000);
    const onLoad = async () => {
      const dfData = await getGraphData();
      const categories = dfData.map((row) => (row.timestamp_est));
      const serie1 = dfData.map((row) => row.close);
      const serie2 = dfData.map((row) => row.vwap);
      const new_serires = [{
        name: "close",
        data: serie1
      }, {
        name: "vwap",
        data: serie2
      },]
      const new_option = {
        series: [{
          name: "Session Duration",
          data: serie1
        },
        {
          name: "Page Views",
          data: serie2
        },
        ],
        chart: {
          height: 350,
          type: 'line',
          zoom: {
            enabled: false
          },
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          width: [5, 7, 5],
          curve: 'straight',
          dashArray: [0, 8, 5]
        },
        title: {
          text: 'Page Statistics',
          align: 'left'
        },
        legend: {
          tooltipHoverFormatter: function (val, opts) {
            return val + ' - ' + opts.w.globals.series[opts.seriesIndex][opts.dataPointIndex] + ''
          }
        },
        markers: {
          size: 0,
          hover: {
            sizeOffset: 6
          }
        },
        xaxis: {
          type: 'datetime',
          categories: categories
        },
        tooltip: {
          // y: [
          //   {
          //     title: {
          //       formatter: function (val) {
          //         return val + " (mins)"
          //       }
          //     }
          //   },
          //   {
          //     title: {
          //       formatter: function (val) {
          //         return val + " per session"
          //       }
          //     }
          //   },
          //   {
          //     title: {
          //       formatter: function (val) {
          //         return val;
          //       }
          //     }
          //   }
          // ]
        },
        grid: {
          borderColor: '#f1f1f1',
        }
      };
      console.log("onload", new_option);
      setOptions(new_option);
      setSeries(new_serires)
    }
    onLoad()
    return () => {
      clearInterval(interval);
    }
  }, [])

  return (
    <div>
      <div id="chart">
        <ReactApexCharts options={options} series={series} type="line" height={350} />
      </div>
      <div id="html-dist"></div>
    </div>
  )
};

export default withStreamlitConnection(Main);

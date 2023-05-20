import React, { useEffect, useState } from "react";
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib";
import ReactApexCharts from 'react-apexcharts'
import ApexCharts from 'apexcharts'
import axios from "axios";
import moment from 'moment';

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


const Main = (props) => {

  const { kwargs } = props.args;
  const { y_axis } = kwargs;
  const [series, setSeries] = useState([]);
  const [options, setOptions] = useState({});


  useEffect(() => Streamlit.setFrameHeight())
  const getGraphData = async () => {
    // console.log("SSSSSSSSSSSSS", kwargs);
    const res = await axios.post("http://localhost:8000/api/data/symbol_graph", {
      ...kwargs
    });
    return JSON.parse(res.data);
    console.log("postres", res.data);
  }
  useEffect(() => {
    const interval = setInterval(async () => {
      const dfData = await getGraphData();
      const categories = dfData.map((row) => (row.timestamp_est / 1000));
      // const categories = dfData.map((row) =>(row.timestamp_est.toString()));
      const serie1 = dfData.map((row) => row.close);
      const serie2 = dfData.map((row) => row.vwap);
      const new_serires = y_axis.map((line) => {
        return {
          name: line.name,
          data: dfData.map((row) => row[line['field']]).slice(0),
        }
      })
      console.log('SSSSSSSSSSSS', serie1.slice(-1));
      setSeries(new_serires)

      ApexCharts.exec('realtime', 'updateSeries', new_serires)
    }, 1000);

    const onLoad = async () => {
      const dfData = await getGraphData();
      const categories = dfData.map((row) => (row.timestamp_est / 1000));
      // const categories = dfData.map((row) =>(row.timestamp_est.toString()));
      const serie1 = dfData.map((row) => row.close);
      const serie2 = dfData.map((row) => row.vwap);
      const new_serires = y_axis.map((line) => {
        return {
          name: line.name,
          data: dfData.map((row) => row[line['field']]).slice(0),
        }
      })
      const colors = y_axis.map((line) => line['color'])
      const new_option = {
        series: new_serires,
        chart: {
          id: 'realtime',
          height: 350,
          type: 'line',
          zoom: {
            enabled: true
          },
          animations: {
            enabled: true,
            easing: 'linear',
            dynamicAnimation: {
              speed: 1000
            }
          },
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          width: [3, 3, 3],
          curve: 'smooth',
          dashArray: [0, 0, 0]
        },
        title: {
          text: '',
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
          type: 'category',
          categories: categories,
          labels: {
            rotate: 0,
            formatter: function (val) {
              return moment.unix(val).format(' hh:mm');
            },
            style: {
              cssClass: 'xaxis-label',
              // fontSize: '22px',
            }
          },
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
    // const interval = setInterval(() => {
    // onLoad()
    // }, 1000);
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
